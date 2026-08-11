import subprocess
import sys

from PyQt6.QtGui import QFontDatabase, QIcon
from PyQt6.QtWidgets import QApplication

from nodebox.core import load_custom_fonts, resource_path, set_default_font
from nodebox.ui import EnhancedMainWindow


def start_ollama():
    """Start ollama serve in the background."""
    try:
        return subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        print("Error: Ollama is not installed or not in PATH.")
        return None


def main():
    ollama_process = start_ollama()

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(resource_path("assets/icons/favicon.png")))

    QFontDatabase.addApplicationFont(resource_path("assets/fonts/Poppins-Regular.ttf"))
    QFontDatabase.addApplicationFont(resource_path("assets/fonts/Poppins-Medium.ttf"))
    QFontDatabase.addApplicationFont(resource_path("assets/fonts/Poppins-SemiBold.ttf"))

    qss_file = resource_path("qss/dark.qss")
    with open(qss_file, "r") as file:
        app.setStyleSheet(file.read())

    load_custom_fonts()
    set_default_font(10)

    window = EnhancedMainWindow()
    window.show()
    exit_code = app.exec()

    if ollama_process:
        ollama_process.terminate()
        try:
            ollama_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            ollama_process.kill()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
