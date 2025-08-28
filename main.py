from PyQt6.QtWidgets import QApplication #type: ignore
from PyQt6.QtGui import QFontDatabase #type: ignore

from utils.font_loader import load_custom_fonts, set_default_font
from ui.main_window import MainWindow
import utils.paths

import os, sys, subprocess

def resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works in dev and PyInstaller bundle"""
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS  # folder where PyInstaller extracts files
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def start_ollama():
    """Start ollama serve in the background."""
    try:
        return subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,  # Hide logs, or use sys.stdout to show them
            stderr=subprocess.DEVNULL
        )
    except FileNotFoundError:
        print("Error: Ollama is not installed or not in PATH.")
        return None

def main():

    # Start Ollama first
    ollama_process = start_ollama()

    app = QApplication(sys.argv)

    # Load local Poppins font
    QFontDatabase.addApplicationFont("assets/fonts/Poppins-Regular.ttf")
    QFontDatabase.addApplicationFont("assets/fonts/Poppins-Medium.ttf")
    QFontDatabase.addApplicationFont("assets/fonts/Poppins-SemiBold.ttf")

    # 2. Apply dark stylesheet
    qss_file = resource_path("qss/dark.qss")
    with open(qss_file, "r") as file:
        app.setStyleSheet(file.read())

    # Load fonts and set default
    load_custom_fonts()
    set_default_font(10)  # Default size

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


    # Cleanup after Qt loop finishes
    if ollama_process:
        ollama_process.terminate()
        try:
            ollama_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            ollama_process.kill()

    sys.exit(exit_code)

if __name__ == "__main__":
    main()
