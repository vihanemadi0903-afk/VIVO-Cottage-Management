from PySide6.QtCore import (
    Qt,
    QPropertyAnimation,
    QEasingCurve,
    QPoint
)

from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QPushButton
)


class AnimatedButton(QPushButton):

    def __init__(self, text, parent=None):
        super().__init__(text, parent)

        self.setMinimumHeight(44)
        self.setCursor(Qt.PointingHandCursor)

        self._normal_pos = QPoint()

        # انیمیشن حرکت
        self._animation = QPropertyAnimation(
            self,
            b"pos",
            self
        )

        self._animation.setDuration(120)
        self._animation.setEasingCurve(
            QEasingCurve.OutCubic
        )

        self.setStyleSheet("""
            QPushButton {
                background-color: rgb(43, 43, 43);
                color: white;

                border: 1px solid rgb(65, 65, 65);
                border-radius: 10px;

                padding: 8px 16px;

                font-size: 14px;
                font-weight: 600;
            }

            QPushButton:hover {
                background-color: rgb(43, 43, 43);
                border: 1px solid rgb(85, 85, 85);
            }

            QPushButton:pressed {
                background-color: rgb(43, 43, 43);
            }

            QPushButton:disabled {
                background-color: rgb(43, 43, 43);
                color: rgb(120, 120, 120);
                border-color: rgb(55, 55, 55);
            }
        """)

    def showEvent(self, event):
        super().showEvent(event)

        if self._normal_pos.isNull():
            self._normal_pos = self.pos()

    def mousePressEvent(self, event):

        if event.button() == Qt.LeftButton:

            self._normal_pos = self.pos()

            pressed_pos = QPoint(
                self._normal_pos.x(),
                self._normal_pos.y() + 2
            )

            self._animation.stop()

            self._animation.setDuration(90)
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

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):

        super().mouseReleaseEvent(event)

        self._animation.stop()

        self._animation.setDuration(160)
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


class ActionButtons(QWidget):

    def __init__(self):
        super().__init__()

        layout = QHBoxLayout(self)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.add_btn = AnimatedButton("➕ ثبت")

        self.edit_btn = AnimatedButton("✏ ویرایش")

        self.delete_btn = AnimatedButton("🗑 حذف")

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