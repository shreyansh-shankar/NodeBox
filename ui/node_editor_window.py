from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal

class NodeEditorWindow(QWidget):

    closed = pyqtSignal()

    def __init__(self, automation_name):
        super().__init__()
        self.setWindowTitle(f"Automation: {automation_name}")
        self.setMinimumSize(1600, 900)
        self.setStyleSheet("background-color: #121212; color: white;")

        layout = QVBoxLayout(self)
        label = QLabel(f"Node Editor for: {automation_name}")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
    
    def closeEvent(self, event):
        self.closed.emit()
        event.accept()
