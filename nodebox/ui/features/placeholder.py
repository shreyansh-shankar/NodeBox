from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QPainter, QPainterPath
from PyQt6.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QWidget


class PlaceholderWidget(QWidget):
    """Lightweight placeholder widget shown while lazy-loading tabs."""

    def __init__(self, feature_name: str, parent=None):
        super().__init__(parent)
        self.feature_name = feature_name
        self._init_ui()

    def _init_ui(self):
        self.setStyleSheet("background-color: #0A0C10;")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(10)

        spinner = QLabel()
        spinner.setFixedSize(40, 40)
        spinner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        spinner.setStyleSheet("""
            QLabel {
                background-color: rgba(99,102,241,0.15);
                border-radius: 20px;
                border: 2px solid #6366F1;
            }
        """)
        layout.addWidget(spinner, alignment=Qt.AlignmentFlag.AlignCenter)

        loading_label = QLabel(f"Loading {self.feature_name}...")
        loading_label.setFont(QFont("Poppins", 14, QFont.Weight.Medium))
        loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        loading_label.setStyleSheet("color: #4A5578; background: transparent;")
        layout.addWidget(loading_label)

        hint = QLabel("Click the tab to open this feature")
        hint.setFont(QFont("Poppins", 10))
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setStyleSheet("color: #252D42; background: transparent;")
        layout.addWidget(hint)


__all__ = ["PlaceholderWidget"]
