from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout
)

from ui.widgets.persian_calendar import PersianCalendarWidget


class CalendarDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.selected_date = None

        self.setWindowTitle("انتخاب تاریخ")

        self.resize(420, 430)

        layout = QVBoxLayout(self)

        self.calendar = PersianCalendarWidget()

        layout.addWidget(self.calendar)

        self.calendar.dateSelected.connect(
            self.on_date_selected
        )

    def on_date_selected(self, date):

        self.selected_date = date

        self.accept()

    @staticmethod
    def get_date(parent=None):
        dialog = CalendarDialog(parent)

        if dialog.exec():
            return dialog.selected_date

        return None


