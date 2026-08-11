from PySide6.QtWidgets import (
    QDialog,
    QGridLayout,
    QLabel,
    QVBoxLayout
)

from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from core.customer_controller import CustomerController


class CottageStatusDialog(QDialog):

    def __init__(self):
        super().__init__()

        self.controller = CustomerController()

        self.setWindowTitle(
            "وضعیت اجاره کلبه‌ها"
        )

        self.resize(
            900,
            650
        )

        layout = QVBoxLayout(self)

        grid = QGridLayout()

        grid.setHorizontalSpacing(15)
        grid.setVerticalSpacing(15)

        layout.addLayout(grid)

        cottages = (
            self.controller.get_cottages_status()
        )

        row = 0
        col = 0

        for number in range(1, 17):

            info = cottages[str(number)]

            # ==========================================
            # کلبه رزرو شده
            # ==========================================

            if info["occupied"]:

                text = (
                    f"🏠 کلبه {number}\n\n"
                    f"🔴 رزرو شده\n\n"
                    f"{info['name']}\n\n"
                    f"تا\n"
                    f"{info['check_out']}"
                )

                color = "#7a1f1f"

            # ==========================================
            # کلبه آزاد
            # ==========================================

            else:

                text = (
                    f"🏠 کلبه {number}\n\n"
                    f"🟢 خالی"
                )

                color = "#1f5f2b"

            # ==========================================
            # کارت
            # ==========================================

            label = QLabel(text)

            label.setAlignment(
                Qt.AlignCenter
            )

            label.setWordWrap(True)

            label.setMinimumHeight(
                130
            )

            label.setFont(
                QFont(
                    "B Nazanin",
                    12
                )
            )

            label.setStyleSheet(
                f"""
                QLabel {{
                    border: 2px solid #555;
                    border-radius: 12px;
                    padding: 18px;
                    background: {color};
                    color: white;
                }}
                """
            )

            grid.addWidget(
                label,
                row,
                col
            )

            col += 1

            if col == 4:
                col = 0
                row += 1