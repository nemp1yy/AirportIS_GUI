from PyQt6 import uic, QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QDialog
import sys
from PyQt6.QtSql import QSqlDatabase, QSqlTableModel, QSqlQueryModel


class SearchWindow(QDialog):
    search_requested = QtCore.pyqtSignal(str, list)

    def __init__(self, parent=None):
        super().__init__(parent)
        # Загружаем UI файл
        uic.loadUi("gui/design/search.ui", self)
        self.main_window = parent

        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName('data/data.db')
        if not self.db.open():
            print("Не удалось открыть базу данных")
            return False


        self.pushButton.clicked.connect(self.emit_search)
        self.pushButton_2.clicked.connect(self.clearParameters)
        self.pushButton_3.clicked.connect(self.close)

        current_datetime = QtCore.QDateTime.currentDateTime()
        self.dateTimeEdit_departure_time_range1.setDateTime(current_datetime)
        self.dateTimeEdit_departure_time_range2.setDateTime(current_datetime)
        self.dateTimeEdit_arrival_time_range1.setDateTime(current_datetime)
        self.dateTimeEdit_arrival_time_range2.setDateTime(current_datetime)

        for datetime_edit in self.findChildren(QtWidgets.QDateTimeEdit):
            datetime_edit.setCalendarPopup(True)


    def emit_search(self):
        print('Поиск строки')

        flight = self.lineEdit_flight.text().strip()
        airline = self.lineEdit_airline.text().strip()
        departure_from = self.lineEdit_departure_from.text().strip()
        destination = self.lineEdit_destination.text().strip()
        departure_time_range1 = self.dateTimeEdit_departure_time_range1.dateTime().toString("yyyy-MM-dd hh:mm")
        departure_time_range2 = self.dateTimeEdit_departure_time_range2.dateTime().toString("yyyy-MM-dd hh:mm")
        arrival_time_range1 = self.dateTimeEdit_arrival_time_range1.dateTime().toString("yyyy-MM-dd hh:mm")
        arrival_time_range2 = self.dateTimeEdit_arrival_time_range2.dateTime().toString("yyyy-MM-dd hh:mm")
        gate = self.lineEdit_gate.text().strip()
        status = self.comboBox_status.currentText()
        aircraft_type = self.lineEdit_aircraft_type.text().strip()

        sql = "SELECT * FROM flights WHERE 1=1"
        conditions = []

        if flight:
            conditions.append(f"flight LIKE '%{flight}%'")

        if airline:
            conditions.append(f"airline LIKE '%{airline}%'")

        if departure_from:
            conditions.append(f"departure_from LIKE '%{departure_from}%'")

        if destination:
            conditions.append(f"destination LIKE '%{destination}%'")

        if departure_time_range1 and departure_time_range2:
            conditions.append(f"departure_time BETWEEN  '{departure_time_range1}' AND '{departure_time_range2}'")
        elif departure_time_range1:
            conditions.append(f"departure_time >= '{departure_time_range1}'")
        elif departure_time_range2:
            conditions.append(f"departure_time <= '{departure_time_range2}'")

        if arrival_time_range1 and arrival_time_range2:
            conditions.append(f"arrival_time BETWEEN  '{arrival_time_range1}' AND '{arrival_time_range2}'")
        elif arrival_time_range1:
            conditions.append(f"arrival_time >= '{arrival_time_range1}'")
        elif arrival_time_range2:
            conditions.append(f"arrival_time <= '{arrival_time_range2}'")

        if gate:
            conditions.append(f"gate LIKE '%{gate}%'")

        if status != "Все статусы":
            conditions.append(f"status LIKE '%{status}%'")

        if aircraft_type:
            conditions.append(f"aircraft_type LIKE '%{aircraft_type}%'")

        for condition in conditions:
            sql += " AND " + condition

        print("SQL:", sql)

        self.search_requested.emit(sql, [])
        self.close()

    def clearParameters(self):
        """Очистка полей с проверкой существования виджетов"""
        try:
            # Автоматическая очистка всех QLineEdit
            for line_edit in self.findChildren(QtWidgets.QLineEdit):
                line_edit.clear()

            # Очистка QDateTimeEdit
            min_date = QtCore.QDateTime(QtCore.QDate(2000, 1, 1), QtCore.QTime(0, 0))
            for date_edit in self.findChildren(QtWidgets.QDateTimeEdit):
                date_edit.setDateTime(min_date)

                # Если есть QComboBox, сбрасываем на первый элемент
                if hasattr(self, 'comboBox_status'):
                    self.comboBox_status.setCurrentIndex(0)

            print("Все поля очищены")
        except AttributeError as e:
            print(f"Ошибка при очистке полей: {e}")

    def execute_search(self):
        """Выполняет поиск и отправляет результат"""
        model = self.search()
        if model:
            self.search.emit(model)
            self.close()
            