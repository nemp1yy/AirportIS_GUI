from PyQt6 import uic, QtCore, QtGui
from PyQt6.QtWidgets import QMainWindow, QApplication, QMessageBox
from PyQt6 import QtWidgets
from PyQt6.QtSql import QSqlDatabase, QSqlTableModel, QSqlQueryModel, QSqlQuery

from gui.SearchWindow import SearchWindow
from gui.ReferenceWindow import ReferenceWindow

from config.cfg import Config

import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        cfg = Config("config.json")
        # Загружаем UI файл
        uic.loadUi("gui/design/main.ui", self)

        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName('data/data.db')
        if not self.db.open():
            QMessageBox.critical(self, "Ошибка БД", "Не удалось подключиться к базе данных")
            sys.exit(1)

        self.load_flights()

        self.tableView.resizeColumnsToContents()
        self.tableView.setSortingEnabled(True)
        self.tableView.setColumnHidden(0, True)

        self.add_button.clicked.connect(self.newRow)
        self.delete_button.clicked.connect(self.delRow)
        self.search_button.clicked.connect(self.show_search_window)
        self.refresh_button.clicked.connect(self.resetTable)

        self.actionAirlines.triggered.connect(lambda: self.show_reference_dialog("airlines"))
        self.actionAircraftTypes.triggered.connect(lambda: self.show_reference_dialog("aircraft_types"))
        self.actionAirports.triggered.connect(lambda: self.show_reference_dialog("airports"))
        self.actionStatuses.triggered.connect(lambda: self.show_reference_dialog("statuses"))

    def load_flights(self):
        model = QSqlQueryModel(self)
        query = '''
        SELECT f.id, f.flight_number, al.name AS airline, ac.model AS aircraft,
               dap.code AS departure, aap.code AS arrival,
               f.departure_time, f.arrival_time,
               st.name AS status, f.gate
        FROM flights f
        LEFT JOIN airlines al ON f.airline_id = al.id
        LEFT JOIN aircraft_types ac ON f.aircraft_type_id = ac.id
        LEFT JOIN airports dap ON f.departure_airport_id = dap.id
        LEFT JOIN airports aap ON f.arrival_airport_id = aap.id
        LEFT JOIN statuses st ON f.status_id = st.id
        '''
        model.setQuery(query, self.db)
        self.tableView.setModel(model)
        self.tableView.resizeColumnsToContents()

    def newRow(self):
        print('Добавление строки')
        kol = int(self.table1.rowCount())
        self.table1.insertRow(kol)

    def delRow(self):
        print("Удаление строки")
        self.table1.removeRow(self.tableView.currentIndex().row())
        self.table1.select()

    def show_search_window(self):
        print("Создаю SearchWindow")
        search_dialog = SearchWindow(self)
        search_dialog.search_requested.connect(self.apply_search)
        search_dialog.exec()
        print("Окно закрыто")

    def apply_search(self, sql, params):
        """Применяет результаты поиска"""
        model = QSqlQueryModel()

        if params:
            # Для параметризованных запросов
            query = QSqlQuery(self.db)
            query.prepare(sql)
            for param in params:
                query.addBindValue(param)
            query.exec()
            model.setQuery(query)
        else:
            model.setQuery(sql, self.db)

        if model.lastError().isValid():
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Не удалось выполнить поиск")
            return

        self.tableView.setModel(model)
        self.tableView.resizeColumnsToContents()

    def resetTable(self):
        """Сбрасывает результаты поиска и возвращает полную таблицу"""
        table = QSqlTableModel(self, self.db)
        query = '''
                SELECT f.id, f.flight_number, al.name AS airline, ac.model AS aircraft,
                       dap.code AS departure, aap.code AS arrival,
                       f.departure_time, f.arrival_time,
                       st.name AS status, f.gate
                FROM flights f
                LEFT JOIN airlines al ON f.airline_id = al.id
                LEFT JOIN aircraft_types ac ON f.aircraft_type_id = ac.id
                LEFT JOIN airports dap ON f.departure_airport_id = dap.id
                LEFT JOIN airports aap ON f.arrival_airport_id = aap.id
                LEFT JOIN statuses st ON f.status_id = st.id
                '''
        table.setQuery(query, self.db)
        self.tableView.setModel(table)

        self.tableView.resizeColumnsToContents()
        self.tableView.setModel(table)
        self.tableView.resizeColumnsToContents()
        self.tableView.setSortingEnabled(True)
        self.tableView.setColumnHidden(0, True)
        print("Поиск сброшен, отображается вся таблица")

    def show_reference_dialog(self, table_name):
        try:

            dialog = ReferenceWindow(table_name, self)
            dialog.exec()

        except Exception as e:
            print(f"Ошибка при открытии диалога: {e}")
