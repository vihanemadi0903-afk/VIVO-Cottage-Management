from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QMessageBox,
    QTableWidgetItem
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from ui.widgets.header_widget import HeaderWidget
from ui.widgets.search_widget import SearchWidget
from ui.widgets.customer_table import CustomerTable
from ui.widgets.action_buttons import ActionButtons
from ui.add_customer_dialog import AddCustomerDialog
from ui.edit_customer_dialog import EditCustomerDialog
from core.customer_controller import CustomerController
from ui.documents_window import DocumentsWindow
from ui.cottage_status_dialog import CottageStatusDialog
from ui.settings_dialog import SettingsDialog
from core.resource_path import resource_path
from ui.about_dialog import AboutDialog


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.controller = CustomerController()

        self.setWindowTitle("برنامه مدیریتی VIVO")

        self.setWindowIcon(
            QIcon(
                resource_path("assets/icons/logo.ico")
            )
        )

        self.resize(1200, 700)

        self.build_ui()

        self.connect_signals()

        self.load_customers()

    # ===================================================
    # ساخت رابط کاربری
    # ===================================================

    def build_ui(self):

        layout = QVBoxLayout(self)

        self.header = HeaderWidget()
        layout.addWidget(self.header)

        self.search = SearchWidget()
        layout.addWidget(self.search)

        self.customer_table = CustomerTable()
        layout.addWidget(self.customer_table)

        self.buttons = ActionButtons()
        layout.addWidget(self.buttons)

    # ===================================================
    # اتصال سیگنال ها
    # ===================================================

    def connect_signals(self):

        self.buttons.add_btn.clicked.connect(
            self.open_add_dialog
        )

        self.buttons.edit_btn.clicked.connect(
            self.open_edit_dialog
        )

        self.buttons.delete_btn.clicked.connect(
            self.delete_customer
        )

        self.buttons.images_btn.clicked.connect(
            self.open_customer_documents
        )

        self.buttons.cottage_btn.clicked.connect(
            self.open_cottage_status
        )

        self.customer_table.table.cellDoubleClicked.connect(
            self.table_double_clicked
        )

        # ---------- فیلترهای لحظه‌ای ----------

        self.search.name_edit.textChanged.connect(
            self.search_customers
        )

        self.search.phone_edit.textChanged.connect(
            self.search_customers
        )

        self.search.date_changed.connect(
            self.search_customers
        )

        self.search.status_combo.currentIndexChanged.connect(
            self.search_customers
        )

        self.search.cottage_combo.currentIndexChanged.connect(
            self.search_customers
        )

        self.header.settings_button.clicked.connect(
            self.open_settings
        )

        self.header.about_clicked.connect(
            self.open_about
        )

    # ===================================================
    # ثبت مسافر
    # ===================================================

    def open_add_dialog(self):

        dialog = AddCustomerDialog()

        if dialog.exec():
            self.load_customers()

    # ===================================================
    # ویرایش
    # ===================================================

    def open_edit_dialog(self):

        table = self.customer_table.table

        row = table.currentRow()

        if row == -1:

            QMessageBox.warning(
                self,
                "خطا",
                "ابتدا یک ردیف را انتخاب کنید."
            )

            return

        customer_id = int(table.item(row, 0).text())

        customer = self.controller.get_customer(customer_id)

        # اضافه کردن لیست مدارک
        customer_id = int(table.item(row, 0).text())

        customer = self.controller.get_customer(customer_id)

        dialog = EditCustomerDialog(customer)

        if dialog.exec():

            self.load_customers()

    # ===================================================
    # بارگذاری جدول
    # ===================================================

    def load_customers(self):

        rows = self.controller.get_customers()

        table = self.customer_table.table

        table.setRowCount(0)

        columns = [

            ("id", 0),

            ("full_name", 1),

            ("phone", 2),

            ("cottage_number", 3),

            ("check_in", 4),

            ("check_out", 5)

        ]

        for row_data in rows:

            row = table.rowCount()

            table.insertRow(row)

            for key, column in columns:

                value = row_data[key]

                if value is None:
                    value = ""

                item = QTableWidgetItem(str(value))

                item.setTextAlignment(Qt.AlignCenter)

                table.setItem(row, column, item)

            # ---------------- وضعیت ----------------

            required_fields = [

                row_data["full_name"],

                row_data["phone"],

                row_data["cottage_number"],

                row_data["check_in"],

                row_data["check_out"]

            ]

            is_complete = all(

                str(value).strip() != ""

                for value in required_fields

            )

            if is_complete:
                status_text = "🟢"
            else:
                status_text = "🔴"

            status_item = QTableWidgetItem(status_text)

            status_item.setTextAlignment(Qt.AlignCenter)

            table.setItem(row, 6, status_item)

            # ---------------- مدارک ----------------

            customer_id = row_data["id"]

            docs_item = QTableWidgetItem()

            if self.controller.customer_has_files(customer_id):

                docs_item.setText("📎")

            else:

                docs_item.setText("")

            docs_item.setTextAlignment(Qt.AlignCenter)

            table.setItem(row, 7, docs_item)

    # ===================================================
    # حذف مسافر
    # ===================================================

    def delete_customer(self):

        table = self.customer_table.table

        row = table.currentRow()

        if row < 0:
            QMessageBox.warning(
                self,
                "خطا",
                "ابتدا یک مسافر را انتخاب کنید."
            )
            return

        customer_id = int(table.item(row, 0).text())
        customer_name = table.item(row, 1).text()

        answer = QMessageBox.question(
            self,
            "تایید حذف",
            f"آیا از حذف\n\n{customer_name}\n\nمطمئن هستید؟",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if answer == QMessageBox.No:
            return

        try:

            self.controller.delete_customer(customer_id)

            self.load_customers()

            table.clearSelection()

            QMessageBox.information(
                self,
                "موفق",
                "مسافر با موفقیت حذف شد."
            )

        except Exception as e:

            QMessageBox.critical(
                self,
                "خطا",
                str(e)
            )
    # ===================================================
    # دریافت ردیف انتخاب شده
    # ===================================================

    def get_selected_row(self):

        table = self.customer_table.table

        row = table.currentRow()

        if row == -1:
            return None

        return row

    # ===================================================
    # دریافت شناسه مسافر انتخاب شده
    # ===================================================

    def get_selected_customer_id(self):

        row = self.get_selected_row()

        if row is None:
            return None

        table = self.customer_table.table

        return int(table.item(row, 0).text())

    # ===================================================
    # آماده برای جستجو
    # ===================================================

    def search_customers(self):

        rows = self.controller.search_customers(

            self.search.status_combo.currentText(),

            self.search.name_edit.text().strip(),

            self.search.phone_edit.text().strip(),

            self.search.cottage_combo.currentText(),

            self.search.get_entry_date(),

            self.search.get_exit_date()

        )

        table = self.customer_table.table

        table.setRowCount(0)

        columns = [

            ("id", 0),

            ("full_name", 1),

            ("phone", 2),

            ("cottage_number", 3),

            ("check_in", 4),

            ("check_out", 5)

        ]

        for row_data in rows:

            row = table.rowCount()

            table.insertRow(row)

            for key, column in columns:

                value = row_data[key]

                if value is None:
                    value = ""

                item = QTableWidgetItem(
                    str(value)
                )

                item.setTextAlignment(
                    Qt.AlignCenter
                )

                table.setItem(
                    row,
                    column,
                    item
                )

            # ---------------- وضعیت ----------------

            status_item = QTableWidgetItem()

            has_files = (
                self.controller.customer_has_files(
                    row_data["id"]
                )
            )

            if has_files:
                status_item.setText("🟢")
            else:
                status_item.setText("🔴")

            status_item.setTextAlignment(
                Qt.AlignCenter
            )

            table.setItem(
                row,
                6,
                status_item
            )

            # ---------------- مدارک ----------------

            docs_item = QTableWidgetItem()

            if has_files:
                docs_item.setText("📎")
            else:
                docs_item.setText("")

            docs_item.setTextAlignment(
                Qt.AlignCenter
            )

            table.setItem(
                row,
                7,
                docs_item
            )

    # ===================================================
    # آماده برای وضعیت کلبه ها
    # ===================================================

    def open_cottage_status(self):

        print("Cottage button clicked")

        dialog = CottageStatusDialog()

        dialog.exec()

    # ===================================================
    # آماده برای مدارک
    # ===================================================

    # ===================================================
    # دوبار کلیک روی جدول
    # ===================================================

    def table_double_clicked(self, row, column):

        # فقط اگر روی ستون مدارک دوبار کلیک شد
        if column == 7:
            self.open_customer_documents()

    # ===================================================
    # پنجره مدارک
    # ===================================================

    def open_customer_documents(self):

        customer_id = self.get_selected_customer_id()

        if customer_id is None:
            QMessageBox.warning(
                self,
                "خطا",
                "ابتدا یک مسافر را انتخاب کنید."
            )
            return

        from ui.documents_window import DocumentsWindow

        dialog = DocumentsWindow(
            customer_id,
            self
        )

        dialog.exec()

    def table_double_clicked(self, row, column):

        # فقط ستون مدارک
        if column != 7:
            return

        self.customer_table.table.selectRow(row)

        self.open_customer_documents()

    def open_settings(self):

        dialog = SettingsDialog()

        dialog.exec()

        # بعد از بسته شدن تنظیمات،
        # اطلاعات جدول را دوباره از دیتابیس بخوان
        self.load_customers()


    def open_about(self):

        dialog = AboutDialog()

        dialog.exec()



