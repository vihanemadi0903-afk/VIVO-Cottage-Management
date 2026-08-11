from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QPushButton
)

from ui.dialogs.calendar_dialog import CalendarDialog


class SearchWidget(QWidget):

    date_changed = Signal()

    def __init__(self):
        super().__init__()

        self.setLayoutDirection(Qt.RightToLeft)

        layout = QHBoxLayout(self)

        layout.setSpacing(10)

        # ---------------- وضعیت ----------------

        layout.addWidget(QLabel("وضعیت"))

        self.status_combo = QComboBox()

        self.status_combo.addItems([
            "همه",
            "🟢 کامل",
            "🔴 ناقص"
        ])

        self.status_combo.setFixedWidth(110)

        layout.addWidget(self.status_combo)

        # ---------------- کلبه ----------------

        layout.addWidget(QLabel("کلبه"))

        self.cottage_combo = QComboBox()

        self.cottage_combo.addItem("همه")

        for i in range(1, 17):
            self.cottage_combo.addItem(str(i))

        self.cottage_combo.setFixedWidth(90)

        layout.addWidget(self.cottage_combo)

        # ---------------- نام ----------------

        layout.addWidget(QLabel("نام"))

        self.name_edit = QLineEdit()

        self.name_edit.setPlaceholderText(
            "نام و نام خانوادگی"
        )

        self.name_edit.setFixedWidth(240)

        layout.addWidget(self.name_edit)

        # ---------------- شماره تماس ----------------

        layout.addWidget(QLabel("تلفن"))

        self.phone_edit = QLineEdit()

        self.phone_edit.setPlaceholderText(
            "09..."
        )

        self.phone_edit.setFixedWidth(150)

        layout.addWidget(self.phone_edit)

        # =====================================================
        # تاریخ ورود
        # =====================================================

        layout.addWidget(QLabel("ورود"))

        entry_layout = QHBoxLayout()
        entry_layout.setSpacing(3)

        self.entry_button = QPushButton(
            "انتخاب تاریخ"
        )

        self.entry_button.setFixedWidth(110)

        self.entry_clear_button = QPushButton("✕")

        self.entry_clear_button.setFixedSize(
            28,
            28
        )

        self.entry_button.clicked.connect(
            self.select_entry_date
        )

        self.entry_clear_button.clicked.connect(
            self.clear_entry_date
        )

        entry_layout.addWidget(
            self.entry_button
        )

        entry_layout.addWidget(
            self.entry_clear_button
        )

        layout.addLayout(
            entry_layout
        )

        # =====================================================
        # تاریخ خروج
        # =====================================================

        layout.addWidget(QLabel("خروج"))

        exit_layout = QHBoxLayout()
        exit_layout.setSpacing(3)

        self.exit_button = QPushButton(
            "انتخاب تاریخ"
        )

        self.exit_button.setFixedWidth(110)

        self.exit_clear_button = QPushButton("✕")

        self.exit_clear_button.setFixedSize(
            28,
            28
        )

        self.exit_button.clicked.connect(
            self.select_exit_date
        )

        self.exit_clear_button.clicked.connect(
            self.clear_exit_date
        )

        exit_layout.addWidget(
            self.exit_button
        )

        exit_layout.addWidget(
            self.exit_clear_button
        )

        layout.addLayout(
            exit_layout
        )

        layout.addStretch()

    # =====================================================
    # انتخاب تاریخ ورود
    # =====================================================

    def select_entry_date(self):

        date = CalendarDialog.get_date(self)

        if date:

            self.entry_button.setText(
                str(date)
            )

            self.date_changed.emit()

    # =====================================================
    # انتخاب تاریخ خروج
    # =====================================================

    def select_exit_date(self):

        date = CalendarDialog.get_date(self)

        if date:

            self.exit_button.setText(
                str(date)
            )

            self.date_changed.emit()

    # =====================================================
    # دریافت تاریخ ورود
    # =====================================================

    def get_entry_date(self):

        text = self.entry_button.text().strip()

        if text == "انتخاب تاریخ":
            return ""

        return text

    # =====================================================
    # دریافت تاریخ خروج
    # =====================================================

    def get_exit_date(self):

        text = self.exit_button.text().strip()

        if text == "انتخاب تاریخ":
            return ""

        return text

    # =====================================================
    # پاک کردن تاریخ ورود
    # =====================================================

    def clear_entry_date(self):

        self.entry_button.setText(
            "انتخاب تاریخ"
        )

        self.date_changed.emit()

    # =====================================================
    # پاک کردن تاریخ خروج
    # =====================================================

    def clear_exit_date(self):

        self.exit_button.setText(
            "انتخاب تاریخ"
        )

        self.date_changed.emit()

    # =====================================================
    # پاک کردن هر دو تاریخ
    # =====================================================

    def clear_dates(self):

        self.entry_button.setText(
            "انتخاب تاریخ"
        )

        self.exit_button.setText(
            "انتخاب تاریخ"
        )

        self.date_changed.emit()
