"""
Filter Window - Dynamic filtering for models with signal-based communication
"""
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from utils.screen_manager import ScreenManager


class FilterCriteria:
    """Data class to hold filter criteria"""

    def __init__(self):
        self.tags = set()
        self.companies = set()
        self.sizes = set()

    def is_empty(self):
        """Check if any filters are active"""
        return not any([self.tags, self.companies, self.sizes])

    def clear(self):
        """Clear all filters"""
        self.tags.clear()
        self.companies.clear()
        self.sizes.clear()

    def __repr__(self):
        return f"FilterCriteria(tags={self.tags}, companies={self.companies}, sizes={self.sizes})"


class FilterWindow(QWidget):
    # Signal emitted when filters are applied
    filters_applied = pyqtSignal(FilterCriteria)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Filter Options")

        # Use dynamic window sizing for dialog
        width, height = ScreenManager.get_dialog_window_size(
            width_percentage=0.2, height_percentage=0.25, min_width=280, min_height=250
        )

        # Center the window
        x, y = ScreenManager.calculate_window_position(width, height, center=True)
        self.setGeometry(x, y, width, height)
        self.setStyleSheet("background-color: #1e1e1e; color: white;")

        # Store checkboxes for access
        self.tag_checkboxes = {}
        self.company_checkboxes = {}
        self.size_checkboxes = {}

        main_layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(
            """
            QTabWidget::pane {
                border: none;
            }
            QTabBar::tab {
                background: #2e2e2e;
                color: white;
                padding: 8px;
                min-width: 80px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background: #3e3e3e;
            }
        """
        )

        # Create tabs with stored checkboxes
        tags_tab, self.tag_checkboxes = self.create_scrollable_tab(
            ["Chat", "Instruct", "Code", "Fun"]
        )
        self.tabs.addTab(tags_tab, "Tags")

        company_tab, self.company_checkboxes = self.create_scrollable_tab(
            ["DeepSeek", "Mistral", "Hermes", "Llama", "Phi"]
        )
        self.tabs.addTab(company_tab, "Company")

        size_tab, self.size_checkboxes = self.create_scrollable_tab(
            ["Small", "Medium", "Large"]
        )
        self.tabs.addTab(size_tab, "Size")

        main_layout.addWidget(self.tabs)

        # Buttons at the bottom
        button_layout = QHBoxLayout()
        
        clear_btn = QPushButton("Clear All")
        clear_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #757575;
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #9e9e9e;
            }
        """
        )
        clear_btn.clicked.connect(self.clear_filters)

        apply_btn = QPushButton("Apply")
        apply_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #2e7d32;
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #388e3c;
            }
        """
        )
        apply_btn.clicked.connect(self.apply_filters)

        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #c62828;
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e53935;
            }
        """
        )
        close_btn.clicked.connect(self.close)

        button_layout.addWidget(clear_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        button_layout.addStretch()
        button_layout.addWidget(apply_btn, alignment=Qt.AlignmentFlag.AlignRight)
        button_layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)
        main_layout.addLayout(button_layout)

    def create_scrollable_tab(self, items):
        """Create a scrollable tab and return it with checkboxes dict"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content_widget = QFrame()
        content_layout = QVBoxLayout(content_widget)
        
        checkboxes = {}
        for item in items:
            cb = QCheckBox(item)
            cb.setStyleSheet(
                """
                QCheckBox {
                    color: white;
                    spacing: 8px;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                    border: 2px solid #3e3e42;
                    border-radius: 3px;
                    background-color: #2d2d30;
                }
                QCheckBox::indicator:checked {
                    background-color: #2e7d32;
                    border-color: #2e7d32;
                }
                QCheckBox::indicator:hover {
                    border-color: #388e3c;
                }
            """
            )
            content_layout.addWidget(cb)
            checkboxes[item] = cb
        
        content_layout.addStretch()

        scroll_area.setWidget(content_widget)
        return scroll_area, checkboxes

    def collect_filter_criteria(self):
        """Collect current filter selections into FilterCriteria object"""
        criteria = FilterCriteria()

        # Collect tag filters
        for tag, checkbox in self.tag_checkboxes.items():
            if checkbox.isChecked():
                criteria.tags.add(tag)

        # Collect company filters
        for company, checkbox in self.company_checkboxes.items():
            if checkbox.isChecked():
                criteria.companies.add(company)

        # Collect size filters
        for size, checkbox in self.size_checkboxes.items():
            if checkbox.isChecked():
                criteria.sizes.add(size)

        return criteria

    def apply_filters(self):
        """Apply current filter selections and emit signal"""
        criteria = self.collect_filter_criteria()
        print(f"Applying filters: {criteria}")  # Debug output
        self.filters_applied.emit(criteria)
        self.close()

    def clear_filters(self):
        """Clear all filter selections"""
        # Uncheck all checkboxes
        for checkbox in self.tag_checkboxes.values():
            checkbox.setChecked(False)
        for checkbox in self.company_checkboxes.values():
            checkbox.setChecked(False)
        for checkbox in self.size_checkboxes.values():
            checkbox.setChecked(False)

        # Emit empty criteria
        criteria = FilterCriteria()
        print("Clearing all filters")  # Debug output
        self.filters_applied.emit(criteria)
