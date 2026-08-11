from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QGridLayout,
    QPushButton,
    QLabel
)

from PySide6.QtCore import Qt

from core.customer_controller import CustomerController


class CottageSelectionDialog(QDialog):

    def __init__(
        self,
        check_in,
        check_out,
        parent=None,
        ignore_customer_id=None
    ):
        super().__init__(parent)

        self.controller = CustomerController()

        self.check_in = check_in
        self.check_out = check_out

        # در حالت تغییر، مسافر فعلی نادیده گرفته می‌شود
        self.ignore_customer_id = ignore_customer_id

        self.selected_cottage = None

        self.setWindowTitle(
            "انتخاب کلبه"
        )

        self.resize(
            900,
            650
        )

        self.build_ui()

        self.load_cottages()

    # =====================================================
    # ساخت رابط کاربری
    # =====================================================

    def build_ui(self):

        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(
            20,
            20,
            20,
            20
        )

        main_layout.setSpacing(15)

        # -------------------------------------------------
        # عنوان
        # -------------------------------------------------

        title = QLabel(
            "انتخاب کلبه برای بازه اقامت"
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        title.setStyleSheet(
            """
            QLabel {
                font-size: 18px;
                font-weight: bold;
            }
            """
        )

        main_layout.addWidget(title)

        # -------------------------------------------------
        # تاریخ
        # -------------------------------------------------

        dates = QLabel(
            f"ورود: {self.check_in}    "
            f"خروج: {self.check_out}"
        )

        dates.setAlignment(
            Qt.AlignCenter
        )

        dates.setStyleSheet(
            """
            QLabel {
                font-size: 13px;
                color: #555;
            }
            """
        )

        main_layout.addWidget(dates)

        # -------------------------------------------------
        # کلبه‌ها
        # -------------------------------------------------

        self.grid = QGridLayout()

        self.grid.setHorizontalSpacing(15)
        self.grid.setVerticalSpacing(15)

        main_layout.addLayout(
            self.grid
        )

    # =====================================================
    # دریافت وضعیت کلبه‌ها
    # =====================================================

    def load_cottages(self):

        cottages = (
            self.controller
            .get_cottages_status_for_period(
                self.check_in,
                self.check_out,
                ignore_customer_id=self.ignore_customer_id
            )
        )

        row = 0
        col = 0

        for number in range(1, 17):

            info = cottages[str(number)]

            button = QPushButton()

            button.setFixedSize(
                190,
                125
            )

            button.setCursor(
                Qt.PointingHandCursor
            )

            # -------------------------------------------------
            # کلبه رزرو شده
            # -------------------------------------------------

            if info["occupied"]:

                name = info["name"] or "نامشخص"

                check_out = (
                    info["check_out"]
                    or ""
                )

                button.setText(
                    f"🏠 کلبه {number}\n\n"
                    f"🔴 رزرو شده\n\n"
                    f"{name}\n"
                    f"تا {check_out}"
                )

                button.setEnabled(False)

                button.setStyleSheet(
                    """
                    QPushButton {
                        background: #7A1F1F;
                        color: white;
                        border: 2px solid #5A1515;
                        border-radius: 14px;
                        font-size: 12px;
                        font-weight: bold;
                    }

                    QPushButton:disabled {
                        background: #7A1F1F;
                        color: white;
                    }
                    """
                )

            # -------------------------------------------------
            # کلبه آزاد
            # -------------------------------------------------

            else:

                button.setText(
                    f"🏠 کلبه {number}\n\n"
                    f"🟢 خالی\n\n"
                    f"قابل انتخاب"
                )

                button.setEnabled(True)

                button.setStyleSheet(
                    """
                    QPushButton {
                        background: #1F5F2B;
                        color: white;
                        border: 2px solid #16471F;
                        border-radius: 14px;
                        font-size: 12px;
                        font-weight: bold;
                    }

                    QPushButton:hover {
                        background: #2E7D32;
                        border: 2px solid #43A047;
                    }

                    QPushButton:pressed {
                        background: #145A20;
                    }
                    """
                )

                button.clicked.connect(
                    lambda checked=False,
                    cottage=number:
                    self.select_cottage(cottage)
                )

            self.grid.addWidget(
                button,
                row,
                col
            )

            col += 1

            if col == 4:

                col = 0
                row += 1

    # =====================================================
    # انتخاب کلبه
    # =====================================================

    def select_cottage(
        self,
        cottage_number
    ):

        self.selected_cottage = (
            cottage_number
        )

        self.accept()