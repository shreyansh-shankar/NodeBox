from PyQt6.QtWidgets import ( #type: ignore
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QScrollArea, QGridLayout, QPushButton
)
from PyQt6.QtGui import QPixmap #type: ignore
from PyQt6.QtCore import Qt #type: ignore

from ui.model_card import ModelCard
from models_data import models
from ui.filter_window import FilterWindow
from ui.downlaod_manager import DownloadManager

class BrowseModelsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Browse Models")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet("background-color: #121212;")

        self._downloads = []

        main_layout = QVBoxLayout(self)

        # 🔍 Search bar + Filter button in one row
        search_filter_layout = QHBoxLayout()

        # Search bar
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
        search_filter_layout.addWidget(self.search_input, stretch=1)  # take most space

        # Filter button
        self.filter_button = QPushButton("Filter")
        self.filter_button.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background-color: #2e2e2e;
                color: white;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3e3e3e;
            }
        """)
        self.filter_button.clicked.connect(self.open_filter_window)
        search_filter_layout.addWidget(self.filter_button)
        main_layout.addLayout(search_filter_layout)

        # 📜 Scroll Area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("border: none;")

        self.scroll_content = QWidget()
        self.grid = QGridLayout(self.scroll_content)
        self.grid.setSpacing(20)
        self.scroll.setWidget(self.scroll_content)

        # Hide scrollbars but keep scrolling functionality
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Optional: If you want smoother scrolling via mouse
        self.scroll.setStyleSheet("""
            QScrollArea {
                border: none;
            }
            QScrollBar:vertical, QScrollBar:horizontal {
                width: 0px;
                height: 0px;
                background: transparent;
            }
        """)

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
            card.downloadRequested.connect(self.open_download_manager)
            self.grid.addWidget(card, row, col)

    def open_filter_window(self):
        self.filter_window = FilterWindow(self)
        self.filter_window = FilterWindow(self)  # Pass parent to keep it tied
        # Calculate the global position of the filter button
        button_pos = self.filter_button.mapToGlobal(self.filter_button.rect().bottomLeft())
        self.filter_window.move(button_pos.x() - 250 , button_pos.y())  # Position it just below the button
        self.filter_window.show()

    def open_download_manager(self, model):
        sizes = model.get("sizes", ["latest"])
        dlg = DownloadManager(model_name=model["name"], sizes=sizes, parent=self)
        self._downloads.append(dlg)  # prevent GC
        dlg.exec()  # use exec