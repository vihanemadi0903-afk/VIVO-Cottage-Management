from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent, QKeySequence
from PySide6.QtWidgets import QLineEdit


class MoneyLineEdit(QLineEdit):
    """
    فیلد اختصاصی ورود مبلغ برای VIVO.

    امکانات:
    - پذیرش اعداد
    - جداکننده هزارگان به صورت لحظه‌ای
    - حفظ موقعیت Cursor
    - پشتیبانی از Paste
    - Backspace و Delete طبیعی
    - دریافت مقدار واقعی با value()
    - تنظیم مقدار با setValue()
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAlignment(Qt.AlignCenter)
        self.setPlaceholderText("0")

        # جلوگیری از اجرای دوباره فرمت هنگام setText
        self._formatting = False

        self.textEdited.connect(self._on_text_edited)

    # --------------------------------------------------
    # تبدیل اعداد فارسی و عربی به انگلیسی
    # --------------------------------------------------

    @staticmethod
    def _normalize_digits(text: str) -> str:

        translation_table = str.maketrans({
            "۰": "0",
            "۱": "1",
            "۲": "2",
            "۳": "3",
            "۴": "4",
            "۵": "5",
            "۶": "6",
            "۷": "7",
            "۸": "8",
            "۹": "9",

            "٠": "0",
            "١": "1",
            "٢": "2",
            "٣": "3",
            "٤": "4",
            "٥": "5",
            "٦": "6",
            "٧": "7",
            "٨": "8",
            "٩": "9",
        })

        return text.translate(translation_table)

    # --------------------------------------------------
    # پاک کردن فرمت مبلغ
    # --------------------------------------------------

    def clean_number(self, text: str) -> str:

        text = self._normalize_digits(text)

        # حذف جداکننده‌ها
        text = text.replace(",", "")
        text = text.replace("٬", "")
        text = text.replace("،", "")
        text = text.replace(" ", "")

        # فقط اعداد
        return "".join(
            character
            for character in text
            if character.isdigit()
        )

    # --------------------------------------------------
    # فرمت مبلغ
    # --------------------------------------------------

    def format_number(self, text: str) -> str:

        clean = self.clean_number(text)

        if not clean:
            return ""

        try:
            return f"{int(clean):,}"

        except (ValueError, TypeError):
            return ""

    # --------------------------------------------------
    # تعداد اعداد قبل از Cursor
    # --------------------------------------------------

    def _digits_before_cursor(
        self,
        text: str,
        cursor_position: int
    ) -> int:

        part = text[:cursor_position]

        part = self._normalize_digits(part)

        return sum(
            1
            for character in part
            if character.isdigit()
        )

    # --------------------------------------------------
    # پیدا کردن موقعیت جدید Cursor
    # --------------------------------------------------

    @staticmethod
    def _cursor_position_for_digit_count(
        formatted_text: str,
        digit_count: int
    ) -> int:

        if digit_count <= 0:
            return 0

        seen = 0

        for index, character in enumerate(formatted_text):

            if character.isdigit():

                seen += 1

                if seen == digit_count:
                    return index + 1

        return len(formatted_text)

    # --------------------------------------------------
    # تغییر لحظه‌ای متن
    # --------------------------------------------------

    def _on_text_edited(self, text: str):

        if self._formatting:
            return

        old_cursor = self.cursorPosition()

        digits_before = self._digits_before_cursor(
            text,
            old_cursor
        )

        formatted = self.format_number(text)

        new_cursor = self._cursor_position_for_digit_count(
            formatted,
            digits_before
        )

        self._formatting = True

        self.setText(formatted)

        self.setCursorPosition(new_cursor)

        self._formatting = False

    # --------------------------------------------------
    # دریافت مقدار واقعی
    # --------------------------------------------------

    def value(self) -> int:

        clean = self.clean_number(
            self.text()
        )

        if not clean:
            return 0

        try:
            return int(clean)

        except ValueError:
            return 0

    # --------------------------------------------------
    # قرار دادن مقدار
    # --------------------------------------------------

    def setValue(self, value):

        if value is None or value == "":
            self.clear()
            return

        try:
            value = int(value)

        except (ValueError, TypeError):
            value = 0

        self._formatting = True

        self.setText(
            f"{value:,}"
        )

        self.setCursorPosition(
            len(self.text())
        )

        self._formatting = False

    # --------------------------------------------------
    # جلوگیری از وارد شدن کاراکترهای غیرعددی
    # --------------------------------------------------

    def keyPressEvent(self, event: QKeyEvent):

        # میانبرهای استاندارد ویندوز
        if event.matches(
            QKeySequence.Copy
        ):
            super().keyPressEvent(event)
            return

        if event.matches(
            QKeySequence.Paste
        ):
            super().keyPressEvent(event)
            return

        if event.matches(
            QKeySequence.Cut
        ):
            super().keyPressEvent(event)
            return

        if event.matches(
            QKeySequence.SelectAll
        ):
            super().keyPressEvent(event)
            return

        key = event.key()

        # کلیدهای کنترلی
        allowed_keys = (
            Qt.Key_Backspace,
            Qt.Key_Delete,
            Qt.Key_Left,
            Qt.Key_Right,
            Qt.Key_Home,
            Qt.Key_End,
            Qt.Key_Tab,
            Qt.Key_Return,
            Qt.Key_Enter,
        )

        if key in allowed_keys:
            super().keyPressEvent(event)
            return

        text = event.text()

        normalized = self._normalize_digits(text)

        # فقط عدد
        if normalized.isdigit():

            # اگر فارسی تایپ شد، نسخه انگلیسی وارد شود
            if normalized != text:

                cursor = self.cursorPosition()

                current = self.text()

                selection_start = self.selectionStart()

                if self.hasSelectedText():

                    selected_length = len(
                        self.selectedText()
                    )

                    current = (
                        current[:selection_start]
                        + normalized
                        + current[
                            selection_start
                            + selected_length:
                        ]
                    )

                    self.setText(current)

                    self.setCursorPosition(
                        selection_start
                        + len(normalized)
                    )

                    self._on_text_edited(
                        self.text()
                    )

                else:

                    current = (
                        current[:cursor]
                        + normalized
                        + current[cursor:]
                    )

                    self.setText(current)

                    self.setCursorPosition(
                        cursor
                        + len(normalized)
                    )

                    self._on_text_edited(
                        self.text()
                    )

                return

            super().keyPressEvent(event)
            return

        # بقیه کاراکترها وارد نشوند
        event.ignore()