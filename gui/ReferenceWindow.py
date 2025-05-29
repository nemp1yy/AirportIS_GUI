from PyQt6 import uic
from PyQt6.QtWidgets import QDialog, QMessageBox
from PyQt6.QtSql import QSqlTableModel

class ReferenceDialog(QDialog):
    def __init__(self, table_name, parent=None):
        super().__init__(parent)
        uic.loadUi("gui/ReferenceDialog.ui", self)

        self.table_name = table_name
        self.model = QSqlTableModel(self)
        self.model.setTable(self.table_name)
        self.model.select()

        self.tableView.setModel(self.model)
        self.tableView.resizeColumnsToContents()

        self.pushButton_add.clicked.connect(self.add_row)
        self.pushButton_del.clicked.connect(self.delete_row)
        self.pushButton_save.clicked.connect(self.save_changes)

    def add_row(self):
        self.model.insertRow(self.model.rowCount())

    def delete_row(self):
        index = self.tableView.currentIndex()
        if index.isValid():
            self.model.removeRow(index.row())

    def save_changes(self):
        if not self.model.submitAll():
            QMessageBox.warning(self, "Ошибка", "Не удалось сохранить изменения")
