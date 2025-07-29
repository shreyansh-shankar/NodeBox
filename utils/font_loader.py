from PyQt6.QtGui import QFontDatabase, QFont
from PyQt6.QtWidgets import QApplication
import os

def load_custom_fonts():
    font_dir = os.path.join(os.path.dirname(__file__), '..', 'assets', 'fonts')
    for font_file in os.listdir(font_dir):
        if font_file.endswith(".ttf"):
            font_path = os.path.join(font_dir, font_file)
            QFontDatabase.addApplicationFont(font_path)

def set_default_font(size: int = 10):
    font = QFont("Poppins")
    font.setPointSize(size)
    QApplication.setFont(font)
