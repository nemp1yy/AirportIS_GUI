from PyQt6 import uic
from PyQt6.QtWidgets import QDialog
from PyQt6.QtCore import QDateTime
from PyQt6.QtSql import QSqlQuery, QSqlTableModel

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
        combo.clear()  # Очищаем комбобокс перед заполнением
        query = QSqlQuery(self.db)
        query.exec(f"SELECT {id_col}, {name_col} FROM {table}")
        while query.next():
            combo.addItem(str(query.value(1)), query.value(0))

    def _load_data(self):
        record = self.model.record(self.row)

        # Получаем ID записи для загрузки исходных данных
        flight_id = record.value("id")

        # Загружаем исходные данные из таблицы flights
        query = QSqlQuery(self.db)
        query.prepare("""
            SELECT flight_number, airline_id, aircraft_type_id, 
                   departure_airport_id, arrival_airport_id, status_id,
                   departure_time, arrival_time, gate
            FROM flights WHERE id = ?
        """)
        query.addBindValue(flight_id)

        if not query.exec() or not query.next():
            MessageHelper.show_error(self, "Ошибка", "Не удалось загрузить данные записи")
            return

        # Заполняем поля формы
        self.lineEdit_flight.setText(query.value("flight_number") or "")
        self.lineEdit_gate.setText(query.value("gate") or "")

        # Устанавливаем значения комбобоксов по ID
        self._set_combo_by_data(self.comboBox_airline, query.value("airline_id"))
        self._set_combo_by_data(self.comboBox_aircraft_type, query.value("aircraft_type_id"))
        self._set_combo_by_data(self.comboBox_departure, query.value("departure_airport_id"))
        self._set_combo_by_data(self.comboBox_arrival, query.value("arrival_airport_id"))
        self._set_combo_by_data(self.comboBox_status, query.value("status_id"))

        # Устанавливаем время
        departure_time = query.value("departure_time")
        arrival_time = query.value("arrival_time")

        if departure_time:
            self.dateTimeEdit_departure_time.setDateTime(
                QDateTime.fromString(str(departure_time), "yyyy-MM-dd HH:mm"))
        if arrival_time:
            self.dateTimeEdit_arrival_time.setDateTime(
                QDateTime.fromString(str(arrival_time), "yyyy-MM-dd HH:mm"))

    def _set_combo_by_data(self, combo, value):
        """Устанавливает значение в комбобоксе по данным"""
        if value is not None:
            index = combo.findData(value)
            if index >= 0:
                combo.setCurrentIndex(index)
            else:
                print(f"Предупреждение: значение {value} не найдено в комбобоксе")
        else:
            combo.setCurrentIndex(-1)  # Сбрасываем выбор если значение None

    def apply_changes(self):
        """Применяет изменения к таблице flights через временную модель"""
        try:
            if self.row is None:
                # Добавление новой записи
                insert_model = QSqlTableModel(self, self.db)
                insert_model.setTable("flights")
                insert_model.select()

                new_row = insert_model.rowCount()
                if not insert_model.insertRow(new_row):
                    MessageHelper.show_error(self, "Ошибка", "Не удалось добавить новую строку")
                    return False

                record = insert_model.record()
                record.setValue("flight_number", self.lineEdit_flight.text())
                record.setValue("gate", self.lineEdit_gate.text())
                record.setValue("airline_id", self.comboBox_airline.currentData())
                record.setValue("aircraft_type_id", self.comboBox_aircraft_type.currentData())
                record.setValue("departure_airport_id", self.comboBox_departure.currentData())
                record.setValue("arrival_airport_id", self.comboBox_arrival.currentData())
                record.setValue("status_id", self.comboBox_status.currentData())
                record.setValue("departure_time",
                                self.dateTimeEdit_departure_time.dateTime().toString("yyyy-MM-dd HH:mm"))
                record.setValue("arrival_time", self.dateTimeEdit_arrival_time.dateTime().toString("yyyy-MM-dd HH:mm"))

                if not insert_model.setRecord(new_row, record):
                    MessageHelper.show_error(self, "Ошибка", "Не удалось установить данные в модель при добавлении")
                    return False

                if not insert_model.submitAll():
                    MessageHelper.show_error(self, "Ошибка",
                                             f"Не удалось сохранить изменения: {insert_model.lastError().text()}")
                    return False

                print("=== Добавление прошло успешно ===")
                return True

            else:
                # Редактирование существующей записи
                # Получаем ID по текущей строке из основной модели (с JOIN'ами)
                original_record = self.model.record(self.row)
                flight_id = original_record.value("id")

                # Создаем временную модель, работающую напрямую с таблицей flights
                edit_model = QSqlTableModel(self, self.db)
                edit_model.setTable("flights")
                edit_model.setFilter(f"id = {flight_id}")
                edit_model.select()

                if edit_model.rowCount() != 1:
                    MessageHelper.show_error(self, "Ошибка", f"Не удалось загрузить запись с id = {flight_id}")
                    return False

                record = edit_model.record(0)
                record.setValue("flight_number", self.lineEdit_flight.text())
                record.setValue("gate", self.lineEdit_gate.text())
                record.setValue("airline_id", self.comboBox_airline.currentData())
                record.setValue("aircraft_type_id", self.comboBox_aircraft_type.currentData())
                record.setValue("departure_airport_id", self.comboBox_departure.currentData())
                record.setValue("arrival_airport_id", self.comboBox_arrival.currentData())
                record.setValue("status_id", self.comboBox_status.currentData())
                record.setValue("departure_time",
                                self.dateTimeEdit_departure_time.dateTime().toString("yyyy-MM-dd HH:mm"))
                record.setValue("arrival_time", self.dateTimeEdit_arrival_time.dateTime().toString("yyyy-MM-dd HH:mm"))

                if not edit_model.setRecord(0, record):
                    MessageHelper.show_error(self, "Ошибка",
                                             f"Не удалось обновить запись: {edit_model.lastError().text()}")
                    return False

                if not edit_model.submitAll():
                    MessageHelper.show_error(self, "Ошибка",
                                             f"Не удалось сохранить изменения: {edit_model.lastError().text()}")
                    return False

                print("=== Редактирование прошло успешно ===")
                return True

        except Exception as e:
            print(f"Exception в apply_changes: {str(e)}")
            MessageHelper.show_error(self, "Ошибка", f"Произошла ошибка: {str(e)}")
            return False