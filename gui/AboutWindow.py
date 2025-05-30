from PyQt6 import uic, QtCore
from PyQt6.QtWidgets import QDialog
from utils.ui_helpers import FormUtils, SearchConditionBuilder, MessageHelper

class AboutWindow(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("gui/design/about.ui", self)

