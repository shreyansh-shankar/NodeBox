from PyQt6.QtWidgets import ( #type: ignore
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox,
    QScrollArea, QGridLayout, QLabel, QSizePolicy, QFrame
)
from PyQt6.QtGui import QPixmap #type: ignore
from PyQt6.QtCore import Qt #type: ignore

from ui.model_card import ModelCard
from models_data import models

class BrowseModelsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Browse Models")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet("background-color: #121212;")

        main_layout = QVBoxLayout(self)

        # 🔍 Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search models...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border-radius: 8px;
                background-color: #1e1e1e;
                color: white;
                font-size: 14px;
            }
        """)
        self.search_input.textChanged.connect(self.update_grid)
        main_layout.addWidget(self.search_input)

        # 📜 Scroll Area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("border: none;")

        self.scroll_content = QWidget()
        self.grid = QGridLayout(self.scroll_content)
        self.grid.setSpacing(20)
        self.scroll.setWidget(self.scroll_content)

        main_layout.addWidget(self.scroll)

        self.update_grid()

    def update_grid(self):
        search_term = self.search_input.text().lower()
        for i in reversed(range(self.grid.count())):
            self.grid.itemAt(i).widget().deleteLater()

        filtered_models = [m for m in models if search_term in m["name"].lower()]
        for idx, model in enumerate(filtered_models):
            row, col = divmod(idx, 2)
            card = ModelCard(model)
            self.grid.addWidget(card, row, col)