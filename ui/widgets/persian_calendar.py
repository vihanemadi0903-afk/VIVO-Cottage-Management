import jdatetime
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout
)


class PersianCalendarWidget(QWidget):

    dateSelected = Signal(str)

    def __init__(self):

        super().__init__()

        today = jdatetime.date.today()

        self.current_year = today.year
        self.current_month = today.month

        self.today = today

        self.selected_day = None

        self.day_buttons = {}

        self.build_ui()

        self.refresh_calendar()

    def build_ui(self):
        self.main_layout = QVBoxLayout(self)

        self.main_layout.setSpacing(12)

        self.main_layout.setContentsMargins(
            12, 12, 12, 12
        )

        # =====================================================
        # Header
        # =====================================================

        header = QHBoxLayout()

        # ◀ = ماه بعد
        self.next_btn = QPushButton("◀")

        self.title = QLabel()

        self.title.setAlignment(Qt.AlignCenter)

        self.title.setFont(
            QFont("Tahoma", 12, QFont.Bold)
        )

        # ▶ = ماه قبل
        self.prev_btn = QPushButton("▶")

        self.next_btn.setFixedSize(
            40,
            35
        )

        self.prev_btn.setFixedSize(
            40,
            35
        )

        header.addWidget(
            self.next_btn
        )

        header.addWidget(
            self.title,
            1
        )

        header.addWidget(
            self.prev_btn
        )

        self.main_layout.addLayout(
            header
        )

        # =====================================================
        # روزهای هفته
        #
        # در تقویم فارسی:
        #
        # جمعه ← سمت چپ
        # ...
        # شنبه ← سمت راست
        #
        # بنابراین از چپ به راست:
        # جمعه، پنجشنبه، چهارشنبه، سه‌شنبه،
        # دوشنبه، یکشنبه، شنبه
        # =====================================================

        week_layout = QGridLayout()

        week_layout.setSpacing(5)

        week_days = [
            "ج",
            "پ",
            "چ",
            "س",
            "د",
            "ی",
            "ش"
        ]

        for i, text in enumerate(week_days):

            lbl = QLabel(text)

            lbl.setAlignment(
                Qt.AlignCenter
            )

            lbl.setFont(
                QFont(
                    "Tahoma",
                    10,
                    QFont.Bold
                )
            )

            # جمعه
            if text == "ج":
                lbl.setStyleSheet(
                    "color:#D32F2F;"
                )

            week_layout.addWidget(
                lbl,
                0,
                i
            )

        self.main_layout.addLayout(
            week_layout
        )

        # =====================================================
        # روزهای ماه
        # =====================================================

        self.days_layout = QGridLayout()

        self.days_layout.setSpacing(5)

        self.main_layout.addLayout(
            self.days_layout
        )

        # =====================================================
        # دکمه‌های پایین
        # =====================================================

        bottom = QHBoxLayout()

        self.today_btn = QPushButton(
            "امروز"
        )

        self.cancel_btn = QPushButton(
            "انصراف"
        )

        self.ok_btn = QPushButton(
            "تأیید"
        )

        bottom.addWidget(
            self.today_btn
        )

        bottom.addStretch()

        bottom.addWidget(
            self.cancel_btn
        )

        bottom.addWidget(
            self.ok_btn
        )

        self.main_layout.addLayout(
            bottom
        )

        # =====================================================
        # اتصال دکمه‌ها
        # =====================================================

        # ◀ در تقویم فارسی = ماه بعد
        self.next_btn.clicked.connect(
            self.next_month
        )

        # ▶ در تقویم فارسی = ماه قبل
        self.prev_btn.clicked.connect(
            self.previous_month
        )

        self.today_btn.clicked.connect(
            self.goto_today
        )

        self.ok_btn.clicked.connect(
            self.accept_date
        )

        self.cancel_btn.clicked.connect(
            self.cancel_selection
        )

        
    def clear_days(self):

        while self.days_layout.count():

            item = self.days_layout.takeAt(0)

            if item.widget():
                item.widget().deleteLater()

        self.day_buttons.clear()

    def refresh_calendar(self):

        months = [
            "فروردین",
            "اردیبهشت",
            "خرداد",
            "تیر",
            "مرداد",
            "شهریور",
            "مهر",
            "آبان",
            "آذر",
            "دی",
            "بهمن",
            "اسفند"
        ]

        self.title.setText(
            f"{months[self.current_month - 1]} "
            f"{self.current_year}"
        )

        self.build_days()

    def build_days(self):

        self.clear_days()

        days_in_month = self.get_days_in_month(
            self.current_year,
            self.current_month
        )

        first_weekday = self.get_first_weekday(
            self.current_year,
            self.current_month
        )

        # -----------------------------------------------------
        # تقویم فارسی:
        #
        # ستون 0 = جمعه   ← سمت چپ
        # ستون 6 = شنبه   ← سمت راست
        #
        # بنابراین موقعیت روز اول ماه را معکوس می‌کنیم.
        # -----------------------------------------------------

        first_weekday = 6 - first_weekday

        row = 0
        col = first_weekday

        for day in range(1, days_in_month + 1):

            button = QPushButton(str(day))

            button.setFixedSize(
                45,
                45
            )

            button.setCursor(
                Qt.PointingHandCursor
            )

            button.setFont(
                QFont(
                    "Tahoma",
                    10
                )
            )

            # -------------------------------------------------
            # اطلاعات خود روز
            # -------------------------------------------------

            button.day = day

            button.is_today = (
                    self.today.year == self.current_year
                    and
                    self.today.month == self.current_month
                    and
                    self.today.day == day
            )

            # بعد از معکوس شدن ستون‌ها:
            # col == 0 یعنی جمعه
            button.is_friday = (
                    col == 0
            )

            button.is_selected = (
                    self.selected_day == day
            )

            # -------------------------------------------------
            # کلیک معمولی
            # -------------------------------------------------

            button.clicked.connect(
                lambda checked=False, d=day:
                self.select_day(d)
            )

            # -------------------------------------------------
            # دابل کلیک
            # -------------------------------------------------

            button.mouseDoubleClickEvent = (
                lambda event, d=day:
                self.double_click_day(
                    event,
                    d
                )
            )

            # -------------------------------------------------
            # ذخیره دکمه
            # -------------------------------------------------

            self.day_buttons[day] = button

            # -------------------------------------------------
            # قرار دادن در تقویم
            # -------------------------------------------------

            self.days_layout.addWidget(
                button,
                row,
                col
            )

            # -------------------------------------------------
            # رفتن به روز بعد
            # -------------------------------------------------

            col -= 1

            # وقتی از سمت چپ تقویم خارج شدیم،
            # به ردیف بعدی می‌رویم و دوباره از سمت راست
            # یعنی شنبه شروع می‌کنیم.
            if col < 0:
                col = 6

                row += 1

        # -----------------------------------------------------
        # اعمال رنگ‌ها و وضعیت‌ها
        # -----------------------------------------------------

        self.refresh_styles()

        
    def previous_month(self):

        self.selected_day = None

        if self.current_month == 1:

            self.current_month = 12
            self.current_year -= 1

        else:

            self.current_month -= 1

        self.refresh_calendar()

    def next_month(self):

        self.selected_day = None

        if self.current_month == 12:

            self.current_month = 1
            self.current_year += 1

        else:

            self.current_month += 1

        self.refresh_calendar()


    def refresh_styles(self):

        for day, button in self.day_buttons.items():
            self.update_button_style(button)

    def update_button_style(self, button):

        # ---------- انتخاب شده ----------

        if button.is_selected:
            button.setStyleSheet("""
            QPushButton{

                background:#2196F3;

                color:white;

                border:2px solid #1976D2;

                border-radius:10px;

                font-weight:bold;

            }

            QPushButton:hover{

                background:#42A5F5;

            }

            """)
            return

        # ---------- امروز ----------

        if button.is_today:
            button.setStyleSheet("""
            QPushButton{

                background:#4CAF50;

                color:white;

                border:2px solid #388E3C;

                border-radius:10px;

                font-weight:bold;

            }

            QPushButton:hover{

                background:#66BB6A;

            }

            """)
            return

        # ---------- جمعه ----------

        if button.is_friday:
            button.setStyleSheet("""
            QPushButton{

                background:white;

                color:#D32F2F;

                border:1px solid #D0D0D0;

                border-radius:10px;

                font-weight:bold;

            }

            QPushButton:hover{

                background:#FFEBEE;

            }

            """)
            return

        # ---------- روز عادی ----------

        button.setStyleSheet("""
        QPushButton{

            background:white;

            color:black;

            border:1px solid #D0D0D0;

            border-radius:10px;

        }

        QPushButton:hover{

            background:#E3F2FD;

        }

        QPushButton:pressed{

            background:#BBDEFB;

        }

        """)

    def select_day(self, day):

        # حذف انتخاب قبلی

        if self.selected_day is not None:

            old = self.day_buttons.get(self.selected_day)

            if old:
                old.is_selected = False

        # انتخاب جدید

        self.selected_day = day

        new = self.day_buttons.get(day)

        if new:
            new.is_selected = True

        self.refresh_styles()

    def goto_today(self):

        self.today = jdatetime.date.today()

        self.current_year = self.today.year
        self.current_month = self.today.month

        self.selected_day = None

        self.refresh_calendar()


    def cancel_selection(self):

        self.selected_day = None

        self.window().reject()

    def accept_date(self):

        if self.selected_day is None:
            return

        date = jdatetime.date(
            self.current_year,
            self.current_month,
            self.selected_day
        )

        self.dateSelected.emit(
            date.strftime("%Y/%m/%d")
        )

        self.window().accept()


    def accept_after_click(self, day):

        self.select_day(day)

    def get_days_in_month(self, year, month):

        if month <= 6:
            return 31

        if month <= 11:
            return 30

        # اسفند
        if jdatetime.date(year, 1, 1).isleap():
            return 30

        return 29

    def get_first_weekday(self, year, month):

        first_day = jdatetime.date(
            year,
            month,
            1
        )

        # jdatetime.weekday():
        # Monday = 0
        # ...
        # Sunday = 6
        #
        # در تقویم ما:
        # شنبه = 0
        # یکشنبه = 1
        # ...
        # جمعه = 6

        return (first_day.weekday() + 2) % 7

    def double_click_day(self, event, day):

        self.select_day(day)

        self.accept_date()

