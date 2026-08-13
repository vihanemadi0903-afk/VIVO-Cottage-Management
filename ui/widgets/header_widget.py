from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QPixmap, QIcon
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QHBoxLayout,
    QVBoxLayout
)
from datetime import datetime

from core.date_utils import DateUtils
from core.resource_path import resource_path
from ui.widgets.action_buttons import AnimatedButton


class HeaderWidget(QWidget):

    settings_clicked = Signal()
    about_clicked = Signal()
    calendar_clicked = Signal()

    def __init__(self):
        super().__init__()

        self.build_ui()

        # ---------- اتصال دکمه‌ها ----------

        self.settings_button.clicked.connect(
            self.settings_clicked.emit
        )

        self.about_button.clicked.connect(
            self.about_clicked.emit
        )

        self.calendar_button.clicked.connect(
            self.calendar_clicked.emit
        )

        # ---------- تایمر ساعت ----------

        self.timer = QTimer(self)

        self.timer.timeout.connect(
            self.update_time
        )

        self.timer.start(1000)

        self.update_time()

    def build_ui(self):

        layout = QHBoxLayout(self)

        # ==================================================
        # لوگو
        # ==================================================

        self.logo = QLabel()

        pix = QPixmap(
            resource_path(
                "assets/icons/logo.png"
            )
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

        # ==================================================
        # عنوان
        # ==================================================

        title_layout = QVBoxLayout()

        self.title = QLabel(
            "برنامه مدیریتی VIVO"
        )

        self.title.setFont(
            QFont(
                "Tahoma",
                16,
                QFont.Bold
            )
        )

        self.subtitle = QLabel(
            "سیستم مدیریت اقامتگاه"
        )

        self.subtitle.setFont(
            QFont(
                "Tahoma",
                10
            )
        )

        title_layout.addWidget(
            self.title
        )

        title_layout.addWidget(
            self.subtitle
        )

        # ==================================================
        # ساعت
        # ==================================================

        self.time_label = QLabel()

        self.time_label.setAlignment(
            Qt.AlignRight
        )

        self.time_label.setFont(
            QFont(
                "Consolas",
                11
            )
        )

        # ==================================================
        # دکمه درباره
        # ==================================================

        self.about_button = AnimatedButton("")

        self.about_button.setFixedSize(
            38,
            38
        )

        self.about_button.setToolTip(
            "درباره VIVO"
        )

        self.about_button.setIcon(
            QIcon(
                resource_path(
                    "assets/icons/about.png"
                )
            )
        )

        self.about_button.setIconSize(
            self.about_button.size() * 0.55
        )

        # ==================================================
        # دکمه تقویم
        # ==================================================

        self.calendar_button = AnimatedButton("")

        self.calendar_button.setFixedSize(
            38,
            38
        )

        self.calendar_button.setToolTip(
            "تقویم"
        )

        self.calendar_button.setIcon(
            QIcon(
                resource_path(
                    "assets/icons/calendar.png"
                )
            )
        )

        self.calendar_button.setIconSize(
            self.calendar_button.size() * 0.55
        )

        # ==================================================
        # دکمه تنظیمات
        # ==================================================

        self.settings_button = AnimatedButton("")

        self.settings_button.setFixedSize(
            38,
            38
        )

        self.settings_button.setToolTip(
            "تنظیمات"
        )

        self.settings_button.setIcon(
            QIcon(
                resource_path(
                    "assets/icons/settings.png"
                )
            )
        )

        self.settings_button.setIconSize(
            self.settings_button.size() * 0.55
        )

        # ==================================================
        # چیدمان نهایی Header
        # ==================================================

        layout.addWidget(
            self.logo
        )

        layout.addLayout(
            title_layout
        )

        layout.addStretch()

        # درباره
        layout.addWidget(
            self.about_button
        )

        # تقویم
        layout.addWidget(
            self.calendar_button
        )

        # تنظیمات
        layout.addWidget(
            self.settings_button
        )

        layout.addSpacing(8)

        # ساعت
        layout.addWidget(
            self.time_label
        )

    def update_time(self):

        # تاریخ شمسی
        today = DateUtils.today()

        # ساعت سیستم
        current_time = datetime.now().strftime(
            "%H:%M:%S"
        )

        self.time_label.setText(
            f"{today}\n{current_time}"
        )