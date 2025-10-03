from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QListWidget, QPushButton, QMessageBox, QHBoxLayout
import subprocess


class ModelManager(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Local Ollama Models")
        self.resize(400, 400)

        # Main layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Info label
        self.info_label = QLabel("Locally Downloaded Ollama Models:")
        self.layout.addWidget(self.info_label)

        # List widget
        self.model_list = QListWidget()
        self.layout.addWidget(self.model_list)

        # Button layout
        self.button_layout = QHBoxLayout()
        self.delete_button = QPushButton("Delete Selected Model")
        self.delete_button.clicked.connect(self.delete_model)
        self.button_layout.addWidget(self.delete_button)
        self.layout.addLayout(self.button_layout)

        # Load models
        self.load_models()

    def load_models(self):
        """Fetch local models and populate the list"""
        self.model_list.clear()
        self.delete_button.setEnabled(True)

        try:
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True, check=True)
            models = [line.strip() for line in result.stdout.splitlines() if line.strip()]
            if models:
                self.model_list.addItems(models)
            else:
                self.model_list.addItem("No models found!")
                self.delete_button.setEnabled(False)
        except FileNotFoundError:
            self.model_list.addItem("Ollama not installed")
            self.delete_button.setEnabled(False)
        except subprocess.CalledProcessError:
            self.model_list.addItem("Error retrieving models")
            self.delete_button.setEnabled(False)

    def delete_model(self):
        """Delete selected model after confirmation"""
        selected_items = self.model_list.selectedItems()
        if not selected_items:
            return

        model_name = selected_items[0].text()
        if model_name in ["No models found!", "Ollama not installed", "Error retrieving models"]:
            return

        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete model '{model_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                subprocess.run(["ollama", "delete", model_name], check=True)
                QMessageBox.information(self, "Deleted", f"Model '{model_name}' deleted successfully.")
                self.load_models()  # Refresh the list
            except subprocess.CalledProcessError:
                QMessageBox.warning(self, "Error", f"Failed to delete model '{model_name}'.")
