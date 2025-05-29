from PyQt6.QtWidgets import QApplication
from gui.MainWindow import MainWindow
import sys

app = QApplication(sys.argv)
window = MainWindow()
window.show()
print("Запуск ГИ")
sys.exit(app.exec())