"""
Optimized Export/Import System - Efficient workflow sharing
"""
import json
import os
import zipfile
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class ExportWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(
        self, workflows, export_path, include_models=False, include_data=False
    ):
        super().__init__()
        self.workflows = workflows
        self.export_path = export_path
        self.include_models = include_models
        self.include_data = include_data
        self._workflows_dir = Path("workflows")
        self._models_dir = Path("models")
        self._data_dir = Path("data")

    def run(self):
        try:
            self.export_workflows()
            self.finished.emit(self.export_path)
        except Exception as e:
            self.error.emit(str(e))

    def export_workflows(self):
        """Optimized workflow export"""
        with zipfile.ZipFile(
            self.export_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6
        ) as zipf:
            total_items = (
                len(self.workflows)
                + (2 if self.include_models else 0)
                + (2 if self.include_data else 0)
                + 1
            )
            # Export workflow files
            for current_item, workflow in enumerate(self.workflows):
                workflow_file = self._workflows_dir / f"{workflow}.json"
                if workflow_file.exists():
                    zipf.write(workflow_file, f"workflows/{workflow}.json")
                self.progress.emit(int((current_item / total_items) * 80))

            # Export models if requested
            if self.include_models and self._models_dir.exists():
                for file_path in self._models_dir.rglob("*"):
                    if file_path.is_file():
                        arc_path = file_path.relative_to(Path("."))
                        zipf.write(file_path, str(arc_path))
                current_item += 1
                self.progress.emit(int((current_item / total_items) * 80))

            # Export data if requested
            if self.include_data and self._data_dir.exists():
                for file_path in self._data_dir.rglob("*"):
                    if file_path.is_file():
                        arc_path = file_path.relative_to(Path("."))
                        zipf.write(file_path, str(arc_path))
                current_item += 1
                self.progress.emit(int((current_item / total_items) * 80))

            # Create compact manifest
            manifest = {
                "version": "2.0",
                "date": datetime.now().isoformat(),
                "workflows": self.workflows,
                "models": self.include_models,
                "data": self.include_data,
            }

            zipf.writestr("manifest.json", json.dumps(manifest, separators=(",", ":")))
            self.progress.emit(100)


class ImportWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, import_path):
        super().__init__()
        self.import_path = import_path

    def run(self):
        try:
            imported_workflows = self.import_workflows()
            self.finished.emit(imported_workflows)
        except Exception as e:
            self.error.emit(str(e))

    def import_workflows(self):
        """Optimized workflow import"""
        imported_workflows = []

        with zipfile.ZipFile(self.import_path, "r") as zipf:
            # Read manifest
            manifest_data = zipf.read("manifest.json")
            manifest = json.loads(manifest_data)

            workflows = manifest.get("workflows", [])
            total_items = (
                len(workflows)
                + (1 if manifest.get("models") else 0)
                + (1 if manifest.get("data") else 0)
            )
            # Extract workflows
            os.makedirs("workflows", exist_ok=True)
            for current_item, workflow in enumerate(workflows):
                workflow_file = f"workflows/{workflow}.json"
                if workflow_file in zipf.namelist():
                    zipf.extract(workflow_file, ".")
                    imported_workflows.append(workflow)
                current_item += 1
                self.progress.emit(int((current_item / total_items) * 80))

            # Extract models if included
            if manifest.get("models"):
                for file_info in zipf.infolist():
                    if file_info.filename.startswith("models/"):
                        zipf.extract(file_info.filename, ".")
                current_item += 1
                self.progress.emit(int((current_item / total_items) * 80))

            # Extract data if included
            if manifest.get("data"):
                for file_info in zipf.infolist():
                    if file_info.filename.startswith("data/"):
                        zipf.extract(file_info.filename, ".")
                current_item += 1
                self.progress.emit(int((current_item / total_items) * 80))

            self.progress.emit(100)

        return imported_workflows


