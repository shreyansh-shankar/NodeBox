import os
import sys

from PyQt6.QtGui import QFont, QFontDatabase
from PyQt6.QtWidgets import QApplication
from utils.paths import resource_path

def load_custom_fonts():
    font_dir = resource_path("assets/fonts")  # handle both cases
    if not os.path.exists(font_dir):
        print(f"[WARN] Font dir not found: {font_dir}")
        return

    for font_file in os.listdir(font_dir):
        if font_file.endswith(".ttf") or font_file.endswith(".otf"):
            font_path = os.path.join(font_dir, font_file)
            font_id = QFontDatabase.addApplicationFont(font_path)
            if font_id == -1:
                print(f"[ERROR] Failed to load font: {font_file}")
            else:
                print(f"[OK] Loaded font: {font_file}")


def set_default_font(size: int = 10):
    font = QFont("Poppins")
    font.setPointSize(size)
    QApplication.setFont(font)
