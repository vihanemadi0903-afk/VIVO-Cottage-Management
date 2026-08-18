from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import (
    QFont,
    QColor,
    QPainter,
    QPen,
)
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal

class ReservationDayWidget(QWidget):
    reservation_double_clicked = Signal(object)
    empty_double_clicked = Signal(int)

    def __init__(
        self,
        day,
        is_today=False,
        parent=None
    ):
        super().__init__(parent)

        self.day = day
        self.is_today = is_today

        # رزروهای مربوط به این روز
        self.reservations = []

        self.setMinimumSize(
            90,
            80
        )

        self.setCursor(
            Qt.PointingHandCursor
        )
        self.setMouseTracking(True)

    # ==================================================
    # دریافت رنگ بر اساس شماره رزرو
    # ==================================================

    @classmethod
    def get_reservation_color(
        cls,
        reservation_index
    ):
        """
        دریافت یکی از 20 رنگ رزرو.

        اگر تعداد رزروها بیشتر از 20 شود،
        رنگ‌ها دوباره از ابتدا استفاده می‌شوند.
        """

        return cls.RESERVATION_COLORS[
            reservation_index
            % len(cls.RESERVATION_COLORS)
        ]

    # ==================================================
    # تنظیم رزروهای روز
    # ==================================================

    def set_reservations(
        self,
        reservations
    ):

        self.reservations = (
            reservations or []
        )

        # اگر رزرو رنگ نداشته باشد،
        # به صورت خودکار رنگ دریافت می‌کند.

        for index, reservation in enumerate(
            self.reservations
        ):

            if not reservation.get("color"):

                reservation["color"] = (
                    self.get_reservation_color(index)
                )

        self.update()

    # ==================================================
    # پاک کردن رزروها
    # ==================================================

    def clear_reservations(self):

        self.reservations = []

        self.update()

    # ==================================================
    # رسم کارت
    # ==================================================

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        rect = self.rect().adjusted(
            1,
            1,
            -1,
            -1
        )

        # ------------------------------------------------
        # رنگ پیش‌فرض کارت
        # ------------------------------------------------

        default_color = QColor(
            43,
            43,
            43
        )

        border_color = QColor(
            65,
            65,
            65
        )

        painter.setBrush(
            default_color
        )

        painter.setPen(
            QPen(
                border_color,
                1
            )
        )

        painter.drawRoundedRect(
            rect,
            8,
            8
        )

        # ------------------------------------------------
        # محدوده داخلی
        # ------------------------------------------------

        inner = rect.adjusted(
            2,
            2,
            -2,
            -2
        )

        # ------------------------------------------------
        # رسم رزرو
        # ------------------------------------------------

        if self.reservations:

            if len(self.reservations) == 1:

                reservation = (
                    self.reservations[0]
                )

                self.draw_reservation(
                    painter,
                    inner,
                    reservation
                )

            else:

                # ----------------------------------------
                # حداکثر دو رزرو در یک روز
                # ----------------------------------------

                left_reservation = None
                right_reservation = None

                for reservation in self.reservations:

                    position = reservation.get(
                        "position",
                        "full"
                    )

                    if position == "end":

                        left_reservation = (
                            reservation
                        )

                    elif position == "start":

                        right_reservation = (
                            reservation
                        )

                # ----------------------------------------
                # نیمه چپ
                # ----------------------------------------

                if left_reservation:

                    left_rect = QRect(
                        inner.left(),
                        inner.top(),
                        inner.width() // 2,
                        inner.height()
                    )

                    self.draw_reservation_part(
                        painter,
                        left_rect,
                        left_reservation
                    )

                # ----------------------------------------
                # نیمه راست
                # ----------------------------------------

                if right_reservation:

                    right_rect = QRect(
                        inner.left()
                        + inner.width() // 2,
                        inner.top(),
                        inner.width()
                        - inner.width() // 2,
                        inner.height()
                    )

                    self.draw_reservation_part(
                        painter,
                        right_rect,
                        right_reservation
                    )

        # ------------------------------------------------
        # شماره روز
        # ------------------------------------------------

        day_font = QFont(
            "Tahoma",
            11,
            QFont.Bold
        )

        painter.setFont(
            day_font
        )

        painter.setPen(
            QColor(
                255,
                255,
                255
            )
        )

        day_rect = QRect(
            inner.left(),
            inner.top() + 5,
            inner.width(),
            24
        )

        painter.drawText(
            day_rect,
            Qt.AlignCenter,
            str(self.day)
        )

        # ------------------------------------------------
        # نمایش امروز
        # ------------------------------------------------

        if self.is_today:

            today_font = QFont(
                "Tahoma",
                7,
                QFont.Bold
            )

            painter.setFont(
                today_font
            )

            painter.setPen(
                QColor(
                    190,
                    215,
                    255
                )
            )

            today_rect = QRect(
                inner.left(),
                inner.top() + 27,
                inner.width(),
                16
            )

            painter.drawText(
                today_rect,
                Qt.AlignCenter,
                "امروز"
            )

        painter.end()

    # ==================================================
    # رسم یک رزرو
    # ==================================================

    def draw_reservation(
        self,
        painter,
        rect,
        reservation
    ):

        position = reservation.get(
            "position",
            "full"
        )

        # ----------------------------------------------
        # ورود
        # ----------------------------------------------

        if position == "start":

            reservation_rect = QRect(
                rect.left()
                + rect.width() // 2,
                rect.top(),
                rect.width()
                - rect.width() // 2,
                rect.height()
            )

            self.draw_reservation_part(
                painter,
                reservation_rect,
                reservation
            )

        # ----------------------------------------------
        # خروج
        # ----------------------------------------------

        elif position == "end":

            reservation_rect = QRect(
                rect.left(),
                rect.top(),
                rect.width() // 2,
                rect.height()
            )

            self.draw_reservation_part(
                painter,
                reservation_rect,
                reservation
            )

        # ----------------------------------------------
        # روز کامل
        # ----------------------------------------------

        else:

            self.draw_reservation_part(
                painter,
                rect,
                reservation
            )

    # ==================================================
    # رسم قسمت رنگی رزرو
    # ==================================================

    def draw_reservation_part(
        self,
        painter,
        rect,
        reservation
    ):

        color_value = reservation.get(
            "color",
            "#3B82F6"
        )

        color = QColor(
            color_value
        )

        color.setAlpha(
            225
        )

        # ------------------------------------------------
        # رنگ رزرو
        # ------------------------------------------------

        painter.setBrush(
            color
        )

        painter.setPen(
            Qt.NoPen
        )

        painter.drawRect(
            rect
        )

        # ------------------------------------------------
        # نام مسافر
        # ------------------------------------------------

        full_name = reservation.get(
            "full_name",
            ""
        )

        if not full_name:
            return

        name_font = QFont(
            "Tahoma",
            7,
            QFont.Bold
        )

        painter.setFont(
            name_font
        )

        painter.setPen(
            QColor(
                255,
                255,
                255
            )
        )

        name_rect = QRect(
            rect.left() + 2,
            rect.top() + 38,
            rect.width() - 4,
            rect.height() - 40
        )

        painter.drawText(
            name_rect,
            Qt.AlignCenter
            | Qt.TextWordWrap,
            full_name
        )

    # ==================================================
    # Hover
    # ==================================================

    def enterEvent(self, event):

        self.update()

        super().enterEvent(
            event
        )

    def leaveEvent(self, event):

        self.update()

        super().leaveEvent(
            event
        )


    def mouseDoubleClickEvent(self, event):

        # ============================================
        # مختصات کلیک
        # ============================================

        click_x = event.position().x()

        middle_x = self.width() / 2

        # ============================================
        # اگر هیچ رزروی وجود ندارد
        # ============================================

        if not self.reservations:
            self.empty_double_clicked.emit(
                self.day
            )

            event.accept()
            return

        # ============================================
        # پیدا کردن رزروهای نیمه چپ و راست
        # ============================================

        left_reservation = None
        right_reservation = None
        full_reservation = None

        for reservation in self.reservations:

            position = reservation.get(
                "position",
                "full"
            )

            # -----------------------------
            # رزرو کل روز
            # -----------------------------

            if position == "full":

                full_reservation = reservation

            # -----------------------------
            # نیمه چپ = روز خروج
            # -----------------------------

            elif position == "end":

                left_reservation = reservation

            # -----------------------------
            # نیمه راست = روز ورود
            # -----------------------------

            elif position == "start":

                right_reservation = reservation

        # ============================================
        # اگر کل روز رزرو شده
        # ============================================

        if full_reservation is not None:
            self.reservation_double_clicked.emit(
                full_reservation
            )

            event.accept()
            return

        # ============================================
        # تشخیص نیمه‌ای که کاربر کلیک کرده
        # ============================================

        if click_x < middle_x:

            # ========================================
            # نیمه چپ
            # ========================================

            if left_reservation is not None:

                # این قسمت رزرو شده
                self.reservation_double_clicked.emit(
                    left_reservation
                )

            else:

                # این قسمت آزاد است
                self.empty_double_clicked.emit(
                    self.day
                )

        else:

            # ========================================
            # نیمه راست
            # ========================================

            if right_reservation is not None:

                # این قسمت رزرو شده
                self.reservation_double_clicked.emit(
                    right_reservation
                )

            else:

                # این قسمت آزاد است
                self.empty_double_clicked.emit(
                    self.day
                )

        event.accept()