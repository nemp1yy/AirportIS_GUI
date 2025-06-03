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

        self.save_button.clicked.connect(self._save_and_close)
        self.cancel_button.clicked.connect(self.reject)

        FormUtils.reset_datetime_edits(self)

        if row is not None:
            self._load_data()

    def _fill_combo(self, combo, table, id_col, name_col):
        combo.clear()  # Очищаем комбобокс перед заполнением
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
        self._set_combo_by_data(self.comboBox_departure, record.value("departure_airport_id"))
        self._set_combo_by_data(self.comboBox_arrival, record.value("arrival_airport_id"))
        self._set_combo_by_data(self.comboBox_status, record.value("status_id"))

        # Исправлена ошибка: было "departure_time" в обоих случаях
        departure_time = record.value("departure_time")
        arrival_time = record.value("arrival_time")

        if departure_time:
            self.dateTimeEdit_departure_time.setDateTime(
                QDateTime.fromString(str(departure_time), "yyyy-MM-dd HH:mm"))
        if arrival_time:
            self.dateTimeEdit_arrival_time.setDateTime(QDateTime.fromString(str(arrival_time), "yyyy-MM-dd HH:mm"))

    def _set_combo_by_data(self, combo, value):
        """Устанавливает значение в комбобоксе по данным"""
        if value is not None:
            index = combo.findData(value)
            if index >= 0:
                combo.setCurrentIndex(index)

    def apply_changes(self):
        """Применяет изменения к модели"""
        try:
            if self.row is None:
                # Добавление новой записи
                if not self.model.insertRow(self.model.rowCount()):
                    MessageHelper.show_error(self, "Ошибка", "Не удалось добавить новую строку")
                    return False
                self.row = self.model.rowCount() - 1

            record = self.model.record(self.row)

            # Устанавливаем значения полей
            record.setValue("flight_number", self.lineEdit_flight.text())
            record.setValue("gate", self.lineEdit_gate.text())
            record.setValue("airline_id", self.comboBox_airline.currentData())
            record.setValue("aircraft_type_id",
                            self.comboBox_aircraft_type.currentData())  # Исправлено с airline_type_id
            record.setValue("departure_id", self.comboBox_departure.currentData())  # Добавлено
            record.setValue("arrival_id", self.comboBox_arrival.currentData())  # Добавлено
            record.setValue("status_id", self.comboBox_status.currentData())
            record.setValue("departure_time",
                            self.dateTimeEdit_departure_time.dateTime().toString("yyyy-MM-dd HH:mm"))
            record.setValue("arrival_time", self.dateTimeEdit_arrival_time.dateTime().toString("yyyy-MM-dd HH:mm"))

            # Применяем запись к модели
            if not self.model.setRecord(self.row, record):
                MessageHelper.show_error(self, "Ошибка",
                                         f"Не удалось установить запись: {self.model.lastError().text()}")
                return False

            # Сохраняем изменения
            if not self.model.submitAll():
                MessageHelper.show_error(self, "Ошибка",
                                         f"Не удалось сохранить изменения: {self.model.lastError().text()}")
                return False

            return True

        except Exception as e:
            MessageHelper.show_error(self, "Ошибка", f"Произошла ошибка: {str(e)}")
            return False

    def _save_and_close(self):
        if self.apply_changes():
            self.accept()