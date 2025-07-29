from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout

class BrowseModelsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Browse Models")
        self.setFixedSize(1200, 800)

        layout = QVBoxLayout()
        label = QLabel("This is the Browse Models window (blank for now).")
        label.setStyleSheet("font-size: 16px; color: #444;")
        layout.addWidget(label)

        self.setLayout(layout)