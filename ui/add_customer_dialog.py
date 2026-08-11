from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QMessageBox
)

from PySide6.QtGui import QIcon

from ui.widgets.customer_form import CustomerForm
from core.customer_controller import CustomerController


class AddCustomerDialog(QDialog):

    def __init__(self):
        super().__init__()

        self.controller = CustomerController()

        self.setWindowTitle("ثبت مسافر جدید")
        self.setWindowIcon(QIcon("assets/icons/logo.ico"))
        self.resize(700, 650)

        layout = QVBoxLayout(self)

        # فرم
        self.form = CustomerForm()
        layout.addWidget(self.form)

        # دکمه ها
        button_layout = QHBoxLayout()

        self.ok_btn = QPushButton("ثبت")
        self.cancel_btn = QPushButton("انصراف")

        button_layout.addWidget(self.ok_btn)
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)

        self.ok_btn.clicked.connect(self.save_customer)
        self.cancel_btn.clicked.connect(self.reject)

    # -------------------------------------------------

    def save_customer(self):

        data = self.form.get_data()

        # اگر شماره تماس وارد شده، باید 11 رقم باشد
        if data["phone"] and len(data["phone"]) != 11:
            QMessageBox.warning(
                self,
                "خطا",
                "شماره تماس باید 11 رقم باشد."
            )
            return

        if (
                not data["name"].strip()
                and not data["phone"].strip()
                and data["cottage"] == "انتخاب کنید"
                and not data["entry"].strip()
                and not data["exit"].strip()
                and not data["description"].strip()
                and len(data["files"]) == 0
        ):
            QMessageBox.warning(
                self,
                "خطا",
                "حداقل یکی از اطلاعات را وارد کنید."
            )
            return

        try:

            self.controller.add_customer(data)

            QMessageBox.information(
                self,
                "موفق",
                "مسافر با موفقیت ثبت شد."
            )

            self.accept()

        except Exception as e:

            QMessageBox.critical(
                self,
                "خطا",
                str(e)
            )