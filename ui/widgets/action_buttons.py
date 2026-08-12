from PySide6.QtCore import (
    Qt,
    QPropertyAnimation,
    QEasingCurve,
    QPoint
)

from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QPushButton,
    QGraphicsDropShadowEffect
)


class AnimatedButton(QPushButton):

    def __init__(self, text, parent=None):
        super().__init__(text, parent)

        self.setMinimumHeight(44)
        self.setCursor(Qt.PointingHandCursor)

        self._normal_pos = QPoint()

        # -----------------------------
        # سایه‌ی سه‌بعدی
        # -----------------------------

        self._shadow = QGraphicsDropShadowEffect(self)

        self._shadow.setBlurRadius(14)
        self._shadow.setOffset(0, 4)
        self._shadow.setColor(Qt.black)

        self.setGraphicsEffect(self._shadow)

        # -----------------------------
        # انیمیشن حرکت
        # -----------------------------

        self._animation = QPropertyAnimation(
            self,
            b"pos",
            self
        )

        self._animation.setDuration(120)
        self._animation.setEasingCurve(
            QEasingCurve.OutCubic
        )

        # -----------------------------
        # ظاهر دکمه
        # -----------------------------

        self.setStyleSheet("""
            QPushButton {
                background-color: rgb(43, 43, 43);
                color: white;

                border-top: 1px solid rgb(85, 85, 85);
                border-left: 1px solid rgb(70, 70, 70);
                border-right: 1px solid rgb(25, 25, 25);
                border-bottom: 2px solid rgb(20, 20, 20);

                border-radius: 10px;

                padding: 8px 16px;

                font-size: 14px;
                font-weight: 600;
            }

            QPushButton:hover {
                background-color: rgb(43, 43, 43);

                border-top: 1px solid rgb(105, 105, 105);
                border-left: 1px solid rgb(80, 80, 80);
                border-right: 1px solid rgb(25, 25, 25);
                border-bottom: 2px solid rgb(15, 15, 15);
            }

            QPushButton:pressed {
                background-color: rgb(43, 43, 43);

                border-top: 2px solid rgb(20, 20, 20);
                border-left: 1px solid rgb(35, 35, 35);
                border-right: 1px solid rgb(35, 35, 35);
                border-bottom: 1px solid rgb(65, 65, 65);
            }

            QPushButton:disabled {
                background-color: rgb(43, 43, 43);
                color: rgb(120, 120, 120);

                border-top: 1px solid rgb(55, 55, 55);
                border-left: 1px solid rgb(50, 50, 50);
                border-right: 1px solid rgb(40, 40, 40);
                border-bottom: 1px solid rgb(35, 35, 35);
            }
        """)

    # -----------------------------
    # ذخیره موقعیت اولیه
    # -----------------------------

    def showEvent(self, event):
        super().showEvent(event)

        if self._normal_pos.isNull():
            self._normal_pos = self.pos()

    # -----------------------------
    # فشرده شدن
    # -----------------------------

    def mousePressEvent(self, event):

        if event.button() == Qt.LeftButton:

            self._normal_pos = self.pos()

            pressed_pos = QPoint(
                self._normal_pos.x(),
                self._normal_pos.y() + 2
            )

            self._animation.stop()

            self._animation.setDuration(100)

            self._animation.setEasingCurve(
                QEasingCurve.OutCubic
            )

            self._animation.setStartValue(
                self.pos()
            )

            self._animation.setEndValue(
                pressed_pos
            )

            self._animation.start()

            # کاهش سایه هنگام فشردن
            self._shadow.setBlurRadius(7)
            self._shadow.setOffset(0, 1)

        super().mousePressEvent(event)

    # -----------------------------
    # برگشت نرم
    # -----------------------------

    def mouseReleaseEvent(self, event):

        super().mouseReleaseEvent(event)

        self._animation.stop()

        self._animation.setDuration(190)

        self._animation.setEasingCurve(
            QEasingCurve.OutBack
        )

        self._animation.setStartValue(
            self.pos()
        )

        self._animation.setEndValue(
            self._normal_pos
        )

        self._animation.start()

        # بازگرداندن سایه
        self._shadow.setBlurRadius(14)
        self._shadow.setOffset(0, 4)


class ActionButtons(QWidget):

    def __init__(self):
        super().__init__()

        layout = QHBoxLayout(self)

        layout.setContentsMargins(
            0, 0, 0, 0
        )

        layout.setSpacing(10)

        self.add_btn = AnimatedButton(
            "➕ ثبت"
        )

        self.edit_btn = AnimatedButton(
            "✏ ویرایش"
        )

        self.delete_btn = AnimatedButton(
            "🗑 حذف"
        )

        self.cottage_btn = AnimatedButton(
            "🏡 وضعیت اجاره کلبه‌ها"
        )

        self.images_btn = AnimatedButton(
            "📷 مدارک"
        )

        buttons = [
            self.add_btn,
            self.edit_btn,
            self.delete_btn,
            self.cottage_btn,
            self.images_btn
        ]

        for btn in buttons:
            layout.addWidget(btn)