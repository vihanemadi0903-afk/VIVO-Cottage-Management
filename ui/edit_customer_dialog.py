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


class EditCustomerDialog(QDialog):

    def __init__(self, customer):
        super().__init__()

        self.customer = customer
        self.controller = CustomerController()

        self.setWindowTitle("ویرایش اطلاعات مسافر")
        self.setWindowIcon(QIcon("assets/icons/logo.ico"))
        self.resize(700, 650)

        layout = QVBoxLayout(self)

        self.form = CustomerForm()
        self.form.set_edit_mode(True)
        self.form.set_data(customer)

        layout.addWidget(self.form)

        # نمایش اطلاعات فعلی
        self.form.set_data(customer)

        buttons = QHBoxLayout()

        self.save_btn = QPushButton("ذخیره تغییرات")
        self.cancel_btn = QPushButton("انصراف")

        buttons.addWidget(self.save_btn)
        buttons.addWidget(self.cancel_btn)

        layout.addLayout(buttons)

        self.save_btn.clicked.connect(self.save_changes)
        self.cancel_btn.clicked.connect(self.reject)

    # ----------------------------------------

    def save_changes(self):

        data = self.form.get_data()

        # اگر شماره وارد شده باشد باید 11 رقم باشد
        if data["phone"] and len(data["phone"]) != 11:

            QMessageBox.warning(
                self,
                "خطا",
                "شماره تماس باید 11 رقم باشد."
            )
            return

        try:

            self.controller.update_customer(
                self.customer["id"],
                data
            )

            QMessageBox.information(
                self,
                "موفق",
                "اطلاعات با موفقیت ویرایش شد."
            )

            self.accept()

        except Exception as e:

            QMessageBox.critical(
                self,
                "خطا",
                str(e)
            )