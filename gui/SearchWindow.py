from PyQt6 import uic, QtCore
from PyQt6.QtWidgets import QDialog
from utils.database import DatabaseManager, SQLQueries
from utils.ui_helpers import FormUtils, SearchConditionBuilder, MessageHelper


class SearchWindow(QDialog):
    search_requested = QtCore.pyqtSignal(str, list)
    reset_requested = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("gui/design/search.ui", self)

        self.db = DatabaseManager.connect()
        FormUtils.reset_datetime_edits(self)

        self.pushButton.clicked.connect(self._emit_search)
        self.pushButton_2.clicked.connect(self._clear_form)
        self.pushButton_3.clicked.connect(self._reset_search)

    def _emit_search(self):
        """Формирование и отправка поискового запроса"""
        params = self._get_form_data()
        conditions, query_params = self._build_search_conditions(params)

        sql = SQLQueries.search_query()
        if conditions:
            sql += " AND " + " AND ".join(conditions)

        self.search_requested.emit("", query_params)
        self.close()

    def _get_form_data(self):
        """Получение данных из формы"""
        return {
            'flight': self.lineEdit_flight.text().strip(),
            'airline': self.lineEdit_airline.text().strip(),
            'departure_from': self.lineEdit_departure_from.text().strip(),
            'destination': self.lineEdit_destination.text().strip(),
            'gate': self.lineEdit_gate.text().strip(),
            'status': self.comboBox_status.currentText(),
            'aircraft_type': self.lineEdit_aircraft_type.text().strip(),
            'departure_range': (
                self.dateTimeEdit_departure_time_range1.dateTime().toString("yyyy-MM-dd hh:mm"),
                self.dateTimeEdit_departure_time_range2.dateTime().toString("yyyy-MM-dd hh:mm")
            ),
            'arrival_range': (
                self.dateTimeEdit_arrival_time_range1.dateTime().toString("yyyy-MM-dd hh:mm"),
                self.dateTimeEdit_arrival_time_range2.dateTime().toString("yyyy-MM-dd hh:mm")
            )
        }

    def _build_search_conditions(self, params):
        """Построение условий поиска"""
        conditions = []
        query_params = []
        builder = SearchConditionBuilder

        # Простые поля
        simple_fields = [
            (params['flight'], "f.flight_number"),
            (params['airline'], "al.name"),
            (params['gate'], "f.gate"),
            (params['aircraft_type'], "ac.model")
        ]

        for value, field in simple_fields:
            builder.add_like_condition(conditions, query_params, value, field)

        # Аэропорты (множественный поиск)
        airport_fields = ["dap.name", "dap.city", "dap.code"]
        builder.add_multi_like_condition(conditions, query_params, params['departure_from'], airport_fields)

        arrival_fields = ["aap.name", "aap.city", "aap.code"]
        builder.add_multi_like_condition(conditions, query_params, params['destination'], arrival_fields)

        # Временные диапазоны
        builder.add_time_range_condition(conditions, query_params,
                                         *params['departure_range'], "f.departure_time")
        builder.add_time_range_condition(conditions, query_params,
                                         *params['arrival_range'], "f.arrival_time")

        # Статус
        if params['status'] != "Все статусы":
            conditions.append("st.name = ?")
            query_params.append(params['status'])

        return conditions, query_params

    def _clear_form(self):
        """Очистка формы"""
        FormUtils.clear_line_edits(self)
        FormUtils.reset_datetime_edits(self)
        FormUtils.reset_combo_boxes(self)

    def _reset_search(self):
        self.reset_requested.emit()
        self.close()