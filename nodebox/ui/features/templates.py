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

from nodebox.core.paths import resource_path


class NodeDetailsDialog(QDialog):
    def __init__(self, category_data, parent=None):
        super().__init__(parent)
        self.category_data = category_data
        self.setWindowTitle(f"{category_data['title']} - Available Nodes")
        self.setMinimumSize(640, 520)
        self.setStyleSheet("QDialog { background-color: #121418; }")
        self.setup_ui()

    def get_icon(self, icon_name):
        icon_path = resource_path(f"assets/icons/{icon_name}.svg")
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        return QIcon()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(14)

        icon_label = QLabel()
        icon = self.get_icon(self.category_data["icon"])
        if not icon.isNull():
            icon_label.setPixmap(icon.pixmap(36, 36))
        header_layout.addWidget(icon_label)

        title = QLabel(self.category_data["title"])
        title.setFont(QFont("Poppins", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #F9FAFB;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        desc = QLabel(self.category_data["description"])
        desc.setFont(QFont("Poppins", 11))
        desc.setStyleSheet("color: #9CA3AF; margin-bottom: 12px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        nodes_label = QLabel("Available Nodes:")
        nodes_label.setFont(QFont("Poppins", 13, QFont.Weight.Bold))
        nodes_label.setStyleSheet("color: #818CF8; margin-top: 8px;")
        layout.addWidget(nodes_label)

        self.node_list = QListWidget()
        self.node_list.setStyleSheet(
            """
            QListWidget {
                background-color: #1A1D24;
                border: 1px solid #2E3444;
                border-radius: 10px;
                padding: 10px;
            }
            QListWidget::item {
                padding: 12px 14px;
                border-bottom: 1px solid #232833;
                border-radius: 6px;
                margin: 2px 0px;
                color: #F9FAFB;
            }
            QListWidget::item:hover {
                background-color: #222733;
            }
            QListWidget::item:selected {
                background-color: #4F46E5;
                color: #FFFFFF;
            }
        """
        )

        for node in self.category_data["nodes"]:
            item = QListWidgetItem(self.get_icon("package"), f"  {node['name']}")
            item.setFont(QFont("Poppins", 11))
            item.setToolTip(node["description"])
            self.node_list.addItem(item)

        layout.addWidget(self.node_list)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_button = QPushButton("  Close")
        close_button.setIcon(self.get_icon("x"))
        close_button.setFont(QFont("Poppins", 11, QFont.Weight.Bold))
        close_button.setMinimumHeight(40)
        close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        close_button.setStyleSheet(
            """
            QPushButton {
                padding: 8px 24px;
                background-color: #222733;
                color: white;
                border: 1px solid #2E3444;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #2A303F;
                border-color: #6366F1;
            }
        """
        )
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)


class NodeTemplateWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def get_icon(self, icon_name):
        icon_path = resource_path(f"assets/icons/{icon_name}.svg")
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        return QIcon()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(28, 28, 28, 28)
        main_layout.setSpacing(20)

        title = QLabel("Node Templates Gallery")
        title.setFont(QFont("Poppins", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: #F9FAFB;")
        main_layout.addWidget(title)

        subtitle = QLabel("Pre-built node templates ready to integrate into your automations")
        subtitle.setFont(QFont("Poppins", 13))
        subtitle.setStyleSheet("color: #9CA3AF; margin-bottom: 12px;")
        main_layout.addWidget(subtitle)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        self.grid_layout = QGridLayout(scroll_content)
        self.grid_layout.setSpacing(20)
        self.grid_layout.setContentsMargins(0, 0, 12, 0)

        self.create_template_cards()

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        self.setLayout(main_layout)
        self.setStyleSheet("QWidget { background-color: #121418; }")

    def get_template_data(self):
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
        templates = self.get_template_data()
        row = 0
        col = 0
        max_cols = 2

        for template in templates:
            card = self.create_template_card(template)
            self.grid_layout.addWidget(card, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1

        self.grid_layout.setRowStretch(row + 1, 1)

    def create_template_card(self, template_data):
        card = QFrame()
        card.setFixedHeight(210)
        card.setStyleSheet(
            """
            QFrame {
                background-color: #1A1D24;
                border: 1px solid #2E3444;
                border-radius: 12px;
            }
            QFrame:hover {
                border-color: #6366F1;
                background-color: #222733;
            }
        """
        )

        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(20, 18, 20, 18)

        title_row = QHBoxLayout()
        title_row.setSpacing(12)

        icon_label = QLabel()
        icon = self.get_icon(template_data["icon"])
        if not icon.isNull():
            icon_label.setPixmap(icon.pixmap(32, 32))
        title_row.addWidget(icon_label)

        title_label = QLabel(template_data["title"])
        title_label.setFont(QFont("Poppins", 14, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #F9FAFB;")
        title_row.addWidget(title_label)
        title_row.addStretch()

        layout.addLayout(title_row)

        desc_label = QLabel(template_data["description"])
        desc_label.setFont(QFont("Poppins", 11))
        desc_label.setStyleSheet("color: #9CA3AF;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        count_label = QLabel(f"{template_data['count']} nodes available")
        count_label.setFont(QFont("Poppins", 9, QFont.Weight.Bold))
        count_label.setStyleSheet(
            """
            color: #818CF8;
            background-color: rgba(99, 102, 241, 0.15);
            padding: 4px 10px;
            border-radius: 6px;
        """
        )
        layout.addWidget(count_label)
        layout.addStretch()

        explore_button = QPushButton("  View Nodes")
        explore_button.setIcon(self.get_icon("package"))
        explore_button.setFont(QFont("Poppins", 10, QFont.Weight.Bold))
        explore_button.setMinimumHeight(38)
        explore_button.setCursor(Qt.CursorShape.PointingHandCursor)
        explore_button.setStyleSheet(
            """
            QPushButton {
                padding: 8px 18px;
                background-color: #6366F1;
                color: white;
                border: none;
                border-radius: 8px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #4F46E5;
            }
            QPushButton:pressed {
                background-color: #4338CA;
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
        dialog = NodeDetailsDialog(category_data, self)
        dialog.exec()


__all__ = ["NodeDetailsDialog", "NodeTemplateWidget"]
