from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
)

from PySide6.QtGui import (
    QPixmap,
    QFont,
    QIcon,
)

from PySide6.QtCore import Qt
from core.resource_path import resource_path


class AboutDialog(QDialog):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("درباره VIVO")

        self.setWindowIcon(
            QIcon(
                resource_path("assets/icons/logo.ico")
            )
        )

        self.setFixedSize(420, 450)

        self.build_ui()

    def build_ui(self):

        layout = QVBoxLayout(self)

        layout.setContentsMargins(30, 30, 30, 30)

        layout.setSpacing(15)

        logo = QLabel()

        pix = QPixmap(
            resource_path("assets/icons/logo.png")
        )

        logo.setPixmap(
            pix.scaled(
                120,
                120,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )

        logo.setAlignment(Qt.AlignCenter)

        title = QLabel("VIVO")

        title.setAlignment(Qt.AlignCenter)

        title.setFont(
            QFont("Arial", 24, QFont.Bold)
        )

        info = QLabel(

            "برنامه مدیریت اقامتگاه\n\n"

            "نسخه : 2.0.1\n\n"

            "طراح و توسعه دهنده\n\n"

            "Vihan Emadi\n\n"

            "© 2026\n"

            "تمام حقوق محفوظ است."

        )

        info.setAlignment(Qt.AlignCenter)

        info.setWordWrap(True)

        info.setFont(
            QFont("Tahoma", 11)
        )

        close_btn = QPushButton("بستن")

        close_btn.setFixedHeight(40)

        close_btn.clicked.connect(self.accept)

        layout.addWidget(logo)

        layout.addWidget(title)

        layout.addWidget(info)

        layout.addStretch()

        layout.addWidget(close_btn)