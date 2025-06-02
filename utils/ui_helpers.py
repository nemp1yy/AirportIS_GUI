from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QSortFilterProxyModel, Qt
from PyQt6.QtSql import QSqlRelationalDelegate, QSqlRelationalTableModel
from datetime import datetime


class TableManager:
    @staticmethod
    def setup_table_view(table_view, model):
        """Настройка представления таблицы с поддержкой выпадающих списков"""
        table_view.setModel(model)

        # Если это реляционная модель - устанавливаем специальный делегат
        if isinstance(model, QSqlRelationalTableModel):
            # Создаем делегат для выпадающих списков
            delegate = QSqlRelationalDelegate(table_view)
            table_view.setItemDelegate(delegate)

        # Настройка внешнего вида
        table_view.resizeColumnsToContents()
        table_view.setAlternatingRowColors(True)
        table_view.setSelectionBehavior(table_view.SelectionBehavior.SelectRows)
        table_view.setSelectionMode(table_view.SelectionMode.SingleSelection)

        # Скрываем ID столбец (опционально)
        if model.columnCount() > 0:
            table_view.setColumnHidden(0, True)


class FlightFilterProxyModel(QSortFilterProxyModel):
    """Кастомная модель для фильтрации рейсов по множественным критериям"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.filters = {}
        self.column_mapping = {}
        self.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

    def set_column_mapping(self, mapping):
        """Установка соответствия названий полей и индексов колонок

        Args:
            mapping (dict): Словарь вида {'field_name': column_index}
            Например: {'flight': 1, 'airline': 2, 'departure_from': 4, ...}
        """
        self.column_mapping = mapping

    def set_filters(self, filters):
        """Установка фильтров для поиска

        Args:
            filters (dict): Словарь фильтров
        """
        self.filters = filters
        self.invalidateFilter()

    def clear_filters(self):
        """Очистка всех фильтров"""
        self.filters = {}
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        """Проверка строки на соответствие фильтрам"""
        if not self.filters:
            return True

        model = self.sourceModel()

        for filter_name, filter_value in self.filters.items():
            if not filter_value:  # Пропускаем пустые фильтры
                continue

            if filter_name in ['departure_range', 'arrival_range']:
                # Обработка временных диапазонов
                time_field = 'departure_time' if filter_name == 'departure_range' else 'arrival_time'
                time_column = self.column_mapping.get(time_field)
                if time_column is not None:
                    cell_data = model.data(model.index(source_row, time_column))
                    if not self._check_time_range(cell_data, filter_value):
                        return False

            elif filter_name == 'status':
                # Точное совпадение для статуса
                if filter_value != "Все статусы":
                    status_column = self.column_mapping.get('status')
                    if status_column is not None:
                        cell_data = model.data(model.index(source_row, status_column))
                        if str(cell_data).lower() != filter_value.lower():
                            return False

            else:
                # Обычный поиск по подстроке
                column_index = self.column_mapping.get(filter_name)
                if column_index is not None:
                    cell_data = str(model.data(model.index(source_row, column_index)))
                    if not self._contains_ignore_case(cell_data, filter_value):
                        return False

        return True

    def _contains_ignore_case(self, text, search_term):
        """Проверка содержания подстроки (без учета регистра)"""
        return search_term.lower() in text.lower()

    def _check_time_range(self, cell_data, time_range):
        """Проверка попадания времени в диапазон"""
        if not time_range or len(time_range) != 2:
            return True

        start_time, end_time = time_range
        if not start_time or not end_time:
            return True

        try:
            # Пробуем разные форматы времени
            cell_str = str(cell_data)

            # Возможные форматы времени
            time_formats = [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d %H:%M",
                "%d.%m.%Y %H:%M",
                "%d/%m/%Y %H:%M"
            ]

            cell_time = None
            for fmt in time_formats:
                try:
                    cell_time = datetime.strptime(cell_str, fmt)
                    break
                except ValueError:
                    continue

            if cell_time is None:
                return True  # Если не удалось достать, показываем строку

            start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
            end_dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M")

            return start_dt <= cell_time <= end_dt
        except (ValueError, TypeError):
            return True

    def get_filtered_count(self):
        """Получение количества отфильтрованных строк"""
        return self.rowCount()


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

    @staticmethod
    def show_info(parent, title, message):
        """Показ информационного сообщения"""
        QMessageBox.information(parent, title, message)


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

    @staticmethod
    def get_line_edit_values(parent, field_names):
        """Получение значений из QLineEdit по именам полей

        Args:
            parent: Родительский виджет
            field_names (list): Список имен полей ['flight', 'airline', ...]

        Returns:
            dict: Словарь {field_name: value}
        """
        values = {}
        for field_name in field_names:
            line_edit = parent.findChild(QtWidgets.QLineEdit, f"lineEdit_{field_name}")
            if line_edit:
                values[field_name] = line_edit.text().strip()
        return values

    @staticmethod
    def get_datetime_range(start_edit, end_edit, default_check_value="2000-01-01 00:00"):
        """Получение временного диапазона из QDateTimeEdit

        Args:
            start_edit: QDateTimeEdit для начального времени
            end_edit: QDateTimeEdit для конечного времени
            default_check_value: Значение для проверки на дефолт

        Returns:
            tuple или None: (start_time, end_time) или None если дефолтные значения
        """
        start_time = start_edit.dateTime().toString("yyyy-MM-dd hh:mm")
        end_time = end_edit.dateTime().toString("yyyy-MM-dd hh:mm")

        if start_time != default_check_value or end_time != default_check_value:
            return (start_time, end_time)
        return None


class SearchConditionBuilder:
    """Построитель условий поиска для SQL запросов"""

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
            conditions.append(f"({condition})")  # Заключаем в скобки для корректности
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


class FilterHelper:
    """Помощник для работы с фильтрами таблиц"""

    @staticmethod
    def create_flight_filter_model(source_model, parent=None):
        """Создание модели фильтрации для рейсов

        Args:
            source_model: Исходная модель данных
            parent: Родительский объект

        Returns:
            FlightFilterProxyModel: Настроенная модель фильтрации
        """
        filter_model = FlightFilterProxyModel(parent)
        filter_model.setSourceModel(source_model)

        # Стандартное соответствие колонок для рейсов
        # Адаптируйте под вашу структуру данных
        default_mapping = {
            'flight': 1,  # Номер рейса
            'airline': 2,  # Авиакомпания
            'aircraft_type': 3,  # Тип самолета
            'departure_from': 4,  # Аэропорт отправления
            'destination': 5,  # Аэропорт назначения
            'departure_time': 6,  # Время отправления
            'arrival_time': 7,  # Время прибытия
            'status': 8,  # Статус
            'gate': 9  # Гейт
        }

        filter_model.set_column_mapping(default_mapping)
        return filter_model

    @staticmethod
    def setup_filtered_table(table_view, source_model, parent=None):
        """Настройка таблицы с фильтрацией

        Args:
            table_view: QTableView для отображения данных
            source_model: Исходная модель данных
            parent: Родительский объект

        Returns:
            FlightFilterProxyModel: Настроенная модель фильтрации
        """
        filter_model = FilterHelper.create_flight_filter_model(source_model, parent)

        # Настраиваем таблицу
        table_view.setModel(filter_model)
        table_view.setSortingEnabled(True)
        table_view.resizeColumnsToContents()

        # Скрываем ID колонку если она есть
        if filter_model.columnCount() > 0:
            table_view.setColumnHidden(0, True)

        return filter_model