"""
Model Manager - View and manage local Ollama models
"""
import subprocess
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QMessageBox,
    QHeaderView,
)


class ModelManager(QDialog):
    """Dialog version for standalone use"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Local Models Manager")
        self.setMinimumSize(700, 500)
        self.widget = ModelManagerWidget()
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.widget)
        
        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        close_button = QPushButton("Close")
        close_button.setFont(QFont("Segoe UI", 11))
        close_button.setMinimumHeight(36)
        close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        close_button.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                background-color: #0e639c;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
        """)
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.setStyleSheet("QDialog { background-color: #252526; }")


class ModelManagerWidget(QWidget):
    """Widget version for embedding in main window"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_models()

    def setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Title
        title = QLabel("Local Ollama Models")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #ffffff;")
        layout.addWidget(title)

        subtitle = QLabel("Manage your downloaded models")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet("color: #a0a0a0; margin-bottom: 10px;")
        layout.addWidget(subtitle)

        # Models table
        self.models_table = QTableWidget()
        self.models_table.setColumnCount(4)
        self.models_table.setHorizontalHeaderLabels(
            ["Model Name", "Size", "Modified", "Actions"]
        )
        self.models_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.models_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        self.models_table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )
        self.models_table.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeMode.ResizeToContents
        )
        self.models_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.models_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.models_table.setStyleSheet(
            """
            QTableWidget {
                background-color: #1e1e1e;
                border: 1px solid #3e3e42;
                border-radius: 4px;
                gridline-color: #3e3e42;
            }
            QTableWidget::item {
                padding: 8px;
                color: #e0e0e0;
            }
            QTableWidget::item:selected {
                background-color: #0e639c;
            }
            QHeaderView::section {
                background-color: #2d2d30;
                color: #e0e0e0;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #3e3e42;
                font-weight: 600;
            }
        """
        )
        layout.addWidget(self.models_table)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setFont(QFont("Segoe UI", 10))
        self.status_label.setStyleSheet("color: #888888;")
        layout.addWidget(self.status_label)

        # Refresh button
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        refresh_button = QPushButton("Refresh")
        refresh_button.setFont(QFont("Segoe UI", 11))
        refresh_button.setMinimumHeight(36)
        refresh_button.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_button.setStyleSheet(
            """
            QPushButton {
                padding: 8px 20px;
                background-color: #3e3e42;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #4e4e52;
            }
        """
        )
        refresh_button.clicked.connect(self.load_models)
        button_layout.addWidget(refresh_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.setStyleSheet("QWidget { background-color: #252526; }")

    def load_models(self):
        """Load models from Ollama"""
        self.models_table.setRowCount(0)
        self.status_label.setText("Loading models...")

        try:
            result = subprocess.run(
                ["ollama", "list"], capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")

                if len(lines) <= 1:  # Only header or empty
                    self.show_no_models()
                    return

                # Skip header line
                models = []
                for line in lines[1:]:
                    parts = line.split()
                    if len(parts) >= 3:
                        models.append(
                            {
                                "name": parts[0],
                                "size": parts[2] if len(parts) > 2 else "Unknown",
                                "modified": " ".join(parts[3:])
                                if len(parts) > 3
                                else "Unknown",
                            }
                        )

                if not models:
                    self.show_no_models()
                    return

                # Populate table
                self.models_table.setRowCount(len(models))
                for row, model in enumerate(models):
                    # Model name
                    name_item = QTableWidgetItem(model["name"])
                    name_item.setFont(QFont("Segoe UI", 10))
                    self.models_table.setItem(row, 0, name_item)

                    # Size
                    size_item = QTableWidgetItem(model["size"])
                    size_item.setFont(QFont("Segoe UI", 10))
                    self.models_table.setItem(row, 1, size_item)

                    # Modified
                    modified_item = QTableWidgetItem(model["modified"])
                    modified_item.setFont(QFont("Segoe UI", 10))
                    self.models_table.setItem(row, 2, modified_item)

                    # Delete button
                    delete_button = QPushButton("Delete")
                    delete_button.setFont(QFont("Segoe UI", 10))
                    delete_button.setCursor(Qt.CursorShape.PointingHandCursor)
                    delete_button.setStyleSheet(
                        """
                        QPushButton {
                            padding: 6px 12px;
                            background-color: #c42b1c;
                            color: white;
                            border: none;
                            border-radius: 4px;
                            font-weight: 600;
                        }
                        QPushButton:hover {
                            background-color: #e03c2d;
                        }
                    """
                    )
                    delete_button.clicked.connect(
                        lambda checked, m=model["name"]: self.delete_model(m)
                    )
                    self.models_table.setCellWidget(row, 3, delete_button)

                self.status_label.setText(f"Found {len(models)} model(s)")

            else:
                self.show_error("Failed to retrieve models from Ollama")

        except FileNotFoundError:
            self.show_error("Ollama is not installed or not in PATH")
        except subprocess.TimeoutExpired:
            self.show_error("Timeout while connecting to Ollama")
        except Exception as e:
            self.show_error(f"Error loading models: {str(e)}")

    def show_no_models(self):
        """Show message when no models are found"""
        self.models_table.setRowCount(1)
        item = QTableWidgetItem("No local models found")
        item.setFont(QFont("Segoe UI", 11))
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.models_table.setItem(0, 0, item)
        self.models_table.setSpan(0, 0, 1, 4)
        self.status_label.setText("No models installed")

    def show_error(self, message):
        """Show error message"""
        self.models_table.setRowCount(1)
        item = QTableWidgetItem(f"⚠ {message}")
        item.setFont(QFont("Segoe UI", 11))
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item.setForeground(Qt.GlobalColor.red)
        self.models_table.setItem(0, 0, item)
        self.models_table.setSpan(0, 0, 1, 4)
        self.status_label.setText("Error")

    def delete_model(self, model_name):
        """Delete a model"""
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete the model:\n\n{model_name}\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.status_label.setText(f"Deleting {model_name}...")
                result = subprocess.run(
                    ["ollama", "rm", model_name],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode == 0:
                    QMessageBox.information(
                        self,
                        "Success",
                        f"Model '{model_name}' has been deleted successfully.",
                    )
                    self.load_models()  # Refresh the list
                else:
                    QMessageBox.warning(
                        self, "Error", f"Failed to delete model:\n\n{result.stderr}"
                    )
                    self.status_label.setText("Deletion failed")

            except subprocess.TimeoutExpired:
                QMessageBox.warning(self, "Error", "Timeout while deleting model")
                self.status_label.setText("Timeout")
            except Exception as e:
                QMessageBox.warning(
                    self, "Error", f"Error deleting model:\n\n{str(e)}"
                )
                self.status_label.setText("Error")
