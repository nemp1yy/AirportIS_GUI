from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow

from gui.SearchWindow import SearchWindow
from gui.ReferenceWindow import ReferenceWindow
from gui.AboutWindow import AboutWindow
from gui.EditWindow import EditWindow

from utils.database import DatabaseManager
from utils.ui_helpers import TableManager, MessageHelper


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("gui/design/main.ui", self)

        self.db = DatabaseManager.connect()
        self.model = DatabaseManager.create_flights_relational_model(self.db)

        self.tableView.setModel(self.model)
        TableManager.setup_table_view(self.tableView, self.model)

        self._connect_buttons()
        self._connect_menu()
        self.tableView.doubleClicked.connect(self._edit_row)

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
        """Добавление новой записи через диалог"""
        try:
            dialog = EditWindow(self.model, row=None, parent=self)
            if dialog.exec():
                if dialog.apply_changes():
                    self.model.select()  # Обновляем модель
                    if hasattr(self, 'statusbar'):
                        self.statusbar.showMessage(f"Запись добавлена. Всего записей: {self.model.rowCount()}")

        except Exception as e:
            print(e)

    def _edit_row(self):
        """Редактирование выбранной записи"""
        try:
            index = self.tableView.currentIndex()
            if not index.isValid():
                MessageHelper.show_error(self, "Ошибка", "Не выбрана строка для редактирования")
                return

            dialog = EditWindow(self.model, row=index.row(), parent=self)
            if dialog.exec():
                if dialog.apply_changes():
                    self.model.select()  # Обновляем модель
                    if hasattr(self, 'statusbar'):
                        self.statusbar.showMessage(f"Запись обновлена. Всего записей: {self.model.rowCount()}")

        except Exception as e:
            print(e)

    def _delete_row(self):
        """Удаление выбранной записи"""
        index = self.tableView.currentIndex()
        if not index.isValid():
            MessageHelper.show_error(self, "Ошибка", "Не выбрана строка для удаления")
            return

        # Подтверждение удаления
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(self, "Подтверждение",
                                     "Вы уверены, что хотите удалить выбранную запись?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            if self.model.removeRow(index.row()):
                if self.model.submitAll():
                    if hasattr(self, 'statusbar'):
                        self.statusbar.showMessage(f"Запись удалена. Всего записей: {self.model.rowCount()}")
                else:
                    MessageHelper.show_error(self, "Ошибка",
                                             f"Не удалось удалить запись: {self.model.lastError().text()}")
            else:
                MessageHelper.show_error(self, "Ошибка", "Не удалось удалить строку")

    def _refresh(self):
        """Обновление данных"""
        self.model.setFilter("")
        self.model.select()
        if hasattr(self, 'statusbar'):
            self.statusbar.showMessage(f"Обновлено. Всего записей: {self.model.rowCount()}")

    def _show_search(self):
        """Показ диалога поиска"""
        dialog = SearchWindow(self)
        dialog.search_requested.connect(self._apply_search_filter)
        dialog.exec()

    def _apply_search_filter(self, filter_text):
        """Применение фильтра поиска"""
        self.model.setFilter(filter_text)
        self.model.select()
        if hasattr(self, 'statusbar'):
            self.statusbar.showMessage(f"Найдено: {self.model.rowCount()} записей")