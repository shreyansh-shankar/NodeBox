"""
Node Templates Widget - Professionally styled with Feather icons and detailed node dialog
"""

import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import (
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from utils.paths import resource_path


class NodeDetailsDialog(QDialog):
    """Dialog showing detailed nodes in a category"""

    def __init__(self, category_data, parent=None):
        super().__init__(parent)
        self.category_data = category_data
        self.setWindowTitle(f"{category_data['title']} - Available Nodes")
        self.setMinimumSize(600, 500)
        self.setup_ui()

    def get_icon(self, icon_name):
        """Get white icon from assets"""
        icon_path = resource_path(f"assets/icons/{icon_name}.svg")
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        return QIcon()

    def setup_ui(self):
        """Setup dialog UI - Match main window style"""
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header with icon and title - Match Home tab style
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        icon_label = QLabel()
        icon = self.get_icon(self.category_data["icon"])
        if not icon.isNull():
            icon_label.setPixmap(icon.pixmap(36, 36))
        header_layout.addWidget(icon_label)

        title = QLabel(self.category_data["title"])
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #ffffff;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Description - Match Home tab typography
        desc = QLabel(self.category_data["description"])
        desc.setFont(QFont("Segoe UI", 11))
        desc.setStyleSheet("color: #a0a0a0; margin-bottom: 12px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Nodes list
        nodes_label = QLabel("Available Nodes:")
        nodes_label.setFont(QFont("Segoe UI", 13, QFont.Weight.DemiBold))
        nodes_label.setStyleSheet("color: #ffffff; margin-top: 8px;")
        layout.addWidget(nodes_label)

        # List widget for nodes
        self.node_list = QListWidget()
        self.node_list.setStyleSheet(
            """
            QListWidget {
                background-color: #1e1e1e;
                border: 1px solid #3e3e42;
                border-radius: 4px;
                padding: 8px;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #2d2d30;
                border-radius: 4px;
                margin: 2px 0px;
                color: #e0e0e0;
            }
            QListWidget::item:hover {
                background-color: #2d2d30;
            }
            QListWidget::item:selected {
                background-color: #0e639c;
                color: #ffffff;
            }
        """
        )

        # Add nodes to list
        for node in self.category_data["nodes"]:
            item = QListWidgetItem(self.get_icon("package"), f"  {node['name']}")
            item.setFont(QFont("Segoe UI", 11))
            # Store node description as tooltip
            item.setToolTip(node["description"])
            self.node_list.addItem(item)

        layout.addWidget(self.node_list)

        # Button row - Match Home tab button style
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_button = QPushButton("  Close")
        close_button.setIcon(self.get_icon("x"))
        close_button.setFont(QFont("Segoe UI", 11))
        close_button.setMinimumHeight(36)
        close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        close_button.setStyleSheet(
            """
            QPushButton {
                padding: 8px 24px;
                background-color: #3e3e42;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #4e4e52;
            }
            QPushButton:pressed {
                background-color: #2e2e32;
            }
        """
        )
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.setStyleSheet("QDialog { background-color: #252526; }")


class NodeTemplateWidget(QWidget):
    """Template gallery matching Home tab design with Feather icons"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def get_icon(self, icon_name):
        """Get white icon from assets"""
        icon_path = resource_path(f"assets/icons/{icon_name}.svg")
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        return QIcon()

    def setup_ui(self):
        """Setup the UI with modern styling matching Home tab"""
        # Main layout - Match Home tab spacing
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        # Title section - Match Home tab typography
        title = QLabel("Node Templates")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #ffffff;")
        main_layout.addWidget(title)

        subtitle = QLabel("Pre-built automation nodes ready to use")
        subtitle.setFont(QFont("Segoe UI", 13))
        subtitle.setStyleSheet("color: #a0a0a0; margin-bottom: 16px;")
        main_layout.addWidget(subtitle)

        # Scroll area for templates
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(
            """
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #2d2d30;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #3e3e42;
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #4e4e52;
            }
        """
        )

        # Container for template cards - Match Home tab style
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        self.grid_layout = QGridLayout(scroll_content)
        self.grid_layout.setSpacing(16)  # Consistent spacing
        self.grid_layout.setContentsMargins(
            0, 0, 16, 0
        )  # Add right margin for scrollbar

        # Add template categories
        self.create_template_cards()

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        self.setLayout(main_layout)
        self.setStyleSheet("QWidget { background-color: #252526; }")

    def get_template_data(self):
        """Get all template categories with detailed node information"""
        return [
            {
                "title": "Data Processing",
                "description": "Extract, transform, and load data between sources",
                "icon": "bar-chart-2",
                "count": 4,
                "nodes": [
                    {
                        "name": "CSV Reader",
                        "description": "Read data from CSV files with customizable delimiters",
                    },
                    {
                        "name": "JSON Parser",
                        "description": "Parse and extract data from JSON structures",
                    },
                    {
                        "name": "Data Filter",
                        "description": "Filter data based on custom conditions",
                    },
                    {
                        "name": "Data Merger",
                        "description": "Combine multiple data sources into one",
                    },
                ],
            },
            {
                "title": "File Operations",
                "description": "File and folder manipulation tools",
                "icon": "folder",
                "count": 4,
                "nodes": [
                    {
                        "name": "File Reader",
                        "description": "Read content from text and binary files",
                    },
                    {
                        "name": "File Writer",
                        "description": "Write data to files with multiple formats",
                    },
                    {
                        "name": "Directory Scanner",
                        "description": "Scan and list files in directories recursively",
                    },
                    {
                        "name": "File Mover",
                        "description": "Move, copy, or rename files and folders",
                    },
                ],
            },
            {
                "title": "Web Automation",
                "description": "Web scraping and API integration",
                "icon": "globe",
                "count": 4,
                "nodes": [
                    {
                        "name": "HTTP Request",
                        "description": "Make HTTP/HTTPS requests with custom headers",
                    },
                    {
                        "name": "Web Scraper",
                        "description": "Extract data from websites using CSS selectors",
                    },
                    {
                        "name": "API Caller",
                        "description": "Call REST APIs with authentication support",
                    },
                    {
                        "name": "HTML Parser",
                        "description": "Parse and extract data from HTML content",
                    },
                ],
            },
            {
                "title": "Text Processing",
                "description": "Text manipulation and analysis",
                "icon": "type",
                "count": 4,
                "nodes": [
                    {
                        "name": "Text Splitter",
                        "description": "Split text by delimiters or patterns",
                    },
                    {
                        "name": "Regex Matcher",
                        "description": "Match and extract text using regular expressions",
                    },
                    {
                        "name": "Text Combiner",
                        "description": "Concatenate multiple text inputs",
                    },
                    {
                        "name": "Formatter",
                        "description": "Format text using templates and variables",
                    },
                ],
            },
            {
                "title": "AI & ML",
                "description": "AI models and machine learning",
                "icon": "cpu",
                "count": 4,
                "nodes": [
                    {
                        "name": "Ollama LLM",
                        "description": "Run local LLM models with Ollama",
                    },
                    {
                        "name": "Image Generator",
                        "description": "Generate images using AI models",
                    },
                    {
                        "name": "Sentiment Analysis",
                        "description": "Analyze sentiment in text data",
                    },
                    {
                        "name": "Classifier",
                        "description": "Classify data using trained models",
                    },
                ],
            },
            {
                "title": "Notifications",
                "description": "Multi-platform alert systems",
                "icon": "bell",
                "count": 4,
                "nodes": [
                    {
                        "name": "Email Sender",
                        "description": "Send emails via SMTP with attachments",
                    },
                    {
                        "name": "Slack Bot",
                        "description": "Post messages to Slack channels",
                    },
                    {
                        "name": "SMS Sender",
                        "description": "Send SMS messages via Twilio or similar",
                    },
                    {
                        "name": "Discord Webhook",
                        "description": "Send notifications to Discord channels",
                    },
                ],
            },
        ]

    def create_template_cards(self):
        """Create template category cards with Feather icons"""
        templates = self.get_template_data()

        row = 0
        col = 0
        max_cols = 2  # 2 columns for better sizing

        for template in templates:
            card = self.create_template_card(template)
            self.grid_layout.addWidget(card, row, col)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

        # Add stretch to push cards to top
        self.grid_layout.setRowStretch(row + 1, 1)

    def create_template_card(self, template_data):
        """Create a template card with Feather icon - Match Home tab card style"""
        card = QFrame()
        card.setFixedHeight(200)  # Increased height for better spacing
        card.setStyleSheet(
            """
            QFrame {
                background-color: #1e1e1e;
                border: 1px solid #3e3e42;
                border-radius: 6px;
            }
            QFrame:hover {
                border: 1px solid #007acc;
                background-color: #252526;
            }
        """
        )

        layout = QVBoxLayout()
        layout.setSpacing(12)  # Match Home tab spacing
        layout.setContentsMargins(20, 18, 20, 18)  # Match Home tab padding

        # Icon and title row - Match Home tab style
        title_row = QHBoxLayout()
        title_row.setSpacing(12)

        # Icon label with actual icon
        icon_label = QLabel()
        icon = self.get_icon(template_data["icon"])
        if not icon.isNull():
            icon_label.setPixmap(
                icon.pixmap(32, 32)
            )  # Larger icon for better visibility
        title_row.addWidget(icon_label)

        title_label = QLabel(template_data["title"])
        title_label.setFont(
            QFont("Segoe UI", 14, QFont.Weight.Bold)
        )  # Match Home tab font size
        title_label.setStyleSheet("color: #ffffff;")
        title_row.addWidget(title_label)
        title_row.addStretch()

        layout.addLayout(title_row)

        # Description - Match Home tab typography
        desc_label = QLabel(template_data["description"])
        desc_label.setFont(QFont("Segoe UI", 11))  # Match Home tab font size
        desc_label.setStyleSheet("color: #a0a0a0;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        # Node count badge - Better styling
        count_label = QLabel(f"{template_data['count']} nodes available")
        count_label.setFont(QFont("Segoe UI", 9))
        count_label.setStyleSheet(
            """
            color: #007acc;
            background-color: rgba(14, 99, 156, 0.15);
            padding: 6px 10px;
            border-radius: 4px;
        """
        )
        layout.addWidget(count_label)

        layout.addStretch()

        # Explore button - Match Home tab button style
        explore_button = QPushButton("  View Nodes")
        explore_button.setIcon(self.get_icon("package"))
        explore_button.setFont(QFont("Segoe UI", 10))
        explore_button.setMinimumHeight(36)  # Match Home tab button height
        explore_button.setCursor(Qt.CursorShape.PointingHandCursor)
        explore_button.setStyleSheet(
            """
            QPushButton {
                padding: 8px 16px;
                background-color: #0e639c;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:pressed {
                background-color: #0d5a8f;
            }
        """
        )
        explore_button.clicked.connect(
            lambda checked, cat=template_data: self.explore_category(cat)
        )
        layout.addWidget(explore_button)

        card.setLayout(layout)
        return card

    def explore_category(self, category_data):
        """Open dialog showing detailed nodes"""
        dialog = NodeDetailsDialog(category_data, self)
        dialog.exec()
