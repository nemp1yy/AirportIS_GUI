from PyQt6 import uic, QtCore, QtGui
from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6 import QtWidgets
import sys
from PyQt6.QtSql import QSqlDatabase, QSqlTableModel, QSqlQueryModel, QSqlQuery
from gui.SearchWindow import SearchWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Загружаем UI файл
        uic.loadUi("gui/design/main.ui", self)

        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName('data/data.db')
        if not self.db.open():
            print("Не удалось открыть базу данных")
            return False

        self.table1 = QSqlTableModel()
        self.table1.setTable("flights")
        self.table1.select()
        self.tableView.setModel(self.table1)


        self.tableView.resizeColumnsToContents()
        self.tableView.setSortingEnabled(True)
        self.tableView.setColumnHidden(0, True)

        self.pushButton.clicked.connect(self.newRow)
        self.pushButton_2.clicked.connect(self.delRow)
        self.pushButton_3.clicked.connect(self.show_search_window)
        self.pushButton_4.clicked.connect(self.resetTable)


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
        self.table1 = QSqlTableModel(self, self.db)
        self.table1.setTable("flights")
        self.table1.select()
        self.tableView.setModel(self.table1)
        self.tableView.resizeColumnsToContents()
        self.tableView.setSortingEnabled(True)
        self.tableView.setColumnHidden(0, True)
        print("Поиск сброшен, отображается вся таблица")
