from PyQt6 import uic
from PyQt6.QtWidgets import QDialog
from PyQt6.QtSql import QSqlTableModel, QSqlDatabase
from utils.ui_helpers import TableManager, MessageHelper


class ReferenceWindow(QDialog):
    def __init__(self, table_name, parent=None):
        super().__init__(parent)
        uic.loadUi("gui/design/reference.ui", self)

        # Инициализация модели
        self.model = QSqlTableModel(self)
        self.model.setTable(table_name)
        self.model.select()

        # Настройка UI
        TableManager.setup_table_view(self.tableView, self.model)
        self._connect_buttons()

    def _connect_buttons(self):
        """Подключение кнопок"""
        self.add_button.clicked.connect(lambda: self.model.insertRow(self.model.rowCount()))
        self.delete_button.clicked.connect(self._delete_selected)
        self.save_button.clicked.connect(self._save_and_close)
        self.update_button.clicked.connect(self._refresh_model)

    def _delete_selected(self):
        """Удаление выбранной строки"""
        index = self.tableView.currentIndex()
        if index.isValid():
            self.model.removeRow(index.row())

    def _save_and_close(self):
        """Сохранение и закрытие"""
        if self.model.submitAll():
            self.close()
        else:
            MessageHelper.show_error(self, "Ошибка", "Не удалось сохранить изменения")

    def _refresh_model(self):
        """Обновление модели"""
        try:
            table_name = self.model.tableName()
            self.model = QSqlTableModel(self, QSqlDatabase.database())
            self.model.setTable(table_name)
            self.model.select()
            TableManager.setup_table_view(self.tableView, self.model)
        except Exception as e:
            MessageHelper.show_error(self, "Ошибка", f"Произошла ошибка: {e}")