import os
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QListWidget,
    QPushButton,
    QMessageBox
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from database import DatabaseManager


class DocumentsWindow(QDialog):

    def __init__(self, customer_id, parent=None):

        super().__init__(parent)

        self.customer_id = customer_id

        self.db = DatabaseManager()

        self.setWindowTitle("مدارک مسافر")

        self.setWindowIcon(QIcon("assets/icons/logo.ico"))

        self.resize(700, 500)

        layout = QVBoxLayout(self)

        self.list_widget = QListWidget()

        layout.addWidget(self.list_widget)

        self.close_btn = QPushButton("بستن")

        layout.addWidget(self.close_btn)

        self.close_btn.clicked.connect(self.accept)

        self.list_widget.itemDoubleClicked.connect(
            self.open_selected_file
        )

        self.load_files()

    # ---------------------------------------------

    def load_files(self):

        self.list_widget.clear()

        files = self.db.get_customer_files(
            self.customer_id
        )

        for file in files:
            self.list_widget.addItem(file)

    # ---------------------------------------------

    def open_selected_file(self, item):

        path = item.text()

        if not os.path.exists(path):

            QMessageBox.warning(

                self,

                "خطا",

                "فایل پیدا نشد."

            )

            return

        QDesktopServices.openUrl(

            QUrl.fromLocalFile(path)

        )