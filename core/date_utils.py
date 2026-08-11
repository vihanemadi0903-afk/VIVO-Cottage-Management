import re
from datetime import date


class DateUtils:

    DATE_PATTERN = re.compile(r"^\d{4}/\d{2}/\d{2}$")

    @staticmethod
    def is_valid_format(date_string: str) -> bool:
        """
        فقط فرمت YYYY/MM/DD را قبول می‌کند.
        مثال:
        1405/05/09 ✅
        1405/5/9 ❌
        """

        if not date_string:
            return False

        return bool(DateUtils.DATE_PATTERN.fullmatch(date_string))

    @staticmethod
    def split_date(date_string):

        year, month, day = date_string.split("/")

        return (
            int(year),
            int(month),
            int(day)
        )

    @staticmethod
    def is_valid_date(date_string):

        if not DateUtils.is_valid_format(date_string):
            return False

        year, month, day = DateUtils.split_date(date_string)

        if month < 1 or month > 12:
            return False

        max_day = DateUtils.days_in_month(year, month)

        if day < 1 or day > max_day:
            return False

        return True

    @staticmethod
    def compare(date1, date2):
        """
        date1 < date2 => -1
        date1 = date2 => 0
        date1 > date2 => 1
        """

        y1, m1, d1 = DateUtils.split_date(date1)
        y2, m2, d2 = DateUtils.split_date(date2)

        a = (y1, m1, d1)
        b = (y2, m2, d2)

        if a < b:
            return -1

        if a > b:
            return 1

        return 0

    @staticmethod
    def is_checkout_after_checkin(
        check_in,
        check_out
    ):

        return (
            DateUtils.compare(
                check_out,
                check_in
            ) >= 0
        )

    @staticmethod
    def gregorian_to_jalali(gy, gm, gd):

        g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]

        if gy > 1600:
            jy = 979
            gy -= 1600
        else:
            jy = 0
            gy -= 621

        if gm > 2:
            gy2 = gy + 1
        else:
            gy2 = gy

        days = (
                365 * gy
                + (gy2 + 3) // 4
                - (gy2 + 99) // 100
                + (gy2 + 399) // 400
                - 80
                + gd
                + g_d_m[gm - 1]
        )

        jy += 33 * (days // 12053)

        days %= 12053

        jy += 4 * (days // 1461)

        days %= 1461

        if days > 365:
            jy += (days - 1) // 365
            days = (days - 1) % 365

        if days < 186:
            jm = 1 + days // 31
            jd = 1 + days % 31
        else:
            jm = 7 + (days - 186) // 30
            jd = 1 + (days - 186) % 30

        return jy, jm, jd

    @staticmethod
    def today():

        t = date.today()

        jy, jm, jd = DateUtils.gregorian_to_jalali(
            t.year,
            t.month,
            t.day
        )

        return f"{jy:04d}/{jm:02d}/{jd:02d}"

    @staticmethod
    def to_number(date_string):

        """
        1405/05/09

        ↓

        14050509
        """

        return int(date_string.replace("/", ""))

    @staticmethod
    def days_in_month(year, month):

        if 1 <= month <= 6:
            return 31

        if 7 <= month <= 11:
            return 30

        if month == 12:

            if DateUtils.is_leap_year(year):
                return 30

            return 29

        return 0

    @staticmethod
    def is_leap_year(year):

        """
        تشخیص سال کبیسه شمسی
        """

        cycle = year % 33

        return cycle in (
            1,
            5,
            9,
            13,
            17,
            22,
            26,
            30
        )



