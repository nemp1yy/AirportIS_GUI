from PyQt6 import uic
from PyQt6.QtWidgets import QDialog, QMessageBox
from PyQt6.QtSql import QSqlTableModel, QSqlDatabase

class ReferenceWindow(QDialog):
    def __init__(self, table_name, parent=None):
        super().__init__(parent)
        uic.loadUi("gui/design/reference.ui", self)

        self.tableName = table_name

        self.model = QSqlTableModel(self)
        self.model.setTable(self.tableName)
        self.model.select()

        self.tableView.setModel(self.model)
        self.tableView.resizeColumnsToContents()
        self.tableView.setSortingEnabled(True)
        self.tableView.setColumnHidden(0, True)

        self.add_button.clicked.connect(self.add_row)
        self.delete_button.clicked.connect(self.del_row)
        self.save_button.clicked.connect(self.save_changes)
        self.update_button.clicked.connect(self.resetTable)

    def add_row(self):
        self.model.insertRow(self.model.rowCount())

    def del_row(self):
        index = self.tableView.currentIndex()
        if index.isValid():
            self.model.removeRow(index.row())

    def save_changes(self):
        if not self.model.submitAll():
            QMessageBox.warning(self, "Ошибка", "Не удалось сохранить изменения")

        self.close()

    def resetTable(self):
        try:
            db = QSqlDatabase.database()  # Получаем текущее подключение к БД
            self.model = QSqlTableModel(self, db)
            self.model.setTable(self.tableName)
            self.model.select()

            self.tableView.setModel(self.model)
            self.tableView.resizeColumnsToContents()
            self.tableView.setSortingEnabled(True)
            self.tableView.setColumnHidden(0, True)

        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Произошла ошибка: {e}")
