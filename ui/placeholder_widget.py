"""
Placeholder Widget for Lazy Loading Tabs
"""
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget


class PlaceholderWidget(QWidget):
    """Lightweight placeholder widget for lazy-loaded tabs"""

    def __init__(self, feature_name: str, parent=None):
        super().__init__(parent)
        self.feature_name = feature_name
        self.init_ui()

    def init_ui(self):
        """Initialize minimal placeholder UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Loading message
        loading_label = QLabel(f"Loading {self.feature_name}...")
        loading_label.setFont(QFont("Poppins", 14))
        loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        loading_label.setStyleSheet("color: #888; padding: 20px;")

        layout.addWidget(loading_label)
