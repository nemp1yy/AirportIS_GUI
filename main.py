from PyQt6.QtWidgets import QApplication
from gui.MainWindow import MainWindow
from data.db_sqlite import create_db
from config.cfg import Config
import sys

print("Проверка БД...", end=" ")

db = create_db()
cfg = Config("config.json")

type_db = cfg.get_type_db()

if type_db == "sqlite":
    print("Используется SQLite")
elif type_db == "myriadb":
    print("Используется MariaDB")
else:
    print("Неизвестный тип БД")
    exit(1)

app = QApplication(sys.argv)
window = MainWindow()
window.show()
print("Запуск приложения")
sys.exit(app.exec())