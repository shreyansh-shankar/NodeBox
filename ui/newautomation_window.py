# ui/new_automation_window.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtCore import Qt

from utils.storage import save_automation, load_automations
from utils.paths import AUTOMATIONS_DIR
import json
import os

class NewAutomationWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Create New Automation")
        self.setFixedSize(400, 200)
        self.setStyleSheet("background-color: #1e1e1e; color: white;")

        layout = QVBoxLayout(self)

        label = QLabel("Enter Automation Name")
        label.setStyleSheet("font-size: 18px; margin-left: 80px")
        layout.addWidget(label)

        self.name_input = QLineEdit()
        self.name_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border-radius: 6px;
                background-color: #2e2e2e;
                color: white;
                font-size: 14px;
            }
        """)
        layout.addWidget(self.name_input)

        create_btn = QPushButton("Create")
        create_btn.setStyleSheet("""
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
        """)
        create_btn.clicked.connect(self.on_create_button_clicked)
        layout.addWidget(create_btn)

    def on_create_button_clicked(self):
        name = self.name_input.text().strip()

        if not name:
            QMessageBox.warning(self, "Invalid Input", "Automation name cannot be empty.")
            return

        filename = f"{name}.json"
        file_path = os.path.join(AUTOMATIONS_DIR, filename)

        if os.path.exists(file_path):
            QMessageBox.warning(self, "Duplicate Name", "An automation with this name already exists.")
            return

        try:
            # Create an empty JSON file
            with open(file_path, "w") as f:
                json.dump({}, f, indent=4)
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create automation file:\n{str(e)}")
