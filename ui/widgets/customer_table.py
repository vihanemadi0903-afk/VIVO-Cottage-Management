from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QHeaderView,
    QAbstractItemView
)
from PySide6.QtCore import Qt

class CustomerTable(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        self.table = QTableWidget()

        # تعداد ستون ها
        self.table.setColumnCount(8)

        # عنوان ستون ها
        self.table.setHorizontalHeaderLabels([
            "ID",
            "نام و نام خانوادگی",
            "شماره تماس",
            "شماره کلبه",
            "تاریخ ورود",
            "تاریخ خروج",
            "وضعیت",
            "مدارک"
        ])

        # مخفی کردن شناسه
        self.table.setColumnHidden(0, True)

        # اندازه ستون ها
        header = self.table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignCenter)

        # همه ستون‌ها اندازه ثابت داشته باشند
        for i in range(1, 8):
            header.setSectionResizeMode(i, QHeaderView.Fixed)

        # فقط آخرین ستون (مدارک) فضای اضافه را پر کند
        header.setStretchLastSection(True)

        self.table.setColumnWidth(1, 290)  # نام و نام خانوادگی
        self.table.setColumnWidth(2, 165)  # شماره تماس
        self.table.setColumnWidth(3, 100)  # شماره کلبه
        self.table.setColumnWidth(4, 120)  # تاریخ ورود
        self.table.setColumnWidth(5, 120)  # تاریخ خروج
        self.table.setColumnWidth(6, 100)  # وضعیت
        # برای ستون مدارک عرض تعیین نکن؛ چون خودش فضای باقی‌مانده را پر می‌کند. # مدارک

        # انتخاب کامل ردیف
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        self.table.setSelectionMode(
            QAbstractItemView.SingleSelection
        )

        self.table.setFocusPolicy(Qt.NoFocus)

        # جلوگیری از ویرایش مستقیم
        self.table.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        # ظاهر جدول
        self.table.setAlternatingRowColors(True)

        self.table.setShowGrid(True)

        self.table.verticalHeader().setVisible(False)

        self.table.verticalHeader().setDefaultSectionSize(42)

        self.table.horizontalHeader().setFixedHeight(42)

        layout.addWidget(self.table)

