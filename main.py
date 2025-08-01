import sys
from PyQt6.QtWidgets import QApplication #type: ignore
from PyQt6.QtGui import QFontDatabase #type: ignore
from utils.font_loader import load_custom_fonts, set_default_font
from ui.main_window import MainWindow
import utils.paths
import os

def main():
    app = QApplication(sys.argv)

    # Load local Poppins font
    QFontDatabase.addApplicationFont("assets/fonts/Poppins-Regular.ttf")
    QFontDatabase.addApplicationFont("assets/fonts/Poppins-Medium.ttf")
    QFontDatabase.addApplicationFont("assets/fonts/Poppins-SemiBold.ttf")

    # 2. Apply dark stylesheet
    with open(os.path.join("qss", "dark.qss"), "r") as file:
        app.setStyleSheet(file.read())

    # Load fonts and set default
    load_custom_fonts()
    set_default_font(10)  # Default size

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