class ExportImportManager(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Minimalist title
        title = QLabel("Export/Import")
        title.setFont(QFont("Poppins", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Export section
        export_group = QGroupBox("Export")
        export_layout = QVBoxLayout()

        # Workflow selection
        self.workflow_list = QListWidget()
        self.workflow_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.workflow_list.setMaximumHeight(120)
        self.load_workflows()
        export_layout.addWidget(QLabel("Workflows:"))
        export_layout.addWidget(self.workflow_list)

        # Compact options
        options_layout = QHBoxLayout()

        self.include_models_check = QCheckBox("Models")
        options_layout.addWidget(self.include_models_check)

        self.include_data_check = QCheckBox("Data")
        options_layout.addWidget(self.include_data_check)

        export_layout.addLayout(options_layout)

        # Export button
        export_button = QPushButton("Export")
        export_button.clicked.connect(self.export_workflows)
        export_button.setStyleSheet("QPushButton { padding: 6px 12px; }")
        export_layout.addWidget(export_button)

        export_group.setLayout(export_layout)
        layout.addWidget(export_group)

        # Import section
        import_group = QGroupBox("Import")
        import_layout = QVBoxLayout()

        # Import file selection
        file_layout = QHBoxLayout()

        self.import_file_edit = QLineEdit()
        self.import_file_edit.setPlaceholderText("Select .nodebox file")
        file_layout.addWidget(self.import_file_edit)

        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_import_file)
        browse_button.setStyleSheet("QPushButton { padding: 4px 8px; }")
        file_layout.addWidget(browse_button)

        import_layout.addLayout(file_layout)

        # Import button
        import_button = QPushButton("Import")
        import_button.clicked.connect(self.import_workflows)
        import_button.setStyleSheet("QPushButton { padding: 6px 12px; }")
        import_layout.addWidget(import_button)

        import_group.setLayout(import_layout)
        layout.addWidget(import_group)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

    def load_workflows(self):
        """Load available workflows"""
        self.workflow_list.clear()

        workflows_dir = Path("workflows")
        if workflows_dir.exists():
            for workflow_file in workflows_dir.glob("*.json"):
                workflow_name = workflow_file.stem
                item = QListWidgetItem(workflow_name)
                self.workflow_list.addItem(item)

    def export_workflows(self):
        """Export selected workflows"""
        selected_items = self.workflow_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(
                self, "No Selection", "Please select workflows to export."
            )
            return

        workflows = [item.text() for item in selected_items]

        # Get export file path
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Workflows",
            f"nodebox_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.nodebox",
            "NodeBox Files (*.nodebox)",
        )

        if not file_path:
            return

        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # Start export worker
        self.export_worker = ExportWorker(
            workflows,
            file_path,
            self.include_models_check.isChecked(),
            self.include_data_check.isChecked(),
        )
        self.export_worker.progress.connect(self.progress_bar.setValue)
        self.export_worker.finished.connect(self.export_finished)
        self.export_worker.error.connect(self.export_error)
        self.export_worker.start()

    def export_finished(self, file_path):
        """Handle export completion"""
        self.progress_bar.setVisible(False)
        QMessageBox.information(
            self, "Export Complete", f"Workflows exported to:\n{file_path}"
        )

    def export_error(self, error_message):
        """Handle export error"""
        self.progress_bar.setVisible(False)
        QMessageBox.critical(
            self, "Export Error", f"Failed to export workflows:\n{error_message}"
        )

    def browse_import_file(self):
        """Browse for import file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Workflows", "", "NodeBox Files (*.nodebox)"
        )

        if file_path:
            self.import_file_edit.setText(file_path)

    def import_workflows(self):
        """Import workflows from file"""
        file_path = self.import_file_edit.text()
        if not file_path or not os.path.exists(file_path):
            QMessageBox.warning(
                self, "Invalid File", "Please select a valid .nodebox file."
            )
            return

        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # Start import worker
        self.import_worker = ImportWorker(file_path)
        self.import_worker.progress.connect(self.progress_bar.setValue)
        self.import_worker.finished.connect(self.import_finished)
        self.import_worker.error.connect(self.import_error)
        self.import_worker.start()

    def import_finished(self, imported_workflows):
        """Handle import completion"""
        self.progress_bar.setVisible(False)
        self.load_workflows()  # Refresh workflow list

        QMessageBox.information(
            self,
            "Import Complete",
            f"Successfully imported {len(imported_workflows)} workflows:\n"
            + "\n".join(imported_workflows),
        )

    def import_error(self, error_message):
        """Handle import error"""
        self.progress_bar.setVisible(False)
        QMessageBox.critical(
            self, "Import Error", f"Failed to import workflows:\n{error_message}"
        )


class WorkflowPreviewDialog(QDialog):
    def __init__(self, workflow_data, parent=None):
        super().__init__(parent)
        self.workflow_data = workflow_data
        self.setWindowTitle("Workflow Preview")
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Workflow info
        info_layout = QFormLayout()

        name_edit = QLineEdit(self.workflow_data.get("name", ""))
        name_edit.setReadOnly(True)
        info_layout.addRow("Name:", name_edit)

        created_edit = QLineEdit(self.workflow_data.get("created", ""))
        created_edit.setReadOnly(True)
        info_layout.addRow("Created:", created_edit)

        layout.addLayout(info_layout)

        # Workflow content
        content_edit = QTextEdit()
        content_edit.setPlainText(json.dumps(self.workflow_data, indent=2))
        content_edit.setReadOnly(True)
        layout.addWidget(content_edit)

        # Buttons
        button_layout = QHBoxLayout()

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)
