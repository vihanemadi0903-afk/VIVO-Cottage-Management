from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QPushButton
)


class ActionButtons(QWidget):

    def __init__(self):
        super().__init__()

        layout = QHBoxLayout(self)

        self.add_btn = QPushButton("➕ ثبت")

        self.edit_btn = QPushButton("✏ ویرایش")

        self.delete_btn = QPushButton("🗑 حذف")

        self.cottage_btn = QPushButton("🏡 وضعیت اجاره کلبه‌ها")

        self.images_btn = QPushButton("📷 مدارک")

        buttons = [
            self.add_btn,
            self.edit_btn,
            self.delete_btn,
            self.cottage_btn,
            self.images_btn
        ]

        for btn in buttons:

            btn.setMinimumHeight(42)

            layout.addWidget(btn)