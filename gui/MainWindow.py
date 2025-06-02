from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow

from gui.SearchWindow import SearchWindow
from gui.ReferenceWindow import ReferenceWindow
from gui.AboutWindow import AboutWindow
from config.cfg import Config
from utils.database import DatabaseManager, SQLQueries
from utils.ui_helpers import TableManager, MessageHelper, FilterHelper, SearchConditionBuilder


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("gui/design/main.ui", self)

        # Инициализация
        Config("config.json")
        self.db = DatabaseManager.connect()

        # Создаем реляционную модель
        self.model = DatabaseManager.create_flights_relational_model(self.db)
        TableManager.setup_table_view(self.tableView, self.model)

        # Подключение сигналов
        self._connect_buttons()
        self._connect_menu_actions()

        # Обновляем статусбар при изменении данных
        self.model.rowsInserted.connect(self._update_status_info)
        self.model.rowsRemoved.connect(self._update_status_info)
        self.model.modelReset.connect(self._update_status_info)

        self._update_status_info()

    def _connect_buttons(self):
        """Подключение кнопок"""
        self.add_button.clicked.connect(self._add_new_row)
        self.delete_button.clicked.connect(self._delete_selected_row)
        self.search_button.clicked.connect(self._show_search_dialog)
        self.refresh_button.clicked.connect(self._refresh_table)

        # Если есть кнопка сброса фильтров
        if hasattr(self, 'clear_filters_button'):
            self.clear_filters_button.clicked.connect(self._clear_filters)

    def _add_new_row(self):
        """Добавление новой строки"""
        try:
            row = self.model.rowCount()
            if self.model.insertRow(row):
                # Устанавливаем курсор на новую строку
                index = self.model.index(row, 1)  # Номер рейса
                self.tableView.setCurrentIndex(index)
                self.tableView.edit(index)
            else:
                MessageHelper.show_error(self, "Ошибка", "Не удалось добавить новую запись")
        except Exception as e:
            MessageHelper.show_error(self, "Ошибка", f"Ошибка при добавлении: {e}")

    def _connect_menu_actions(self):
        """Подключение действий меню"""
        menu_actions = {
            self.actionAirlines: "airlines",
            self.actionAircraftTypes: "aircraft_types",
            self.actionAirports: "airports",
            self.actionStatuses: "statuses"
        }
        for action, table in menu_actions.items():
            action.triggered.connect(lambda checked, t=table: ReferenceWindow(t, self).exec())

    def _delete_selected_row(self):
        """Удаление выбранной строки"""
        row = self.tableView.currentIndex().row()
        if row < 0:
            MessageHelper.show_error(self, "Ошибка", "Не выбрана запись для удаления")
            return

        try:
            if self.model.removeRow(row):
                self.model.submitAll()
                if self.model.lastError().isValid():
                    MessageHelper.show_error(self, "Ошибка", f"Ошибка удаления: {self.model.lastError().text()}")
                    self.model.revertAll()
                else:
                    # Обновляем модель после успешного удаления
                    self.model.select()
            else:
                MessageHelper.show_error(self, "Ошибка", "Не удалось удалить запись")
        except Exception as e:
            MessageHelper.show_error(self, "Ошибка", f"Ошибка при удалении: {e}")

    def _show_search_dialog(self):
        dialog = SearchWindow(self)
        dialog.search_requested.connect(self._apply_filter)
        dialog.exec()

    def _apply_filters(self, filter_params):
        try:
            filter_string = SearchConditionBuilder.build_filter_string(filter_params)

            if filter_string:
                # Применяем фильтр к модели
                self.model.setFilter(filter_string)
            else:
                # Убираем фильтр, если условий нет
                self.model.setFilter("")

            # Обновляем модель
            self.model.select()

        except Exception as e:
            MessageHelper.show_error(self, "Ошибка", f"Ошибка применения фильтра: {e}")

    def _clear_filters(self):
        """Сброс всех фильтров"""
        self.model.clear_filters()
        self._update_status_info()

        if hasattr(self, 'statusbar'):
            self.statusbar.showMessage("Фильтры сброшены")

    def _refresh_table(self):
        self.model.setFilter("")
        self.model.select()

    def _update_status_info(self):
        """Обновление информации в статусбаре"""
        if hasattr(self, 'statusbar'):
            filtered_count = self.model.get_filtered_count()
            total_count = self.source_model.rowCount()

            if filtered_count == total_count:
                status_text = f"Всего записей: {total_count}"
            else:
                active_filters = len([v for v in self.model.filters.values() if v])
                status_text = f"Показано: {filtered_count} из {total_count} | Активных фильтров: {active_filters}"

            self.statusbar.showMessage(status_text)

    # Дополнительные методы для удобства работы с фильтрами

    def get_selected_row_data(self):
        """Получение данных выбранной строки"""
        proxy_index = self.tableView.currentIndex()
        if not proxy_index.isValid():
            return None

        source_index = self.model.mapToSource(proxy_index)
        if not source_index.isValid():
            return None

        row_data = {}
        for col in range(self.source_model.columnCount()):
            header = self.source_model.headerData(col, 1)  # Qt.Orientation.Horizontal = 1
            value = self.source_model.data(self.source_model.index(source_index.row(), col))
            row_data[str(header)] = value

        return row_data

    def set_quick_filter(self, field_name, value):
        """Быстрая установка фильтра (можно использовать для контекстного меню)"""
        current_filters = self.model.filters.copy()
        current_filters[field_name] = value
        self.model.set_filters(current_filters)
        self._update_status_info()

    def export_filtered_data(self):
        """Экспорт отфильтрованных данных (заглушка для будущей реализации)"""
        filtered_count = self.model.get_filtered_count()
        MessageHelper.show_info(
            self,
            "Экспорт",
            f"Будет экспортировано {filtered_count} записей"
        )