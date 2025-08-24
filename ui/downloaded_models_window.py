# downloaded_models_window.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QHBoxLayout, QPushButton, QMessageBox
)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt
import subprocess
import json

class DownloadedModelsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Downloaded Models")
        self.setGeometry(150, 150, 600, 400)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Title
        title = QLabel("Downloaded Models")
        title.setFont(QFont("Poppins", 22))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(title)

        # List widget
        self.model_list = QListWidget()
        self.model_list.setStyleSheet("""
            QListWidget {
                border: none;
                padding: 5px;
                margin: 0px;
                background-color: transparent;
            }
        """)
        self.layout.addWidget(self.model_list)

        # Load models
        self.load_models()

    def load_models(self):
        self.model_list.clear()

        models = self.fetch_downloaded_models()

        if not models:
            empty_label = QLabel("No models downloaded yet.")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setFont(QFont("Poppins", 14))
            empty_label.setStyleSheet("color: #888;")
            self.layout.addWidget(empty_label)
            return

        for model in models:
            item_widget = QWidget()
            item_layout = QHBoxLayout()
            item_widget.setLayout(item_layout)

            name_label = QLabel(model.get("name", "Unknown"))
            version_label = QLabel(model.get("version", ""))
            version_label.setStyleSheet("color: #888; font-size: 12px;")

            # 🔴 Delete Button
            delete_button = QPushButton("Delete")
            delete_button.setFixedWidth(80)
            delete_button.setStyleSheet("QPushButton { color: white; }")
            delete_button.clicked.connect(lambda _, m=model: self.delete_model(m))

            item_layout.addWidget(name_label)
            item_layout.addWidget(version_label)
            item_layout.addStretch()
            item_layout.addWidget(delete_button)

            list_item = QListWidgetItem()
            list_item.setSizeHint(item_widget.sizeHint())

            self.model_list.addItem(list_item)
            self.model_list.setItemWidget(list_item, item_widget)

    def fetch_downloaded_models(self):
        """Fetch models using `ollama list` (plain text)."""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True, text=True, check=True
            )
            lines = result.stdout.strip().split("\n")
            models = []

            for line in lines:
                # Skip headers if present
                if line.lower().startswith("name"):
                    continue
                parts = line.split()  # Assuming name version columns
                if len(parts) >= 1:
                    models.append({
                        "name": parts[0],
                        "version": parts[1] if len(parts) > 1 else ""
                    })
            return models

        except subprocess.CalledProcessError as e:
            print("⚠️ Ollama command failed:", e)
            return []


    def delete_model(self, model):
        """Delete a model using `ollama rm`."""
        model_name = model.get("name", "")
        if not model_name:
            return

        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete model '{model_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                subprocess.run(
                    ["ollama", "rm", model_name],
                    capture_output=True, text=True, check=True
                )
                QMessageBox.information(self, "Deleted", f"Model '{model_name}' deleted successfully.")
                self.load_models()  # Refresh list
            except subprocess.CalledProcessError as e:
                QMessageBox.critical(self, "Error", f"Failed to delete model '{model_name}':\n{e}")
