from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QMessageBox


class TableManager:
    """Менеджер для работы с таблицами"""

    @staticmethod
    def setup_table_view(table_view, model, hide_id=True):
        """Стандартная настройка TableView"""
        table_view.setModel(model)
        table_view.resizeColumnsToContents()
        table_view.setSortingEnabled(True)
        if hide_id:
            table_view.setColumnHidden(0, True)


class MessageHelper:
    """Помощник для показа сообщений"""

    @staticmethod
    def show_error(parent, title, message):
        """Показ сообщения об ошибке"""
        QMessageBox.warning(parent, title, message)

    @staticmethod
    def show_critical(parent, title, message):
        """Показ критического сообщения"""
        QMessageBox.critical(parent, title, message)


class FormUtils:
    """Утилиты для работы с формами"""

    @staticmethod
    def clear_line_edits(parent):
        """Очистка всех QLineEdit в родительском виджете"""
        for line_edit in parent.findChildren(QtWidgets.QLineEdit):
            line_edit.clear()

    @staticmethod
    def reset_datetime_edits(parent):
        """Сброс всех QDateTimeEdit к текущему времени"""
        current_datetime = QtCore.QDateTime.currentDateTime()
        for date_edit in parent.findChildren(QtWidgets.QDateTimeEdit):
            date_edit.setDateTime(current_datetime)

    @staticmethod
    def reset_combo_boxes(parent):
        """Сброс всех QComboBox к первому элементу"""
        for combo in parent.findChildren(QtWidgets.QComboBox):
            combo.setCurrentIndex(0)


class SearchConditionBuilder:
    """Построитель условий поиска"""

    @staticmethod
    def add_like_condition(conditions, params, value, field):
        """Добавление LIKE условия"""
        if value:
            conditions.append(f"{field} LIKE ?")
            params.append(f"%{value}%")

    @staticmethod
    def add_multi_like_condition(conditions, params, value, fields):
        """Добавление множественного LIKE условия"""
        if value:
            condition = " OR ".join([f"{field} LIKE ?" for field in fields])
            conditions.append(condition)
            params.extend([f"%{value}%"] * len(fields))

    @staticmethod
    def add_time_range_condition(conditions, params, start_time, end_time, field):
        """Добавление условия временного диапазона"""
        if start_time and end_time:
            conditions.append(f"{field} BETWEEN ? AND ?")
            params.extend([start_time, end_time])
        elif start_time:
            conditions.append(f"{field} >= ?")
            params.append(start_time)
        elif end_time:
            conditions.append(f"{field} <= ?")
            params.append(end_time)