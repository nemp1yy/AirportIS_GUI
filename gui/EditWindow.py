from PyQt6 import uic
from PyQt6.QtWidgets import QDialog
from PyQt6.QtCore import QDateTime
from PyQt6.QtSql import QSqlQuery

from utils.ui_helpers import TableManager, MessageHelper, FormUtils
from utils.database import DatabaseManager

class EditWindow(QDialog):
    def __init__(self, model, row=None, parent=None):
        super().__init__(parent)
        uic.loadUi("gui/design/edit.ui", self)

        self.db = DatabaseManager.connect()
        self.model = model
        self.row = row

        self._fill_combo(self.comboBox_airline, "airlines", "id", "name")
        self._fill_combo(self.comboBox_aircraft_type, "aircraft_types", "id", "model")
        self._fill_combo(self.comboBox_departure, "airports", "id", "name")
        self._fill_combo(self.comboBox_arrival, "airports", "id", "name")
        self._fill_combo(self.comboBox_status, "statuses", "id", "name")

        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        FormUtils.reset_datetime_edits(self)

        if row is not None:
            self._load_data()

    def _fill_combo(self, combo, table, id_col, name_col):
        query = QSqlQuery(self.db)
        query.exec(f"SELECT {id_col}, {name_col} FROM {table}")
        while query.next():
            combo.addItem(str(query.value(1)), query.value(0))

    def _load_data(self):
        record = self.model.record(self.row)
        self.lineEdit_flight.setText(record.value("flight_number"))
        self.lineEdit_gate.setText(record.value("gate"))

        self._set_combo_by_data(self.comboBox_airline, record.value("airline_id"))
        self._set_combo_by_data(self.comboBox_aircraft_type, record.value("aircraft_type_id"))
        self._set_combo_by_data(self.comboBox_departure, record.value("departure_id"))
        self._set_combo_by_data(self.comboBox_arrival, record.value("arrival_id"))
        self._set_combo_by_data(self.comboBox_status, record.value("status_id"))

        self.dateTimeEdit_departure_time.setDateTime(QDateTime.fromString(record.value("departure_time"), "yyyy-MM-dd HH:mm:ss"))
        self.dateTimeEdit_arrival_time.setDateTime(QDateTime.fromString(record.value("departure_time"), "yyyy-MM-dd HH:mm:ss"))

        def _set_combo_by_data(self, combo, value):
            index = combo.findData(value)
            if index >= 0:
                combo.setCurrentIndex(index)

        def apply_changet(self):
            if self.row is None:
                self.model.insertRow(self.model.rowCount())
                self.row = self.model.rowCount() - 1

            record = self.model.record(self.row)
            record.setValue("flight_number", self.lineEdit_flight.text())
            record.setValue("gate", self.lineEdit_gate.text())
            record.setValue("airline_id", self.comboBox_airline.currentData())
            record.setValue("airline_type_id", self.comboBox_aircraft_type.currentData())
            record.setValue("status_id", self.comboBox_status.currentData())
            record.setValue("departure_time", self.dateTimeEdit_departure_time.dateTime().toString("yyyy-MM-dd HH:mm:ss"))
            record.setValue("arrival_time", self.dateTimeEdit_arrival_time.dateTime().toString("yyyy-MM-dd HH:mm:ss"))

            self.model.setRecord(self.row, record)
            self.model.submitAll()



