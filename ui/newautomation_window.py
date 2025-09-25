# ui/new_automation_window.py
import json
import os

from PyQt6.QtWidgets import (
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from automation_manager.node_editor_window import NodeEditorWindow
from utils.paths import AUTOMATIONS_DIR
from utils.screen_manager import ScreenManager


class NewAutomationWindow(QWidget):
    def __init__(self, main_window=None):
        self.main_window = main_window
        super().__init__()
        self.setWindowTitle("Create New Automation")

        # Use dynamic window sizing for small dialog
        width, height = ScreenManager.get_dialog_window_size(
            width_percentage=0.25, height_percentage=0.15, min_width=350, min_height=150
        )

        # Center the window
        x, y = ScreenManager.calculate_window_position(width, height, center=True)
        self.setGeometry(x, y, width, height)
        self.setStyleSheet("background-color: #1e1e1e; color: white;")

        layout = QVBoxLayout(self)

        label = QLabel("Enter Automation Name")
        label.setStyleSheet("font-size: 18px; margin-left: 80px")
        layout.addWidget(label)

        self.name_input = QLineEdit()
        self.name_input.setStyleSheet(
            """
            QLineEdit {
                padding: 10px;
                border-radius: 6px;
                background-color: #2e2e2e;
                color: white;
                font-size: 14px;
            }
        """
        )
        layout.addWidget(self.name_input)

        create_btn = QPushButton("Create")
        create_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #2e7d32;
                color: white;
                padding: 10px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #388e3c;
            }
        """
        )
        create_btn.clicked.connect(self.on_create_button_clicked)
        layout.addWidget(create_btn)

    def on_create_button_clicked(self):
        name = self.name_input.text().strip()

        if not name:
            QMessageBox.warning(
                self, "Invalid Input", "Automation name cannot be empty."
            )
            return

        filename = f"{name}.json"
        file_path = os.path.join(AUTOMATIONS_DIR, filename)

        if os.path.exists(file_path):
            QMessageBox.warning(
                self, "Duplicate Name", "An automation with this name already exists."
            )
            return

        try:
            # Create an empty JSON file
            with open(file_path, "w") as f:
                json.dump({}, f, indent=4)

            self.main_window.load_automations()

            # Open Node Editor
            self.node_editor = NodeEditorWindow(name)
            self.node_editor.closed.connect(self.reopen_main_window)
            self.node_editor.show()

            if self.main_window:
                self.main_window.close()

            # Close this window
            self.close()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to create automation file:\n{str(e)}"
            )

    def reopen_main_window(self):
        if self.main_window:
            self.main_window.show()
