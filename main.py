from PyQt6.QtWidgets import QApplication
from gui.MainWindow import MainWindow
from data.db import create_db
import sys

print("Проверка БД")
db = create_db()

app = QApplication(sys.argv)
window = MainWindow()
window.show()
print("Запуск приложения")
sys.exit(app.exec())