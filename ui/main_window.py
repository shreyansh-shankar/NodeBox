from PyQt6.QtWidgets import ( #type: ignore
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QHBoxLayout, QGraphicsDropShadowEffect, QSizePolicy
)
from PyQt6.QtSvgWidgets import QSvgWidget #type: ignore
from PyQt6.QtSvg import QSvgRenderer #type: ignore
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPainter #type: ignore
from PyQt6.QtCore import Qt, QPoint #type: ignore

from ui.browsemodel_window import BrowseModelsWindow
from ui.newautomation_window import NewAutomationWindow
from utils.paths import AUTOMATIONS_DIR

import os
import json

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NodeBox - Automation Studio")
        self.setGeometry(100, 100, 900, 600)

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # 🧠 Title
        title = QLabel("NodeBox")
        title.setFont(QFont("Poppins", 24))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(title)

        # ➕ Create New Automation Button
        create_button = QPushButton("➕ Create New Automation")
        create_button.setStyleSheet("""
        QPushButton {
            font-family: 'Poppins';
            padding: 12px 10px;
            font-size: 18px;
            margin: 6px 248px;
            border-radius: 8px;
        }
    """)
        create_button.clicked.connect(self.create_new_automation)
        self.main_layout.addWidget(create_button)

        # 🔁 Automation List
        self.main_layout.addWidget(QLabel("Your Automations:"))
        self.automation_list = QListWidget()
        self.automation_list.setStyleSheet("""
            QListWidget {
                border: none;
                padding: 5px;
                margin: 0px;
                background-color: transparent;
            }
        """)
        self.main_layout.addWidget(self.automation_list)

        # 👉 Load sample automations
        self.load_automations()

        # 🧺 Floating Browse Models Button
        self.browse_button = QPushButton("🧺 Browse Models", self)
        self.browse_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.browse_button.setStyleSheet("""
            QPushButton {
                background-color: #2b2b2b;
                color: white;
                border-radius: 12px;
                padding: 8px 14px;
                font-family: 'Poppins';
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #000000;
            }
        """)

        # Optional shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(10)
        shadow.setOffset(2, 2)
        self.browse_button.setGraphicsEffect(shadow)
        self.browse_button.resize(160, 40)

        self.browse_button.clicked.connect(self.open_browse_models_window)

    def load_automations(self):
        self.automation_list.clear()

        automations = self.fetch_automations()

        if not automations:
            self.show_empty_state()
            self.automation_list.setFixedHeight(0)
            return

        self.clear_empty_state()
        self.automation_list.show()
        self.automation_list.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.automation_list.setMinimumHeight(300)

        for name in automations:
            item_widget = QWidget()
            item_layout = QHBoxLayout()
            item_widget.setLayout(item_layout)

            label = QLabel(name)
            run_button = QPushButton("Run")
            edit_button = QPushButton("Edit")

            run_button.setFixedWidth(60)
            edit_button.setFixedWidth(60)

            item_layout.addWidget(label)
            item_layout.addStretch()
            item_layout.addWidget(run_button)
            item_layout.addWidget(edit_button)

            list_item = QListWidgetItem()
            list_item.setSizeHint(item_widget.sizeHint())

            self.automation_list.addItem(list_item)
            self.automation_list.setItemWidget(list_item, item_widget)

            edit_button.clicked.connect(lambda _, n=name: self.edit_automation(n))

    def fetch_automations(self):
        automations = []

        if not AUTOMATIONS_DIR.exists():
            return automations

        for file in AUTOMATIONS_DIR.glob("*.json"):
            try:
                with open(file, "r") as f:
                    data = json.load(f)
                    name = data.get("name", file.stem)
                    automations.append(name)
            except Exception as e:
                print(f"⚠️ Error loading {file.name}: {e}")
                continue

        return automations
    
    def edit_automation(self, name):
        from ui.node_editor_window import NodeEditorWindow

        self.editor_window = NodeEditorWindow(name)
        self.editor_window.closed.connect(self.show)
        self.editor_window.show()
        self.hide()

    def show_empty_state(self):
        self.automation_list.hide()
        if hasattr(self, 'empty_state_widget'):
            self.empty_state_widget.show()
            return

        # Create full-area widget
        self.empty_state_widget = QWidget()
        self.empty_state_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Outer layout (fills the space)
        outer_layout = QVBoxLayout(self.empty_state_widget)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        # Inner container for centered content
        inner_container = QWidget()
        inner_layout = QVBoxLayout(inner_container)
        inner_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # SVG image
        image = QLabel()
        svg_renderer = QSvgRenderer("assets/icons/anchor.svg")
        if svg_renderer.isValid():
            pixmap = QPixmap(100, 100)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            svg_renderer.render(painter)
            painter.end()
            image.setPixmap(pixmap)
        else:
            fallback_pixmap = QPixmap(100, 100)
            fallback_pixmap.fill(Qt.GlobalColor.lightGray)
            image.setPixmap(fallback_pixmap)

        image.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Title
        message = QLabel("No automations yet.")
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message.setStyleSheet("""
            QLabel {
                font-family: 'Poppins';
                font-size: 20px;
                font-weight: 500;
                color: #ccc;
                margin-top: 16px;
            }
        """)

        # Subtext
        subtext = QLabel("Click the ➕ button above to create your first automation.")
        subtext.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtext.setWordWrap(True)
        subtext.setStyleSheet("""
            QLabel {
                font-family: 'Poppins';
                font-size: 14px;
                color: #ccc;
                margin-top: 8px;
            }
        """)

        # Assemble
        inner_layout.addWidget(image)
        inner_layout.addWidget(message)
        inner_layout.addWidget(subtext)
        outer_layout.addWidget(inner_container, alignment=Qt.AlignmentFlag.AlignCenter)

        # Drop shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 4)
        self.empty_state_widget.setGraphicsEffect(shadow)

        # Add to main layout
        self.main_layout.addWidget(self.empty_state_widget)

    def clear_empty_state(self):
        if hasattr(self, 'empty_state_widget'):
            self.empty_state_widget.hide()

    def create_new_automation(self):
        self.new_automation_window = NewAutomationWindow(main_window=self)
        self.new_automation_window.show()
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        margin = 20
        x = self.width() - self.browse_button.width() - margin
        y = self.height() - self.browse_button.height() - margin
        self.browse_button.move(x, y)

    def open_browse_models_window(self):
        self.browse_window = BrowseModelsWindow()
        self.browse_window.show()
