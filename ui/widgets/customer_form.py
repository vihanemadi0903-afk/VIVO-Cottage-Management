from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QTextEdit,
    QComboBox,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QGridLayout,
    QHBoxLayout,
    QVBoxLayout,
    QFileDialog,
    QGroupBox,
    QFrame,
    QMessageBox
)
import os
import jdatetime
from ui.dialogs.calendar_dialog import CalendarDialog
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import QRegularExpression
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from ui.cottage_selection_dialog import CottageSelectionDialog
from PySide6.QtCore import QPropertyAnimation, QEasingCurve
from PySide6.QtCore import QPoint
import tempfile
from pathlib import Path
from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices


class CustomerForm(QWidget):

    def __init__(self):
        super().__init__()

        self.customer_id = None

        self.selected_files = []

        self.existing_files = []

        self.deleted_file_ids = []

        self.files_changed = False

        self.edit_mode = False

        self.build_ui()

        self.set_initial_state()

    def build_ui(self):

        main_layout = QVBoxLayout(self)

        grid = QGridLayout()

        grid.setHorizontalSpacing(15)
        grid.setVerticalSpacing(12)

        # =====================================================
        # ردیف اول
        # =====================================================

        # ---------- نام ----------

        self.lbl_name = QLabel("نام و نام خانوادگی")

        self.name_edit = QLineEdit()

        self.name_edit.setPlaceholderText(
            "مثلاً: علی محمدی"
        )

        # ---------- شماره تماس ----------

        self.lbl_phone = QLabel("شماره تماس")

        self.phone_edit = QLineEdit()

        self.phone_edit.setPlaceholderText(
            "09xxxxxxxxx"
        )

        self.phone_edit.setMaxLength(11)

        phone_validator = QRegularExpressionValidator(
            QRegularExpression(r"^09\d{0,9}$")
        )

        self.phone_edit.setValidator(
            phone_validator
        )

        # ---------- کلبه ----------

        lbl_cottage = QLabel("شماره کلبه")

        self.cottage_button = QPushButton(
            "انتخاب کلبه"
        )

        self.cottage_button.setFixedHeight(38)

        self.cottage_button.clicked.connect(
            self.open_cottage_selection
        )

        # ---------- چینش ----------

        grid.addWidget(self.lbl_name, 0, 2)
        grid.addWidget(self.name_edit, 1, 2)

        grid.addWidget(self.lbl_phone, 0, 1)
        grid.addWidget(self.phone_edit, 1, 1)

        grid.addWidget(lbl_cottage, 0, 0)
        grid.addWidget(self.cottage_button, 1, 0)

        # =====================================================
        # ردیف دوم
        # =====================================================

        # ---------- تاریخ ورود ----------

        lbl_in = QLabel("تاریخ ورود")

        self.entry_button = QPushButton(
            "انتخاب تاریخ ورود"
        )

        self.entry_button.setFixedHeight(38)

        self.entry_button.clicked.connect(
            self.select_entry_date
        )

        # ---------- تاریخ خروج ----------

        lbl_out = QLabel("تاریخ خروج")

        self.exit_button = QPushButton(
            "انتخاب تاریخ خروج"
        )

        self.exit_button.setFixedHeight(38)

        self.exit_button.clicked.connect(
            self.select_exit_date
        )

        grid.addWidget(lbl_in, 2, 2)
        grid.addWidget(
            self.entry_button,
            3,
            2
        )

        grid.addWidget(lbl_out, 2, 1)
        grid.addWidget(
            self.exit_button,
            3,
            1
        )

        # =====================================================
        # ردیف سوم
        # =====================================================

        # ---------- توضیحات ----------

        self.lbl_desc = QLabel("توضیحات")

        self.desc_edit = QTextEdit()

        self.desc_edit.setFixedWidth(300)
        self.desc_edit.setFixedHeight(140)

        grid.addWidget(
            self.lbl_desc,
            4,
            2,
            alignment=Qt.AlignTop
        )

        grid.addWidget(
            self.desc_edit,
            5,
            2,
            alignment=Qt.AlignTop
        )

        # ---------- مدارک ----------

        self.lbl_files = QLabel(
            "مدارک و تصاویر"
        )

        self.files_list = QListWidget()

        self.files_list.setFixedWidth(260)
        self.files_list.setFixedHeight(140)

        grid.addWidget(
            self.lbl_files,
            4,
            1,
            alignment=Qt.AlignTop
        )

        grid.addWidget(
            self.files_list,
            5,
            1,
            alignment=Qt.AlignTop
        )

        # ---------- دکمه‌های مدارک ----------

        buttons_layout = QVBoxLayout()

        self.add_file_btn = QPushButton(
            "➕ افزودن"
        )

        self.remove_file_btn = QPushButton(
            "🗑 حذف"
        )

        buttons_layout.addWidget(
            self.add_file_btn
        )

        buttons_layout.addWidget(
            self.remove_file_btn
        )

        buttons_layout.addStretch()

        grid.addLayout(
            buttons_layout,
            5,
            0
        )

        # ---------- اندازه ستون‌ها ----------

        grid.setColumnStretch(2, 3)
        grid.setColumnStretch(1, 2)
        grid.setColumnStretch(0, 0)

        main_layout.addLayout(grid)

        # =====================================================
        # اطلاعات پرداخت
        # =====================================================

        self.payment_group = QGroupBox(
            "اطلاعات پرداخت"
        )

        payment_layout = QGridLayout()

        payment_layout.setHorizontalSpacing(12)
        payment_layout.setVerticalSpacing(10)

        # ---------- پز دفتر ----------

        lbl_pos_office = QLabel("پز دفتر")

        self.pos_office_edit = QLineEdit()

        payment_layout.addWidget(
            lbl_pos_office,
            0,
            1
        )

        payment_layout.addWidget(
            self.pos_office_edit,
            0,
            0
        )

        # ---------- پز کافه ----------

        lbl_pos_cafe = QLabel("پز کافه")

        self.pos_cafe_edit = QLineEdit()

        payment_layout.addWidget(
            lbl_pos_cafe,
            1,
            1
        )

        payment_layout.addWidget(
            self.pos_cafe_edit,
            1,
            0
        )

        # ---------- پز سوپرمارکت ----------

        lbl_pos_market = QLabel(
            "پز سوپرمارکت"
        )

        self.pos_market_edit = QLineEdit()

        payment_layout.addWidget(
            lbl_pos_market,
            2,
            1
        )

        payment_layout.addWidget(
            self.pos_market_edit,
            2,
            0
        )

        # ---------- نقدی ----------

        lbl_cash = QLabel("نقدی")

        self.cash_edit = QLineEdit()

        payment_layout.addWidget(
            lbl_cash,
            3,
            1
        )

        payment_layout.addWidget(
            self.cash_edit,
            3,
            0
        )

        # ---------- کارت به کارت ----------

        lbl_card = QLabel("کارت به کارت")

        self.card_edit = QLineEdit()

        payment_layout.addWidget(
            lbl_card,
            4,
            1
        )

        payment_layout.addWidget(
            self.card_edit,
            4,
            0
        )

        # ---------- گیرنده ----------

        lbl_receiver = QLabel("گیرنده")

        self.receiver_edit = QLineEdit()

        # ---------- نسیه ----------

        lbl_credit = QLabel("نسیه")

        self.credit_edit = QLineEdit()

        payment_layout.addWidget(
            lbl_credit,
            6,
            1
        )

        payment_layout.addWidget(
            self.credit_edit,
            6,
            0
        )


        payment_fields = [
            self.pos_office_edit,
            self.pos_cafe_edit,
            self.pos_market_edit,
            self.cash_edit,
            self.card_edit,
            self.credit_edit
        ]

        for field in payment_fields:
            field.textChanged.connect(
                self.on_payment_changed
            )

        payment_layout.addWidget(
            lbl_receiver,
            5,
            1
        )

        payment_layout.addWidget(
            self.receiver_edit,
            5,
            0
        )
        # ---------- خط جداکننده ----------

        line = QFrame()

        line.setFrameShape(
            QFrame.HLine
        )

        payment_layout.addWidget(
            line,
            7,
            0,
            1,
            2
        )

        # ---------- جمع پرداخت ----------

        lbl_total = QLabel(
            "جمع پرداختی"
        )

        lbl_total.setStyleSheet("""
            font-weight:bold;
            font-size:13px;
        """)

        self.total_label = QLabel(
            "0 تومان"
        )

        self.total_label.setStyleSheet("""
            font-weight:bold;
            font-size:15px;
            color:#2E7D32;
        """)

        payment_layout.addWidget(
            lbl_total,
            8,
            1
        )

        payment_layout.addWidget(
            self.total_label,
            8,
            0
        )

        self.payment_group.setLayout(
            payment_layout
        )

        main_layout.addWidget(
            self.payment_group
        )

        # =====================================================
        # اتصال دکمه‌های مدارک
        # =====================================================

        self.add_file_btn.clicked.connect(
            self.add_files
        )

        self.remove_file_btn.clicked.connect(
            self.remove_file
        )

        self.files_list.itemDoubleClicked.connect(
            self.open_file
        )

    # --------------------------------------------

    def add_files(self):

        files, _ = QFileDialog.getOpenFileNames(
            self,
            "انتخاب مدارک"
        )

        if not files:
            return

        for file_path in files:

            if file_path in self.selected_files:
                continue

            self.selected_files.append(
                file_path
            )

            item = QListWidgetItem(
                os.path.basename(file_path)
            )

            item.setData(
                Qt.UserRole,
                {
                    "type": "new",
                    "path": file_path
                }
            )

            self.files_list.addItem(
                item
            )

        self.files_changed = True
    # --------------------------------------------

    def remove_file(self):

        row = self.files_list.currentRow()

        if row < 0:
            return

        item = self.files_list.item(row)

        if item is None:
            return

        file_info = item.data(Qt.UserRole)

        if not file_info:
            return

        # -------------------------------
        # مدرک جدید
        # -------------------------------

        if file_info.get("type") == "new":

            file_path = file_info.get("path")

            if file_path in self.selected_files:
                self.selected_files.remove(file_path)

            self.files_list.takeItem(row)

            self.files_changed = True

            return

        # -------------------------------
        # مدرک قبلی دیتابیس
        # -------------------------------

        if file_info.get("type") == "existing":

            file_id = file_info.get("id")

            if file_id is not None:

                if file_id not in self.deleted_file_ids:
                    self.deleted_file_ids.append(file_id)

            self.files_list.takeItem(row)

            self.files_changed = True
    # --------------------------------------------

    def get_data(self):

        return {

            "name":
                self.name_edit.text(),

            "phone":
                self.phone_edit.text(),

            "cottage":
                self.selected_cottage,

            "entry":
                self.entry_button.text(),

            "exit":
                self.exit_button.text(),

            "description":
                self.desc_edit.toPlainText(),

            # فقط فایل‌های جدید
            "files":
                self.selected_files.copy(),

            "files_changed":
                self.files_changed,

            # شناسه مدارک قبلی که حذف شده‌اند
            "deleted_file_ids":
                self.deleted_file_ids.copy(),

            # -------------------------
            # پرداخت
            # -------------------------

            "pos_office":
                self.pos_office_edit.text(),

            "pos_cafe":
                self.pos_cafe_edit.text(),

            "pos_market":
                self.pos_market_edit.text(),

            "cash":
                self.cash_edit.text(),

            "card_transfer":
                self.card_edit.text(),

            "card_transfer_receiver":
                self.receiver_edit.text(),

            "credit":
                self.credit_edit.text()
        }
    # --------------------------------------------

    def clear(self):

        self.name_edit.clear()

        self.phone_edit.clear()

        self.selected_cottage = None

        self.cottage_button.setText(
            "انتخاب کلبه"
        )

        self.entry_button.clear()

        self.exit_button.clear()

        self.desc_edit.clear()

        self.selected_files.clear()

        self.files_list.clear()

        self.name_edit.setFocus()

        self.files_list.clearSelection()

        self.credit_edit.clear()

        self.update_total_payment()

    def set_data(self, data):

        self.customer_id = data["id"]

        # =====================================================
        # اطلاعات مسافر
        # =====================================================

        self.name_edit.setText(
            data.get("full_name") or ""
        )

        self.phone_edit.setText(
            data.get("phone") or ""
        )

        cottage = str(
            data.get("cottage_number") or ""
        ).strip()

        self.selected_cottage = (
            cottage if cottage else None
        )

        if cottage:
            self.cottage_button.setText(
                f"🏠 کلبه {cottage}"
            )
        else:
            self.cottage_button.setText(
                "انتخاب کلبه"
            )

        self.entry_button.setText(
            data.get("check_in") or ""
        )

        self.exit_button.setText(
            data.get("check_out") or ""
        )

        self.desc_edit.setPlainText(
            data.get("description") or ""
        )

        # =====================================================
        # اطلاعات پرداخت
        # =====================================================

        self.pos_office_edit.setText(
            str(data.get("pos_office") or "")
        )

        self.pos_cafe_edit.setText(
            str(data.get("pos_cafe") or "")
        )

        self.pos_market_edit.setText(
            str(data.get("pos_market") or "")
        )

        self.cash_edit.setText(
            str(data.get("cash") or "")
        )

        self.card_edit.setText(
            str(data.get("card_transfer") or "")
        )

        self.receiver_edit.setText(
            data.get("card_transfer_receiver") or ""
        )

        self.credit_edit.setText(
            str(data.get("credit") or "")
        )

        # =====================================================
        # مدارک
        # =====================================================

        self.selected_files.clear()

        self.existing_files.clear()

        self.deleted_file_ids.clear()

        self.files_list.clear()

        self.files_changed = False

        files = data.get("files") or []

        for file in files:

            # -----------------------------------------
            # مدرک ذخیره شده در دیتابیس
            # -----------------------------------------

            if isinstance(file, dict):

                file_id = file.get("id")

                file_name = (
                        file.get("file_name")
                        or "مدرک بدون نام"
                )

                file_data = file.get(
                    "file_data"
                )

                file_path = (
                        file.get("file_path")
                        or ""
                )

                file_info = {

                    "id": file_id,

                    "file_name": file_name,

                    "file_data": file_data,

                    "file_path": file_path
                }

                self.existing_files.append(
                    file_info
                )

                # آیتم لیست
                item = QListWidgetItem(
                    file_name
                )

                # اطلاعات واقعی فایل
                item.setData(
                    Qt.UserRole,
                    {
                        "type": "existing",
                        "id": file_id
                    }
                )

                self.files_list.addItem(
                    item
                )

            # -----------------------------------------
            # فایل جدید
            # -----------------------------------------

            else:

                file_path = str(file)

                self.selected_files.append(
                    file_path
                )

                item = QListWidgetItem(
                    os.path.basename(file_path)
                )

                item.setData(
                    Qt.UserRole,
                    {
                        "type": "new",
                        "path": file_path
                    }
                )

                self.files_list.addItem(
                    item
                )

        # =====================================================
        # جمع پرداخت
        # =====================================================

        self.update_total_payment()


    def set_files(self, files):

        self.selected_files = files.copy()

        self.files_list.clear()

        for file in files:
            self.files_list.addItem(
                os.path.basename(file)
            )

    def get_files(self):

        return self.selected_files.copy()


    def set_initial_state(self):

        # ---------------- اطلاعات مسافر ----------------

        self.lbl_name.setVisible(False)
        self.name_edit.setVisible(False)

        self.lbl_phone.setVisible(False)
        self.phone_edit.setVisible(False)

        # ---------------- توضیحات ----------------

        self.lbl_desc.setVisible(False)
        self.desc_edit.setVisible(False)

        # ---------------- مدارک ----------------

        self.lbl_files.setVisible(False)
        self.files_list.setVisible(False)

        self.add_file_btn.setVisible(False)
        self.remove_file_btn.setVisible(False)

        # ---------------- اطلاعات پرداخت ----------------

        self.payment_group.setVisible(False)

        # ---------------- موارد اولیه ----------------

        self.entry_button.setVisible(True)
        self.exit_button.setVisible(True)
        self.cottage_button.setVisible(True)

    def select_entry_date(self):

        date = CalendarDialog.get_date(self)

        if date:
            self.entry_button.setText(date)

    def select_exit_date(self):

        date = CalendarDialog.get_date(self)

        if date:
            self.exit_button.setText(date)


    # --------------------------------------------

    def on_date_selected(self, date):

        if self.calendar_target == "entry":

            # فقط تاریخ ورود ثبت شود
            self.entry_button.setText(date)

            return

        if self.calendar_target == "exit":

            # تاریخ خروج ثبت شود
            self.exit_button.setText(date)

            # بعد از انتخاب تاریخ خروج،
            # پنجره انتخاب کلبه باز شود
            self.open_cottage_selection()

    # --------------------------------------------

    def open_cottage_selection(self):

        entry_date = self.entry_button.text().strip()
        exit_date = self.exit_button.text().strip()

        if (
                not entry_date
                or not exit_date
                or entry_date == "انتخاب تاریخ ورود"
                or exit_date == "انتخاب تاریخ خروج"
        ):
            return

        # ---------------------------------------------
        # شناسه مسافر فعلی در حالت تغییر
        # ---------------------------------------------

        ignore_customer_id = getattr(
            self,
            "customer_id",
            None
        )

        # ---------------------------------------------
        # باز کردن پنجره انتخاب کلبه
        # ---------------------------------------------

        dialog = CottageSelectionDialog(
            entry_date,
            exit_date,
            self,
            ignore_customer_id=ignore_customer_id
        )

        if dialog.exec():

            cottage = dialog.selected_cottage

            if cottage is None:
                return

            self.selected_cottage = cottage

            self.cottage_button.setText(
                f"🏠 کلبه {cottage}"
            )

            if not self.edit_mode:
                self.show_customer_fields()

    def show_customer_fields(self):

        widgets = [
            self.lbl_name,
            self.name_edit,

            self.lbl_phone,
            self.phone_edit,

            self.lbl_desc,
            self.desc_edit,

            self.lbl_files,
            self.files_list,

            self.add_file_btn,
            self.remove_file_btn,

            self.payment_group
        ]

        # همه ابتدا مخفی باشند
        for widget in widgets:
            widget.setVisible(False)
            widget.setWindowOpacity(0.0)

        self._animations = []
        self._animation_index = 0

        self.animate_widget_sequence(widgets, 0)

    def animate_widget_sequence(self, widgets, index):

        if index >= len(widgets):
            return

        widget = widgets[index]

        widget.setVisible(True)

        # شروع کمی پایین‌تر از جای اصلی
        start_pos = widget.pos()

        start_y = start_pos.y() + 12

        widget.move(
            start_pos.x(),
            start_y
        )

        # -------------------------
        # انیمیشن شفافیت
        # -------------------------

        opacity_animation = QPropertyAnimation(
            widget,
            b"windowOpacity",
            self
        )

        opacity_animation.setDuration(320)

        opacity_animation.setStartValue(0.0)

        opacity_animation.setEndValue(1.0)

        opacity_animation.setEasingCurve(
            QEasingCurve.OutCubic
        )

        # -------------------------
        # انیمیشن حرکت
        # -------------------------

        position_animation = QPropertyAnimation(
            widget,
            b"pos",
            self
        )

        position_animation.setDuration(380)

        position_animation.setStartValue(
            QPoint(
                start_pos.x(),
                start_y
            )
        )

        position_animation.setEndValue(
            start_pos
        )

        position_animation.setEasingCurve(
            QEasingCurve.OutCubic
        )

        # نگه داشتن انیمیشن‌ها
        self._animations.append(
            opacity_animation
        )

        self._animations.append(
            position_animation
        )

        # وقتی حرکت تمام شد، سراغ مورد بعدی برو
        position_animation.finished.connect(
            lambda:
            self.animate_widget_sequence(
                widgets,
                index + 1
            )
        )

        position_animation.finished.connect(
            lambda:
            self._cleanup_animation(
                opacity_animation,
                position_animation
            )
        )

        opacity_animation.start()
        position_animation.start()

    def _cleanup_animation(
            self,
            opacity_animation,
            position_animation
    ):

        if hasattr(self, "_animations"):

            if opacity_animation in self._animations:
                self._animations.remove(
                    opacity_animation
                )

            if position_animation in self._animations:
                self._animations.remove(
                    position_animation
                )

    def _remove_animation(self, animation):

        if hasattr(self, "_animations"):

            if animation in self._animations:
                self._animations.remove(animation)

    def format_money(self, text):
        digits = "".join(
            ch for ch in text
            if ch.isdigit()
        )

        if not digits:
            return ""

        return f"{int(digits):,}"

    def update_total_payment(self):

        fields = [
            self.pos_office_edit,
            self.pos_cafe_edit,
            self.pos_market_edit,
            self.cash_edit,
            self.card_edit
        ]

        total = 0

        for field in fields:

            text = field.text().replace(",", "").strip()

            if text.isdigit():
                total += int(text)

        self.total_label.setText(
            f"{total:,} تومان"
        )

    def on_payment_changed(self):

        field = self.sender()

        if field is None:
            return

        text = field.text()

        digits = "".join(
            ch for ch in text
            if ch.isdigit()
        )

        formatted = (
            f"{int(digits):,}"
            if digits
            else ""
        )

        if text != formatted:
            field.blockSignals(True)

            field.setText(formatted)

            field.setCursorPosition(
                len(formatted)
            )

            field.blockSignals(False)

        self.update_total_payment()

    def set_edit_mode(self, enabled=True):

        self.edit_mode = enabled

        if not enabled:
            return

        # همه فیلدها از ابتدا نمایان باشند
        self.lbl_name.setVisible(True)
        self.name_edit.setVisible(True)

        self.lbl_phone.setVisible(True)
        self.phone_edit.setVisible(True)

        self.lbl_desc.setVisible(True)
        self.desc_edit.setVisible(True)

        self.lbl_files.setVisible(True)
        self.files_list.setVisible(True)

        self.add_file_btn.setVisible(True)
        self.remove_file_btn.setVisible(True)

        self.payment_group.setVisible(True)

        self.entry_button.setVisible(True)
        self.exit_button.setVisible(True)
        self.cottage_button.setVisible(True)

    def open_file(self, item):

        if item is None:
            return

        file_info = item.data(
            Qt.UserRole
        )

        if not file_info:
            return

        # =====================================================
        # فایل جدید
        # =====================================================

        if file_info.get("type") == "new":

            file_path = file_info.get(
                "path"
            )

            if not file_path:
                return

            if not os.path.exists(file_path):
                QMessageBox.warning(
                    self,
                    "خطا",
                    "فایل موردنظر پیدا نشد."
                )

                return

            QDesktopServices.openUrl(
                QUrl.fromLocalFile(
                    file_path
                )
            )

            return

        # =====================================================
        # فایل قبلی دیتابیس
        # =====================================================

        if file_info.get("type") == "existing":

            file_id = file_info.get(
                "id"
            )

            file_data = None
            file_name = "document"

            # پیدا کردن فایل از existing_files
            for file in self.existing_files:

                if file.get("id") == file_id:
                    file_data = file.get(
                        "file_data"
                    )

                    file_name = (
                            file.get("file_name")
                            or "document"
                    )

                    break

            if not file_data:
                QMessageBox.warning(
                    self,
                    "خطا",
                    "اطلاعات فایل در دیتابیس پیدا نشد."
                )

                return

            try:

                # پسوند فایل
                suffix = Path(
                    file_name
                ).suffix

                if not suffix:
                    suffix = ".bin"

                # ساخت فایل موقت
                temp_file = tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=suffix
                )

                temp_path = temp_file.name

                temp_file.write(
                    bytes(file_data)
                )

                temp_file.close()

                # باز کردن با برنامه پیش‌فرض ویندوز
                QDesktopServices.openUrl(
                    QUrl.fromLocalFile(
                        temp_path
                    )
                )

            except Exception as e:

                QMessageBox.critical(
                    self,
                    "خطا",
                    f"باز کردن فایل انجام نشد:\n{e}"
                )



