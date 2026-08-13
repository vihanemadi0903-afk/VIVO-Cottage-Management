from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from core.backup_manager import BackupManager
from datetime import datetime
import json
from pathlib import Path
from core.settings_manager import SettingsManager
from PySide6.QtWidgets import QFileDialog
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QGroupBox,
    QHBoxLayout
)


class SettingsDialog(QDialog):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("تنظیمات")

        self.setMinimumSize(650, 450)

        self.build_ui()

        # ---------- مدیر تنظیمات ----------
        self.settings = SettingsManager()

        # ---------- مدیر بکاپ ----------
        self.backup = BackupManager()

        # ---------- نمایش مسیر بکاپ ----------
        self.folder_label.setText(
            self.settings.get_backup_folder()
        )

        # ---------- اتصال دکمه‌ها ----------
        self.backup_button.clicked.connect(
            self.create_backup
        )

        self.add_backup_button.clicked.connect(
            self.add_backup
        )

        self.change_folder_button.clicked.connect(
            self.change_backup_folder
        )

        # ---------- نمایش آخرین بکاپ ----------
        self.update_last_backup()

        self.update_database_info()

    def build_ui(self):

        main_layout = QVBoxLayout(self)

        # ---------- عنوان ----------

        title = QLabel("⚙ تنظیمات برنامه")

        title.setAlignment(Qt.AlignCenter)

        title.setFont(QFont("Tahoma", 15, QFont.Bold))

        main_layout.addWidget(title)

        # ---------- بکاپ ----------

        backup_group = QGroupBox("💾 بکاپ اطلاعات")

        backup_layout = QVBoxLayout()

        self.backup_button = QPushButton("ایجاد بکاپ")

        self.add_backup_button = QPushButton("📥 افزودن بک آپ")

        self.last_backup_label = QLabel("آخرین بکاپ: ---")

        backup_layout.addWidget(
            self.backup_button
        )

        backup_layout.addWidget(
            self.add_backup_button
        )

        backup_layout.addWidget(
            self.last_backup_label
        )

        backup_group.setLayout(backup_layout)

        main_layout.addWidget(backup_group)

        # ---------- پوشه بکاپ ----------

        folder_group = QGroupBox("📂 محل ذخیره بکاپ")

        folder_layout = QVBoxLayout()

        self.folder_label = QLabel("backups")

        self.change_folder_button = QPushButton("تغییر پوشه")

        folder_layout.addWidget(self.folder_label)

        folder_layout.addWidget(self.change_folder_button)

        folder_group.setLayout(folder_layout)

        main_layout.addWidget(folder_group)

        # ---------- اطلاعات ----------

        info_group = QGroupBox("ℹ اطلاعات برنامه")

        info_layout = QVBoxLayout()

        self.version_label = QLabel("نسخه: VIVO 4.0.1")

        self.database_label = QLabel("دیتابیس: SQLite")

        self.customers_label = QLabel("تعداد مسافران: ---")

        self.size_label = QLabel("حجم دیتابیس: ---")

        info_layout.addWidget(self.version_label)

        info_layout.addWidget(self.database_label)

        info_layout.addWidget(self.customers_label)

        info_layout.addWidget(self.size_label)

        info_group.setLayout(info_layout)

        main_layout.addWidget(info_group)

        main_layout.addStretch()

        # ---------- بستن ----------

        buttons = QHBoxLayout()

        buttons.addStretch()

        close_button = QPushButton("بستن")

        close_button.clicked.connect(self.close)

        buttons.addWidget(close_button)

        main_layout.addLayout(buttons)

    def create_backup(self):

        from PySide6.QtWidgets import QMessageBox

        try:

            self.backup.create_backup()

            self.folder_label.setText(
                self.settings.get_backup_folder()
            )

            self.update_last_backup()

            self.update_last_backup()

            QMessageBox.information(

                self,

                "موفق",

                "بکاپ با موفقیت ایجاد شد."

            )

        except Exception as e:

            QMessageBox.critical(

                self,

                "خطا",

                str(e)

            )

    def update_last_backup(self):

        backup_folder = Path(
            self.settings.get_backup_folder()
        )

        json_file = backup_folder / "last_backup.json"

        if not json_file.exists():
            self.last_backup_label.setText(
                "آخرین بکاپ: ---"
            )

            return

        try:

            with open(
                    json_file,
                    "r",
                    encoding="utf-8"
            ) as f:

                info = json.load(f)

            db_file = backup_folder / info["file"]

            if db_file.exists():

                size = db_file.stat().st_size / 1024

                self.last_backup_label.setText(

                    f"""آخرین بکاپ:

    تاریخ: {info["date"]}

    ساعت: {info["time"]}

    حجم: {size:.1f} KB"""

                )

            else:

                self.last_backup_label.setText(
                    "آخرین بکاپ: ---"
                )

        except Exception:

            self.last_backup_label.setText(
                "آخرین بکاپ: ---"
            )

    def change_backup_folder(self):

        folder = QFileDialog.getExistingDirectory(

            self,

            "انتخاب پوشه ذخیره بکاپ"

        )

        if not folder:
            return

        from pathlib import Path

        folder = Path(folder) / "VIVO"

        folder.mkdir(

            parents=True,

            exist_ok=True

        )

        self.settings.set_backup_folder(

            str(folder)

        )

        self.folder_label.setText(

            str(folder)

        )

        # BackupManager مسیر جدید را بشناسد

        self.backup.settings = self.settings

        self.backup.backup_folder = folder

    from pathlib import Path

    def update_database_info(self):

        from database import DatabaseManager

        db = DatabaseManager()

        conn = db.connect()

        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM customers")

        count = cursor.fetchone()[0]

        conn.close()

        self.customers_label.setText(
            f"تعداد مسافران: {count}"
        )

        size = db.db_path.stat().st_size / 1024

        if size < 1024:

            text = f"{size:.1f} KB"

        else:

            text = f"{size / 1024:.2f} MB"

        self.size_label.setText(
            f"حجم دیتابیس: {text}"
        )


    def add_backup(self):

        from PySide6.QtWidgets import QMessageBox

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "انتخاب فایل بک آپ",
            "",
            "VIVO Database (*.db)"
        )

        if not file_path:
            return

        reply = QMessageBox.question(
            self,
            "افزودن بک آپ",
            (
                "اطلاعات موجود در فایل بک آپ "
                "به اطلاعات فعلی برنامه اضافه می‌شوند.\n\n"
                "هیچ‌کدام از اطلاعات فعلی حذف نخواهند شد.\n\n"
                "آیا ادامه می‌دهید؟"
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        try:

            from database import DatabaseManager

            db = DatabaseManager()

            result = db.merge_backup(
                file_path
            )

            # ---------------------------------------------
            # به‌روزرسانی اطلاعات صفحه تنظیمات
            # ---------------------------------------------

            self.update_database_info()

            # ---------------------------------------------
            # به‌روزرسانی فوری پنجره اصلی
            # ---------------------------------------------

            main_window = self.parent()

            if main_window is not None:

                if hasattr(
                        main_window,
                        "load_customers"
                ):
                    main_window.load_customers()

                elif hasattr(
                        main_window,
                        "refresh_data"
                ):
                    main_window.refresh_data()

                elif hasattr(
                        main_window,
                        "load_data"
                ):
                    main_window.load_data()

            QMessageBox.information(
                self,
                "موفق",
                (
                    f"تعداد {result['customers']} "
                    f"مسافر به برنامه اضافه شد.\n\n"
                    f"تعداد {result['files']} "
                    f"مدرک نیز منتقل شد.\n\n"
                    "اطلاعات فعلی برنامه حفظ شدند."
                )
            )

        except Exception as e:

            QMessageBox.critical(
                self,
                "خطا در افزودن بک آپ",
                (
                    "افزودن بک آپ انجام نشد.\n\n"
                    f"جزئیات خطا:\n{e}"
                )
            )
