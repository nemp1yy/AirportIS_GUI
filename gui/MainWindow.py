from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow

from gui.SearchWindow import SearchWindow
from gui.ReferenceWindow import ReferenceWindow
from gui.AboutWindow import AboutWindow
from config.cfg import Config
from utils.database import DatabaseManager, SQLQueries
from utils.ui_helpers import TableManager, MessageHelper


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("gui/design/main.ui", self)

        # Инициализация
        Config("config.json")
        self.db = DatabaseManager.connect()

        # Используем новый метод для создания реляционной модели
        self.model = DatabaseManager.create_flights_relational_model(self.db)
        TableManager.setup_table_view(self.tableView, self.model)

        # Подключение сигналов
        self._connect_buttons()
        self._connect_menu_actions()

    def _connect_buttons(self):
        """Подключение кнопок"""
        self.add_button.clicked.connect(self._add_new_row)
        self.delete_button.clicked.connect(self._delete_selected_row)
        self.search_button.clicked.connect(self._show_search_dialog)
        self.refresh_button.clicked.connect(self._refresh_table)

    def _add_new_row(self):
        """Добавление новой строки"""
        try:
            row = self.model.rowCount()
            if self.model.insertRow(row):
                # Устанавливаем курсор на новую строку (номер рейса)
                index = self.model.index(row, 1)
                self.tableView.setCurrentIndex(index)
                self.tableView.edit(index)
            else:
                MessageHelper.show_error(self, "Ошибка", "Не удалось добавить новую запись")
        except Exception as e:
            MessageHelper.show_error(self, "Ошибка", f"Ошибка при добавлении: {e}")

    def _connect_menu_actions(self):
        """Подключение действий меню"""
        menu_actions = {
            self.actionAirlines: "airlines",
            self.actionAircraftTypes: "aircraft_types",
            self.actionAirports: "airports",
            self.actionStatuses: "statuses"
        }
        for action, table in menu_actions.items():
            action.triggered.connect(lambda checked, t=table: ReferenceWindow(t, self).exec())



    def _delete_selected_row(self):
        """Удаление выбранной строки"""
        row = self.tableView.currentIndex().row()
        if row < 0:
            MessageHelper.show_error(self, "Ошибка", "Не выбрана запись для удаления")
            return

        try:
            if self.model.removeRow(row):
                self.model.submitAll()
                if self.model.lastError().isValid():
                    MessageHelper.show_error(self, "Ошибка", f"Ошибка удаления: {self.model.lastError().text()}")
                    self.model.revertAll()
            else:
                MessageHelper.show_error(self, "Ошибка", "Не удалось удалить запись")
        except Exception as e:
            MessageHelper.show_error(self, "Ошибка", f"Ошибка при удалении: {e}")

    def _show_search_dialog(self):
        """Показ диалога поиска"""
        dialog = SearchWindow(self)
        dialog.search_requested.connect(self._apply_search)
        dialog.exec()

    def _apply_search(self, sql, params):
        """Применение результатов поиска"""
        # Для поиска используем исходный подход с JOIN
        search_model = DatabaseManager.create_query_model(self.db, sql, params)
        if search_model.lastError().isValid():
            MessageHelper.show_error(self, "Ошибка", f"Поиск не выполнен: {search_model.lastError().text()}")
            return
        TableManager.setup_table_view(self.tableView, search_model)

    def _refresh_table(self):
        """Обновление таблицы"""
        # Возвращаемся к основной редактируемой модели
        self.model = DatabaseManager.create_flights_relational_model(self.db)
        TableManager.setup_table_view(self.tableView, self.model)