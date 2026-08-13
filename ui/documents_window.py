import os
import sys
import tempfile
import subprocess
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QListWidget,
    QPushButton,
    QMessageBox
)
from PySide6.QtGui import (
    QIcon,
    QDesktopServices
)
from PySide6.QtCore import QUrl, Qt
from database import DatabaseManager


class DocumentsWindow(QDialog):

    def __init__(self, customer_id, parent=None):

        super().__init__(parent)

        self.customer_id = customer_id

        self.db = DatabaseManager()

        # فایل‌های موقتی که در این پنجره ساخته می‌شوند
        self.temp_files = []

        self.setWindowTitle("مدارک مسافر")

        self.setWindowIcon(
            QIcon(
                "assets/icons/logo.ico"
            )
        )

        self.resize(
            700,
            500
        )

        layout = QVBoxLayout(self)

        # ---------------------------------------------
        # لیست مدارک
        # ---------------------------------------------

        self.list_widget = QListWidget()

        layout.addWidget(
            self.list_widget
        )

        # ---------------------------------------------
        # دکمه بستن
        # ---------------------------------------------

        self.close_btn = QPushButton(
            "بستن"
        )

        layout.addWidget(
            self.close_btn
        )

        self.close_btn.clicked.connect(
            self.accept
        )

        # ---------------------------------------------
        # باز کردن مدرک
        # ---------------------------------------------

        self.list_widget.itemDoubleClicked.connect(
            self.open_selected_file
        )

        self.load_files()

    # =================================================
    # دریافت مدارک
    # =================================================

    def load_files(self):

        self.list_widget.clear()

        files = self.db.get_customer_files_data(
            self.customer_id
        )

        for file in files:

            file_name = file["file_name"]

            if not file_name:
                file_name = "مدرک بدون نام"

            item = self.list_widget.addItem(
                file_name
            )

            # -----------------------------------------
            # ذخیره اطلاعات فایل داخل آیتم
            # -----------------------------------------

            item = self.list_widget.item(
                self.list_widget.count() - 1
            )

            item.setData(
                Qt.UserRole,
                file["id"]
            )

    # =================================================
    # باز کردن مدرک انتخاب‌شده
    # =================================================

    def open_selected_file(self, item):

        file_id = item.data(
            Qt.UserRole
        )

        if not file_id:

            QMessageBox.warning(
                self,
                "خطا",
                "اطلاعات مدرک پیدا نشد."
            )

            return

        # ---------------------------------------------
        # دریافت فایل از SQLite
        # ---------------------------------------------

        conn = self.db.connect()

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                file_name,
                file_data
            FROM customer_files
            WHERE id=?
            """,
            (file_id,)
        )

        row = cursor.fetchone()

        conn.close()

        if row is None:

            QMessageBox.warning(
                self,
                "خطا",
                "مدرک پیدا نشد."
            )

            return

        file_name = row["file_name"]
        file_data = row["file_data"]

        # ---------------------------------------------
        # بررسی اطلاعات فایل
        # ---------------------------------------------

        if not file_data:

            QMessageBox.warning(
                self,
                "خطا",
                "اطلاعات فایل داخل برنامه وجود ندارد."
            )

            return

        # ---------------------------------------------
        # ساخت فایل موقت
        # ---------------------------------------------

        try:

            suffix = ""

            if file_name:

                _, extension = os.path.splitext(
                    file_name
                )

                suffix = extension

            temp_file = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=suffix
            )

            temp_file.write(
                bytes(file_data)
            )

            temp_file.close()

            self.temp_files.append(
                temp_file.name
            )

            # -----------------------------------------
            # باز کردن فایل با برنامه پیش‌فرض ویندوز
            # -----------------------------------------

            QDesktopServices.openUrl(
                QUrl.fromLocalFile(
                    temp_file.name
                )
            )

        except Exception as e:

            QMessageBox.critical(
                self,
                "خطا",
                f"باز کردن مدرک انجام نشد.\n\n{e}"
            )

    # =================================================
    # پاک‌سازی فایل‌های موقت
    # =================================================

    def closeEvent(self, event):

        for file_path in self.temp_files:

            try:

                if os.path.exists(
                    file_path
                ):

                    os.remove(
                        file_path
                    )

            except Exception:
                pass

        self.temp_files.clear()

        super().closeEvent(
            event
        )

    def migrate_old_customer_files(self):

        conn = self.connect()
        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                SELECT
                    id,
                    file_path
                FROM customer_files
                WHERE
                    (file_data IS NULL OR length(file_data) = 0)
                    AND file_path IS NOT NULL
                    AND file_path != ''
                """
            )

            rows = cursor.fetchall()

            migrated_count = 0

            for row in rows:

                file_id = row["id"]
                old_path = row["file_path"]

                if not old_path:
                    continue

                source_path = Path(old_path)

                # ---------------------------------------------
                # اگر مسیر قدیمی نسبی باشد
                # ---------------------------------------------

                if not source_path.is_absolute():
                    source_path = (
                            self.data_path / source_path
                    )

                # ---------------------------------------------
                # بررسی وجود فایل
                # ---------------------------------------------

                if not source_path.exists():
                    continue

                if not source_path.is_file():
                    continue

                # ---------------------------------------------
                # خواندن فایل
                # ---------------------------------------------

                with open(
                        source_path,
                        "rb"
                ) as file:

                    file_data = file.read()

                # ---------------------------------------------
                # نام فایل
                # ---------------------------------------------

                file_name = source_path.name

                # ---------------------------------------------
                # انتقال به SQLite
                # ---------------------------------------------

                cursor.execute(
                    """
                    UPDATE customer_files

                    SET
                        file_name = ?,
                        file_data = ?

                    WHERE id = ?
                    """,
                    (
                        file_name,
                        sqlite3.Binary(
                            file_data
                        ),
                        file_id
                    )
                )

                migrated_count += 1

            conn.commit()

            return migrated_count

        except Exception:

            conn.rollback()

            raise

        finally:

            conn.close()