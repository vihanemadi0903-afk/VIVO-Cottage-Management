from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton
)
from datetime import datetime
from core.date_utils import DateUtils
from core.resource_path import resource_path
from PySide6.QtCore import Signal


class HeaderWidget(QWidget):

    settings_clicked = Signal()
    about_clicked = Signal()

    def __init__(self):
        super().__init__()

        self.build_ui()

        self.settings_button.clicked.connect(
            self.settings_clicked.emit
        )

        self.about_button.clicked.connect(
            self.about_clicked.emit
        )

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

        self.update_time()

    def build_ui(self):

        layout = QHBoxLayout(self)

        # ---------- لوگو ----------

        self.logo = QLabel()

        pix = QPixmap(
            resource_path("assets/icons/logo.png")
        )

        if not pix.isNull():
            self.logo.setPixmap(
                pix.scaled(
                    70,
                    70,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            )

        # ---------- عنوان ----------

        title_layout = QVBoxLayout()

        self.title = QLabel("برنامه مدیریتی VIVO")
        self.title.setFont(QFont("Tahoma", 16, QFont.Bold))

        self.subtitle = QLabel("سیستم مدیریت اقامتگاه")
        self.subtitle.setFont(QFont("Tahoma", 10))

        title_layout.addWidget(self.title)
        title_layout.addWidget(self.subtitle)

        # ---------- ساعت ----------

        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignRight)
        self.time_label.setFont(QFont("Consolas", 11))

        # ---------- تنظیمات ----------

        self.settings_button = QPushButton("⚙")

        self.settings_button.setFixedSize(38, 38)

        self.settings_button.setCursor(Qt.PointingHandCursor)

        self.settings_button.setFont(QFont("Segoe UI Emoji", 13))

        self.settings_button.setStyleSheet("""
        QPushButton{

            background:#3b3b3b;

            border:1px solid #555;

            border-radius:8px;

            color:white;

        }

        QPushButton:hover{

            background:#4a4a4a;

        }

        QPushButton:pressed{

            background:#666;

        }
        """)

        self.about_button = QPushButton("❓")

        self.about_button.setFixedSize(38, 38)

        self.about_button.setToolTip("درباره VIVO")

        self.about_button.setCursor(Qt.PointingHandCursor)

        self.about_button.setFont(QFont("Segoe UI Emoji", 13))

        self.about_button.setStyleSheet("""
        QPushButton{

            background:#3b3b3b;

            border:1px solid #555;

            border-radius:8px;

            color:white;

        }

        QPushButton:hover{

            background:#4a4a4a;

        }

        QPushButton:pressed{

            background:#666;

        }
        """)

        layout.addWidget(self.logo)

        layout.addLayout(title_layout)

        layout.addStretch()

        layout.addWidget(self.about_button)

        layout.addWidget(self.settings_button)

        layout.addSpacing(8)

        layout.addWidget(self.time_label)


    def update_time(self):

        # تاریخ شمسی
        today = DateUtils.today()

        # ساعت سیستم
        current_time = datetime.now().strftime("%H:%M:%S")

        self.time_label.setText(
            f"{today}\n{current_time}"
        )