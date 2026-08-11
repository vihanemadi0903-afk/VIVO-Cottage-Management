from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon, QPixmap
from ui.main_window import MainWindow
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QMessageBox,
)
from core.resource_path import resource_path



class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.main_window = None

        self.setWindowTitle("برنامه مدیریتی VIVO")
        self.setWindowIcon(
            QIcon(
                resource_path("assets/icons/logo.ico")
            )
        )
        self.setFixedSize(420, 500)

        self.build_ui()

    def build_ui(self):
        layout = QVBoxLayout(self)

        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        logo = QLabel()

        pixmap = QPixmap(
            resource_path("assets/icons/logo.png")
        )

        logo.setPixmap(
            pixmap.scaled(
                140,
                140,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )

        logo.setAlignment(Qt.AlignCenter)

        title = QLabel("VIVO")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 26, QFont.Bold))

        subtitle = QLabel("برنامه مدیریتی VIVO")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(QFont("Tahoma", 14))

        password_label = QLabel("رمز عبور")

        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText("رمز عبور را وارد کنید")

        login_btn = QPushButton("ورود")
        login_btn.setFixedHeight(45)

        login_btn.clicked.connect(self.login)

        layout.addStretch()

        layout.addWidget(logo)

        layout.addWidget(title)
        layout.addWidget(subtitle)

        layout.addSpacing(30)

        layout.addWidget(password_label)
        layout.addWidget(self.password)

        layout.addSpacing(20)

        layout.addWidget(login_btn)

        layout.addStretch()

    def login(self):

        if self.password.text() != "0903":

            QMessageBox.warning(
                self,
                "خطا",
                "رمز عبور اشتباه است."
            )
            return

        self.main_window = MainWindow()
        self.main_window.show()

        self.close()
