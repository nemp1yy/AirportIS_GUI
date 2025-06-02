from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtSql import QSqlRelationalDelegate, QSqlQueryModel
from PyQt6.QtSql import QSqlQuery

from gui.SearchWindow import SearchWindow
from gui.ReferenceWindow import ReferenceWindow
from gui.AboutWindow import AboutWindow
from utils.database import DatabaseManager, SQLQueries
from utils.ui_helpers import MessageHelper, MultiFieldFilterProxyModel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("gui/design/main.ui", self)

        self.db = DatabaseManager.connect()

        self.model = DatabaseManager.create_flights_relational_model(self.db)

        self.proxy_model = MultiFieldFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.model)

        self.tableView.setModel(self.proxy_model)
        self.tableView.setItemDelegate(QSqlRelationalDelegate(self.tableView))
        self.tableView.setSortingEnabled(True)
        self.tableView.resizeColumnsToContents()
        self.tableView.setColumnHidden(0, True)

        self._connect_buttons()
        self._connect_menu()



        if hasattr(self, 'statusbar'):
            self.statusbar.showMessage(f"Всего записей: {self.model.rowCount()}")

    def _connect_buttons(self):
        self.add_button.clicked.connect(self._add_row)
        self.delete_button.clicked.connect(self._delete_row)
        self.refresh_button.clicked.connect(self._refresh)
        self.search_button.clicked.connect(self._show_search)

    def _connect_menu(self):
        menu_actions = {
            self.actionAirlines: "airlines",
            self.actionAircraftTypes: "aircraft_types",
            self.actionAirports: "airports",
            self.actionStatuses: "statuses"
        }
        for action, table in menu_actions.items():
            action.triggered.connect(lambda checked, t=table: ReferenceWindow(t, self).exec())

    def _add_row(self):
        row = self.model.rowCount()
        if self.model.insertRow(row):
            self.tableView.selectRow(row)
            self.tableView.edit(self.model.index(row, 1))
        else:
            MessageHelper.show_error(self, "Ошибка", "Не удалось добавить строку")

    def _delete_row(self):
        index = self.tableView.currentIndex()
        if not index.isValid():
            MessageHelper.show_error(self, "Ошибка", "Не выбрана строка")
            return
        self.model.removeRow(index.row())
        self.model.submitAll()

    def _refresh(self):
        self.model.setFilter("")
        if hasattr(self, 'statusbar'):
            self.statusbar.showMessage(f"Обновлено. Всего записей: {self.model.rowCount()}")

    def _show_search(self):
        dialog = SearchWindow(self)
        dialog.search_requested.connect(self._apply_search_query)
        dialog.reset_requested.connect(self._reset_search_results)  # ← новое подключение
        dialog.exec()

    def _apply_search_query(self, query_text, params):
        column_map = {
            'flight': 1,
            'airline': 2,
            'aircraft_type': 3,
            'departure_from': 4,
            'destination': 5,
            'departure_time': 6,
            'arrival_time': 7,
            'status': 8,
            'gate': 9
        }

        # Сопоставим по названиям фильтров
        filter_dict = {}
        for i, key in enumerate(column_map.keys()):
            value = params[i] if i < len(params) else None
            if value and value != "Все статусы":
                filter_dict[column_map[key]] = str(value)

        self.proxy_model.set_filters(filter_dict)

        if hasattr(self, 'statusbar'):
            self.statusbar.showMessage(f"Найдено записей: {self.proxy_model.rowCount()}")

        self.tableView.setModel(self.model)
        if hasattr(self, 'statusbar'):
            self.statusbar.showMessage(f"Результатов: {self.model.rowCount()}")

        print("Фильтры:", filter_dict)

    def _reset_search_results(self):
        self.tableView.setModel(self.model)
        self.tableView.setItemDelegate(QSqlRelationalDelegate(self.tableView))
        self.model.select()
        self.tableView.resizeColumnsToContents()

        if hasattr(self, 'statusbar'):
            self.statusbar.showMessage(f"Всего записей: {self.model.rowCount()}")
