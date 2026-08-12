from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QHeaderView,
    QAbstractItemView
)

from PySide6.QtCore import Qt, Signal


class CustomerTable(QWidget):

    # row, column
    row_double_clicked = Signal(int, int)

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        self.table = QTableWidget()

        # -----------------------------
        # دبل کلیک روی سلول
        # -----------------------------

        self.table.cellDoubleClicked.connect(
            self._handle_double_click
        )

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
            header.setSectionResizeMode(
                i,
                QHeaderView.Fixed
            )

        # فقط آخرین ستون فضای اضافه را پر کند
        header.setStretchLastSection(True)

        self.table.setColumnWidth(1, 290)
        self.table.setColumnWidth(2, 165)
        self.table.setColumnWidth(3, 100)
        self.table.setColumnWidth(4, 120)
        self.table.setColumnWidth(5, 120)
        self.table.setColumnWidth(6, 100)

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

    # =====================================================
    # مدیریت دبل کلیک
    # =====================================================

    def _handle_double_click(self, row, column):

        # اگر روی ردیف واقعی کلیک شده باشد
        if row < 0:
            return

        # ارسال ردیف و ستون به MainWindow
        self.row_double_clicked.emit(
            row,
            column
        )