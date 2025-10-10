from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from browsemodels_manager.downlaod_manager import DownloadManager
from browsemodels_manager.filter_window import FilterCriteria, FilterWindow
from browsemodels_manager.model_card import ModelCard
from models_data import models
from utils.screen_manager import ScreenManager


class BrowseModelsWindow(QWidget):
    def __init__(self):
        # Set busy cursor at the start (before loading models)
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        try:
            super().__init__()
            self.setWindowTitle("Browse Models")

            # Use dynamic window sizing based on screen resolution
            x, y, width, height = ScreenManager.get_browse_window_geometry()
            self.setGeometry(x, y, width, height)
            self.setStyleSheet("background-color: #121212;")

            self._downloads = []
            self.filter_window = None
            self.current_filters = FilterCriteria()  # Store active filters

            main_layout = QVBoxLayout(self)

            #  Search bar + Filter button in one row
            search_filter_layout = QHBoxLayout()

            # Search bar
            self.search_input = QLineEdit()
            self.search_input.setPlaceholderText("Search models...")
            self.search_input.setStyleSheet(
                """
                QLineEdit {
                    padding: 10px;
                    border-radius: 8px;
                    background-color: #1e1e1e;
                    color: white;
                    font-size: 14px;
                }
            """
            )
            self.search_input.textChanged.connect(self.update_grid)
            search_filter_layout.addWidget(self.search_input, stretch=1)

            # Filter button
            self.filter_button = QPushButton("Filter")
            self.filter_button.setStyleSheet(
                """
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
            """
            )
            self.filter_button.clicked.connect(self.open_filter_window)
            search_filter_layout.addWidget(self.filter_button)

            # Clear filters button (hidden initially)
            self.clear_filter_button = QPushButton("Clear Filters")
            self.clear_filter_button.setStyleSheet(
                """
                QPushButton {
                    padding: 10px 20px;
                    background-color: #c62828;
                    color: white;
                    border-radius: 8px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #e53935;
                }
            """
            )
            self.clear_filter_button.clicked.connect(self.clear_all_filters)
            self.clear_filter_button.setVisible(False)
            search_filter_layout.addWidget(self.clear_filter_button)

            main_layout.addLayout(search_filter_layout)

            # Filter status label
            self.filter_status_label = QLabel("Showing all models")
            self.filter_status_label.setStyleSheet(
                """
                QLabel {
                    color: #888888;
                    font-size: 12px;
                    padding: 5px;
                }
            """
            )
            main_layout.addWidget(self.filter_status_label)

            #  Scroll Area
            self.scroll = QScrollArea()
            self.scroll.setWidgetResizable(True)
            self.scroll.setStyleSheet("border: none;")

            self.scroll_content = QWidget()
            self.grid = QGridLayout(self.scroll_content)
            self.grid.setSpacing(20)
            self.scroll.setWidget(self.scroll_content)

            # Hide scrollbars but keep scrolling functionality
            self.scroll.setVerticalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )
            self.scroll.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )

            self.scroll.setStyleSheet(
                """
                QScrollArea {
                    border: none;
                }
                QScrollBar:vertical, QScrollBar:horizontal {
                    width: 0px;
                    height: 0px;
                    background: transparent;
                }
            """
            )

            main_layout.addWidget(self.scroll)

            # This loads all the model cards (potentially slow)
            self.update_grid()

        finally:
            # Restore cursor after window is loaded
            QApplication.restoreOverrideCursor()

    def model_matches_filter(self, model, criteria):
        """Check if a model matches the current filter criteria"""
        # If no filters active, show all
        if criteria.is_empty():
            return True

        # Check tags
        if criteria.tags:
            model_tags = {tag.lower() for tag in model.get("tags", [])}
            if not criteria.tags.intersection(model_tags):
                return False

        # Check company (match against model name)
        if criteria.companies:
            model_name_lower = model.get("name", "").lower()
            company_match = any(
                company in model_name_lower for company in criteria.companies
            )
            if not company_match:
                return False

        # Check size (you can enhance this based on your model data)
        if criteria.sizes:
            # Example: check if "small", "medium", or "large" matches
            # You might want to add size info to your models_data.py
            model_sizes = model.get("sizes", [])
            if model_sizes:
                # Simple heuristic: check first size
                first_size = str(model_sizes[0]).lower()
                size_match = any(
                    size_keyword in first_size for size_keyword in criteria.sizes
                )
                if not size_match:
                    return False

        return True

    def update_grid(self):
        """Update the grid with filtered and searched models"""
        search_term = self.search_input.text().lower()

        # Clear existing cards
        for i in reversed(range(self.grid.count())):
            widget = self.grid.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Apply search filter
        filtered_models = [m for m in models if search_term in m["name"].lower()]

        # Apply other filters
        filtered_models = [
            m
            for m in filtered_models
            if self.model_matches_filter(m, self.current_filters)
        ]

        # Update status label
        total_count = len(models)
        filtered_count = len(filtered_models)

        if filtered_count == total_count and not search_term:
            self.filter_status_label.setText("Showing all models")
        else:
            self.filter_status_label.setText(
                f"Showing {filtered_count} of {total_count} models"
            )

        # Show/hide clear button based on active filters
        self.clear_filter_button.setVisible(
            not self.current_filters.is_empty() or bool(search_term)
        )

        # Add filtered model cards to grid
        if filtered_count == 0:
            # Show "no results" message
            no_results_label = QLabel("No models match your filters")
            no_results_label.setStyleSheet(
                """
                QLabel {
                    color: #888888;
                    font-size: 16px;
                    padding: 50px;
                }
            """
            )
            no_results_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.grid.addWidget(no_results_label, 0, 0, 1, 2)
        else:
            for idx, model in enumerate(filtered_models):
                row, col = divmod(idx, 2)
                card = ModelCard(model)
                card.downloadRequested.connect(self.open_download_manager)
                self.grid.addWidget(card, row, col)

    def open_filter_window(self):
        """Open the filter window and connect signals"""
        if self.filter_window is None:
            self.filter_window = FilterWindow(self)
            # Connect the filters_applied signal
            self.filter_window.filters_applied.connect(self.on_filters_applied)

        # Calculate the global position of the filter button
        button_pos = self.filter_button.mapToGlobal(
            self.filter_button.rect().bottomLeft()
        )
        self.filter_window.move(button_pos.x() - 250, button_pos.y())
        self.filter_window.show()
        self.filter_window.raise_()
        self.filter_window.activateWindow()

    def on_filters_applied(self, criteria):
        """Handle filter application from filter window"""
        print(f"Filters applied: {criteria}")  # Debug output
        self.current_filters = criteria
        self.update_grid()

    def clear_all_filters(self):
        """Clear all filters and search"""
        self.current_filters.clear()
        self.search_input.clear()
        if self.filter_window:
            self.filter_window.clear_filters()
        self.update_grid()

    def open_download_manager(self, model):
        """Open download manager dialog"""
        sizes = model.get("sizes", ["latest"])
        dlg = DownloadManager(model_name=model["name"], sizes=sizes, parent=self)
        self._downloads.append(dlg)  # prevent GC
        dlg.exec()
