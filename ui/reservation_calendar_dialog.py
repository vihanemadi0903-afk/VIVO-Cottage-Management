import jdatetime
from core.customer_controller import CustomerController
from PySide6.QtCore import (
    Qt,
    QPropertyAnimation,
    QEasingCurve,
)
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QGridLayout,
    QFrame,
)
from ui.widgets.reservation_day_widget import ReservationDayWidget


class ReservationCalendarDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("تقویم رزرو کلبه‌ها")
        self.setFixedSize(950, 820)

        today = jdatetime.date.today()

        self.year = today.year
        self.month = today.month

        self.selected_cottage = None

        self.customer_controller = CustomerController()
        self.cottage_reservations = []
        self.animation = None

        self.build_ui()
        self.update_calendar()

    # ==================================================
    # رابط کاربری
    # ==================================================

    def build_ui(self):

        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(
            25, 25, 25, 25
        )

        main_layout.setSpacing(15)

        # ==================================================
        # نوار بالایی
        # ==================================================

        header_layout = QHBoxLayout()

        header_layout.setContentsMargins(
            5, 5, 5, 5
        )

        # ----------------------------------------------
        # فلش سمت چپ = ماه بعد
        # ----------------------------------------------

        self.next_button = QPushButton("‹")

        self.next_button.setFixedSize(
            55,
            45
        )

        self.next_button.setCursor(
            Qt.PointingHandCursor
        )

        self.next_button.setFont(
            QFont("Arial", 32, QFont.Bold)
        )

        self.next_button.setToolTip(
            "ماه بعد"
        )

        self.next_button.clicked.connect(
            self.next_month
        )

        # ----------------------------------------------
        # عنوان ماه
        # ----------------------------------------------

        self.month_label = QLabel()

        self.month_label.setAlignment(
            Qt.AlignCenter
        )

        self.month_label.setFont(
            QFont(
                "Tahoma",
                18,
                QFont.Bold
            )
        )

        # ----------------------------------------------
        # فلش سمت راست = ماه قبل
        # ----------------------------------------------

        self.previous_button = QPushButton("›")

        self.previous_button.setFixedSize(
            55,
            45
        )

        self.previous_button.setCursor(
            Qt.PointingHandCursor
        )

        self.previous_button.setFont(
            QFont("Arial", 32, QFont.Bold)
        )

        self.previous_button.setToolTip(
            "ماه قبل"
        )

        self.previous_button.clicked.connect(
            self.previous_month
        )

        header_layout.addWidget(
            self.next_button
        )

        header_layout.addWidget(
            self.month_label,
            1
        )

        header_layout.addWidget(
            self.previous_button
        )

        main_layout.addLayout(
            header_layout
        )

        # ==================================================
        # روزهای هفته
        # ==================================================

        self.week_layout = QGridLayout()

        self.week_layout.setSpacing(4)

        # از راست به چپ:
        # شنبه → ... → جمعه

        week_names = [
            "شنبه",
            "یکشنبه",
            "دوشنبه",
            "سه‌شنبه",
            "چهارشنبه",
            "پنجشنبه",
            "جمعه",
        ]

        for column, name in enumerate(
            week_names
        ):

            label = QLabel(name)

            label.setAlignment(
                Qt.AlignCenter
            )

            label.setFont(
                QFont(
                    "Tahoma",
                    10,
                    QFont.Bold
                )
            )

            self.week_layout.addWidget(
                label,
                0,
                6 - column
            )

        main_layout.addLayout(
            self.week_layout
        )

        # ==================================================
        # جدول روزهای ماه
        # ==================================================

        self.days_frame = QFrame()

        self.days_layout = QGridLayout(
            self.days_frame
        )

        self.days_layout.setSpacing(5)

        main_layout.addWidget(
            self.days_frame,
            1
        )

        # ==================================================
        # دکمه امروز
        # ==================================================

        self.today_button = QPushButton(
            "امروز"
        )

        self.today_button.setFixedHeight(
            40
        )

        self.today_button.clicked.connect(
            self.go_to_today
        )

        main_layout.addWidget(
            self.today_button
        )

        # ==================================================
        # انتخاب کلبه
        # ==================================================

        self.cottage_layout = QGridLayout()

        self.cottage_layout.setSpacing(6)

        self.cottage_buttons = []

        for cottage_number in range(1, 17):
            button = QPushButton(
                f"کلبه {cottage_number}"
            )

            button.setFixedHeight(38)

            button.setCursor(
                Qt.PointingHandCursor
            )

            button.clicked.connect(
                lambda checked=False,
                       number=cottage_number:
                self.select_cottage(number)
            )

            self.cottage_buttons.append(
                button
            )

            # 8 دکمه در هر ردیف
            row = (cottage_number - 1) // 8
            column = 7 - (
                    (cottage_number - 1) % 8
            )

            self.cottage_layout.addWidget(
                button,
                row,
                column
            )

        main_layout.addLayout(
            self.cottage_layout
        )

        # ==================================================
        # ظاهر
        # ==================================================

        self.setStyleSheet(
            """
            QDialog {
                background-color: rgb(35, 35, 35);
                color: white;
            }

            QLabel {
                color: white;
            }

            QPushButton {
                background-color: rgb(43, 43, 43);
                color: white;

                border: 1px solid rgb(65, 65, 65);
                border-radius: 8px;

                font-size: 14px;
                font-weight: 600;
            }

            QPushButton:hover {
                background-color: rgb(43, 43, 43);
                border: 1px solid rgb(90, 90, 90);
            }

            QPushButton:pressed {
                background-color: rgb(43, 43, 43);
            }
            """
        )

    # ==================================================
    # ساخت تقویم
    # ==================================================

    def update_calendar(self):

        # ==================================================
        # حذف روزهای قبلی
        # ==================================================

        while self.days_layout.count():

            item = self.days_layout.takeAt(0)

            widget = item.widget()

            if widget:
                widget.deleteLater()

        # ==================================================
        # نام ماه‌های شمسی
        # ==================================================

        month_names = [
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
            "اسفند",
        ]

        # ==================================================
        # عنوان ماه
        # ==================================================

        self.month_label.setText(
            f"{month_names[self.month - 1]} {self.year}"
        )

        # ==================================================
        # تعداد روزهای ماه
        # ==================================================

        if self.month <= 6:

            days_in_month = 31

        elif self.month <= 11:

            days_in_month = 30

        else:

            # سال کبیسه شمسی
            if jdatetime.j_days_in_month[11] == 30:
                days_in_month = 30
            else:
                days_in_month = 29

        # ==================================================
        # روز اول ماه
        # ==================================================

        first_day = jdatetime.date(
            self.year,
            self.month,
            1
        )

        # jdatetime:
        # شنبه = 0
        # یکشنبه = 1
        # دوشنبه = 2
        # سه‌شنبه = 3
        # چهارشنبه = 4
        # پنجشنبه = 5
        # جمعه = 6

        start_day = first_day.weekday()

        # ==================================================
        # تاریخ امروز
        # ==================================================

        today = jdatetime.date.today()

        # ==================================================
        # ساخت کارت‌های روز
        # ==================================================

        for day in range(
                1,
                days_in_month + 1
        ):
            # ----------------------------------------------
            # تعیین موقعیت روز در تقویم
            # ----------------------------------------------

            position = (
                    start_day + day - 1
            )

            row = (
                          position // 7
                  ) + 1

            column = 6 - (
                    position % 7
            )

            # ----------------------------------------------
            # بررسی امروز
            # ----------------------------------------------

            is_today = (
                    self.year == today.year
                    and
                    self.month == today.month
                    and
                    day == today.day
            )

            # ----------------------------------------------
            # ساخت Widget روز
            # ----------------------------------------------

            day_widget = ReservationDayWidget(
                day=day,
                is_today=is_today
            )

            # ----------------------------------------------
            # دریافت رزروهای مربوط به این روز
            # ----------------------------------------------

            day_reservations = self.get_day_reservations(
                self.year,
                self.month,
                day
            )

            # ----------------------------------------------
            # نمایش رزروها
            # ----------------------------------------------

            day_widget.set_reservations(
                day_reservations
            )

            # ----------------------------------------------
            # اضافه کردن کارت به تقویم
            # ----------------------------------------------

            self.days_layout.addWidget(
                day_widget,
                row,
                column
            )

    # ==================================================
    # انیمیشن تغییر ماه
    # ==================================================

    def animate_month_change(self):

        self.month_label.setWindowOpacity(
            0.0
        )

        self.animation = QPropertyAnimation(
            self.month_label,
            b"windowOpacity",
            self
        )

        self.animation.setDuration(
            220
        )

        self.animation.setStartValue(
            0.0
        )

        self.animation.setEndValue(
            1.0
        )

        self.animation.setEasingCurve(
            QEasingCurve.OutCubic
        )

        self.animation.start()

    # ==================================================
    # ماه قبل
    # ==================================================

    def previous_month(self):

        self.month -= 1

        if self.month < 1:

            self.month = 12
            self.year -= 1

        self.update_calendar()
        self.animate_month_change()

    # ==================================================
    # ماه بعد
    # ==================================================

    def next_month(self):

        self.month += 1

        if self.month > 12:

            self.month = 1
            self.year += 1

        self.update_calendar()
        self.animate_month_change()

    # ==================================================
    # امروز
    # ==================================================

    def go_to_today(self):

        today = jdatetime.date.today()

        self.year = today.year
        self.month = today.month

        self.update_calendar()
        self.animate_month_change()

    def select_cottage(self, cottage_number):

        self.selected_cottage = cottage_number

        # دریافت رزروهای کلبه انتخاب‌شده
        self.cottage_reservations = (
            self.customer_controller
            .get_cottage_reservations(
                cottage_number
            )
        )

        # مشخص کردن دکمه انتخاب‌شده
        for number, button in enumerate(
                self.cottage_buttons,
                start=1
        ):

            if number == cottage_number:

                button.setStyleSheet(
                    """
                    QPushButton {
                        background-color: rgb(43, 43, 43);
                        color: white;
                        border: 2px solid rgb(100, 150, 255);
                        border-radius: 8px;
                        font-weight: 700;
                    }
                    """
                )

            else:

                button.setStyleSheet(
                    """
                    QPushButton {
                        background-color: rgb(43, 43, 43);
                        color: white;
                        border: 1px solid rgb(65, 65, 65);
                        border-radius: 8px;
                        font-weight: 600;
                    }

                    QPushButton:hover {
                        background-color: rgb(43, 43, 43);
                        border: 1px solid rgb(95, 95, 95);
                    }
                    """
                )

        # بروزرسانی تقویم
        self.update_calendar()

    def get_day_reservations(self, year, month, day):
        """
        رزروهای بصری مربوط به یک روز را برمی‌گرداند.

        منطق نمایش:
            روز ورود     -> نیمه راست کارت
            روزهای وسط   -> کل کارت
            روز خروج     -> نیمه چپ کارت

        توجه:
            این منطق فقط برای نمایش تقویم است
            و منطق اشغال واقعی کلبه را تغییر نمی‌دهد.
        """

        current_date = jdatetime.date(
            year,
            month,
            day
        )

        reservations = []

        # ==================================================
        # 20 رنگ مختلف رزرو
        # ==================================================
        colors = [
            "#3B82F6",  # 01 - آبی
            "#c60d0d",  # 02 - بنفش
            "#3e1d59",  # 03 - سبز زمردی
            "#68ce46",  # 04 - کهربایی
            "#b04ed0",  # 05 - قرمز
            "#FF69B4",  # 06 - صورتی
            "#06B6D4",  # 07 - فیروزه‌ای
            "#6366F1",  # 08 - نیلی
            "#14B8A6",  # 09 - سبز فیروزه‌ای
            "#F97316",  # 10 - نارنجی
            "#A855F7",  # 11 - ارغوانی
            "#22C55E",  # 12 - سبز
            "#0EA5E9",  # 13 - آبی روشن
            "#E11D48",  # 14 - سرخابی تیره
            "#84CC16",  # 15 - سبز لیمویی
            "#D946EF",  # 16 - بنفش صورتی
            "#F43F5E",  # 17 - رز
            "#0D9488",  # 18 - سبز دریایی
            "#CA8A04",  # 19 - طلایی
            "#7C3AED",  # 20 - بنفش عمیق
        ]

        # ==================================================
        # بررسی تمام رزروهای کلبه انتخاب‌شده
        # ==================================================

        for index, reservation in enumerate(
                self.cottage_reservations
        ):

            check_in = reservation.get(
                "check_in",
                ""
            )

            check_out = reservation.get(
                "check_out",
                ""
            )

            if not check_in or not check_out:
                continue

            # ==================================================
            # تبدیل تاریخ‌ها
            # ==================================================

            try:

                start_date = jdatetime.datetime.strptime(
                    check_in,
                    "%Y/%m/%d"
                ).date()

                end_date = jdatetime.datetime.strptime(
                    check_out,
                    "%Y/%m/%d"
                ).date()

            except ValueError:

                continue

            # ==================================================
            # اگر روز خارج از بازه رزرو باشد
            # ==================================================

            if current_date < start_date:
                continue

            if current_date > end_date:
                continue

            # ==================================================
            # تعیین وضعیت بصری روز
            # ==================================================

            if (
                    current_date == start_date
                    and
                    current_date == end_date
            ):

                # ورود و خروج در یک روز
                position = "single"

            elif current_date == start_date:

                # روز ورود
                # نیمه راست کارت
                position = "end"

            elif current_date == end_date:

                # روز خروج
                # نیمه چپ کارت
                position = "start"

            else:

                # روزهای بین ورود و خروج
                # کل کارت
                position = "full"

            # ==================================================
            # ساخت اطلاعات رزرو
            # ==================================================

            reservations.append({

                "id": reservation.get(
                    "id"
                ),

                "full_name": reservation.get(
                    "full_name",
                    ""
                ),

                "check_in": check_in,

                "check_out": check_out,

                # رنگ اختصاصی این رزرو
                "color": colors[
                    index % len(colors)
                    ],

                "position": position
            })

        return reservations


