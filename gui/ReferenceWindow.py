from PyQt6 import uic
from PyQt6.QtWidgets import QDialog
from PyQt6.QtSql import QSqlTableModel, QSqlDatabase
from utils.ui_helpers import TableManager, MessageHelper


class ReferenceWindow(QDialog):
    def __init__(self, table_name, parent=None):
        super().__init__(parent)
        uic.loadUi("gui/design/reference.ui", self)

        self.model = QSqlTableModel(self)
        self.model.setTable(table_name)
        self.model.select()

        TableManager.setup_table_view(self.tableView, self.model)

        self._connect_buttons()
        # self._resize_to_contents()
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
        try:
            table_name = self.model.tableName()
            self.model = QSqlTableModel(self, QSqlDatabase.database())
            self.model.setTable(table_name)
            self.model.select()
            TableManager.setup_table_view(self.tableView, self.model)
            self._resize_to_contents()  # Добавлено здесь
        except Exception as e:
            MessageHelper.show_error(self, "Ошибка", f"Произошла ошибка: {e}")

    def _resize_to_contents(self):
        # Подгоняем ширину столбцов под содержимое
        self.tableView.resizeColumnsToContents()

        # Рассчитываем общую ширину таблицы
        table_width = self.tableView.verticalHeader().width() + 2  # Учет вертикального заголовка
        for column in range(self.model.columnCount()):
            table_width += self.tableView.columnWidth(column)

        # Рассчитываем высоту таблицы (макс. 10 строк)
        header_height = self.tableView.horizontalHeader().height()
        row_height = self.tableView.rowHeight(0) if self.model.rowCount() > 0 else 30
        visible_rows = min(10, self.model.rowCount())
        table_height = header_height + (row_height * visible_rows)

        # Добавляем отступы для элементов управления
        padding = 20
        total_width = table_width + padding
        total_height = table_height + self.button_frame.height() + padding

        # Устанавливаем размеры окна
        self.resize(total_width, total_height)
        self.setMinimumSize(total_width, total_height)