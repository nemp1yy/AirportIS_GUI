from PyQt6 import uic, QtCore
from PyQt6.QtWidgets import QDialog
from utils.ui_helpers import FormUtils, MessageHelper
from utils.database import DatabaseManager


class SearchWindow(QDialog):
    """Окно поиска с фильтрацией через FlightFilterProxyModel"""
    search_requested = QtCore.pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("gui/design/search.ui", self)

        self.db = DatabaseManager.connect()
        FormUtils.reset_datetime_edits(self)

        # Подключение кнопок
        self.pushButton.clicked.connect(self._emit_search)
        self.pushButton_2.clicked.connect(self._clear_form)
        self.pushButton_3.clicked.connect(self.close)

        # Если есть дополнительная кнопка для сброса фильтров
        if hasattr(self, 'pushButton_reset_filters'):
            self.pushButton_reset_filters.clicked.connect(self._reset_filters)

    def _emit_search(self):
        params = self._get_form_data()
        self.search_requested.emit(params)
        self.close()

    def _get_form_data(self):
        """Получение данных из формы"""
        params = {}

        # Простые поля
        if self.lineEdit_flight.text().strip():
            params['flight'] = self.lineEdit_flight.text().strip()

        if self.lineEdit_airline.text().strip():
            params['airline'] = self.lineEdit_airline.text().strip()

        if self.lineEdit_departure_from.text().strip():
            params['departure_from'] = self.lineEdit_departure_from.text().strip()

        if self.lineEdit_destination.text().strip():
            params['destination'] = self.lineEdit_destination.text().strip()

        if self.lineEdit_gate.text().strip():
            params['gate'] = self.lineEdit_gate.text().strip()

        if self.lineEdit_aircraft_type.text().strip():
            params['aircraft_type'] = self.lineEdit_aircraft_type.text().strip()

        if self.comboBox_status.currentText() != "Все статусы":
            params['status'] = self.comboBox_status.currentText()

        # Временные диапазоны (добавляем только если выбраны)
        departure_start = self.dateTimeEdit_departure_time_range1.dateTime().toString("yyyy-MM-dd hh:mm")
        departure_end = self.dateTimeEdit_departure_time_range2.dateTime().toString("yyyy-MM-dd hh:mm")
        if departure_start != departure_end:  # Проверяем, что диапазон задан
            params['departure_range'] = (departure_start, departure_end)

        arrival_start = self.dateTimeEdit_arrival_time_range1.dateTime().toString("yyyy-MM-dd hh:mm")
        arrival_end = self.dateTimeEdit_arrival_time_range2.dateTime().toString("yyyy-MM-dd hh:mm")
        if arrival_start != arrival_end:  # Проверяем, что диапазон задан
            params['arrival_range'] = (arrival_start, arrival_end)

    def _apply_filter(self):
        """Применение фильтров к таблице"""
        filters = self._collect_filters()

        if not filters:
            MessageHelper.show_info(self, "Поиск", "Заполните хотя бы одно поле для поиска")
            return

        self.filter_requested.emit(filters)
        self.close()

    def _collect_filters(self):
        """Сбор всех фильтров из формы"""
        filters = {}

        # Простые текстовые поля
        text_fields = ['flight', 'airline', 'departure_from', 'destination', 'gate', 'aircraft_type']
        text_values = FormUtils.get_line_edit_values(self, text_fields)

        # Добавляем только непустые значения
        for field, value in text_values.items():
            if value:
                filters[field] = value

        # Статус
        status = self.comboBox_status.currentText()
        if status and status != "Все статусы":
            filters['status'] = status

        # Временные диапазоны
        departure_range = FormUtils.get_datetime_range(
            self.dateTimeEdit_departure_time_range1,
            self.dateTimeEdit_departure_time_range2
        )
        if departure_range:
            filters['departure_range'] = departure_range

        arrival_range = FormUtils.get_datetime_range(
            self.dateTimeEdit_arrival_time_range1,
            self.dateTimeEdit_arrival_time_range2
        )
        if arrival_range:
            filters['arrival_range'] = arrival_range

        return filters

    def _clear_form(self):
        """Очистка формы поиска"""
        FormUtils.clear_line_edits(self)
        FormUtils.reset_datetime_edits(self)
        FormUtils.reset_combo_boxes(self)

    def _reset_filters(self):
        """Сброс всех фильтров в таблице"""
        self.filters_cleared.emit()
        self.close()

    def set_initial_values(self, **kwargs):
        """Установка начальных значений в форму

        Args:
            **kwargs: Пары field_name=value для установки в форму
        """
        for field_name, value in kwargs.items():
            # Для текстовых полей
            line_edit = self.findChild(self.__class__, f"lineEdit_{field_name}")
            if line_edit and hasattr(line_edit, 'setText'):
                line_edit.setText(str(value))

            # Для combobox
            if field_name == 'status':
                combo = self.comboBox_status
                index = combo.findText(str(value))
                if index >= 0:
                    combo.setCurrentIndex(index)