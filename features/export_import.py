"""
Export/Import System - Share workflows easily
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QFileDialog, QMessageBox, QListWidget, QListWidgetItem,
                             QCheckBox, QLineEdit, QTextEdit, QDialog, QFormLayout,
                             QGroupBox, QProgressBar)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
import json
import zipfile
import os
import shutil
from datetime import datetime
from pathlib import Path

class ExportWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, workflows, export_path, include_models=False, include_data=False):
        super().__init__()
        self.workflows = workflows
        self.export_path = export_path
        self.include_models = include_models
        self.include_data = include_data
    
    def run(self):
        try:
            self.export_workflows()
            self.finished.emit(self.export_path)
        except Exception as e:
            self.error.emit(str(e))
    
    def export_workflows(self):
        """Export workflows to a zip file"""
        with zipfile.ZipFile(self.export_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Export workflow files
            for i, workflow in enumerate(self.workflows):
                self.progress.emit(int((i / len(self.workflows)) * 80))
                
                workflow_file = f"workflows/{workflow}.json"
                if os.path.exists(workflow_file):
                    zipf.write(workflow_file, f"workflows/{workflow}.json")
            
            # Export models if requested
            if self.include_models:
                self.progress.emit(85)
                models_dir = "models"
                if os.path.exists(models_dir):
                    for root, dirs, files in os.walk(models_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arc_path = os.path.relpath(file_path, ".")
                            zipf.write(file_path, arc_path)
            
            # Export data if requested
            if self.include_data:
                self.progress.emit(90)
                data_dir = "data"
                if os.path.exists(data_dir):
                    for root, dirs, files in os.walk(data_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arc_path = os.path.relpath(file_path, ".")
                            zipf.write(file_path, arc_path)
            
            # Create manifest
            self.progress.emit(95)
            manifest = {
                "export_version": "1.0",
                "export_date": datetime.now().isoformat(),
                "workflows": self.workflows,
                "include_models": self.include_models,
                "include_data": self.include_data
            }
            
            zipf.writestr("manifest.json", json.dumps(manifest, indent=2))
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
        """Import workflows from a zip file"""
        imported_workflows = []
        
        with zipfile.ZipFile(self.import_path, 'r') as zipf:
            # Read manifest
            manifest_data = zipf.read("manifest.json")
            manifest = json.loads(manifest_data)
            
            # Extract workflows
            for i, workflow in enumerate(manifest.get("workflows", [])):
                self.progress.emit(int((i / len(manifest["workflows"])) * 80))
                
                workflow_file = f"workflows/{workflow}.json"
                if workflow_file in zipf.namelist():
                    # Extract to workflows directory
                    os.makedirs("workflows", exist_ok=True)
                    zipf.extract(workflow_file, ".")
                    imported_workflows.append(workflow)
            
            # Extract models if included
            if manifest.get("include_models", False):
                self.progress.emit(85)
                for file_info in zipf.infolist():
                    if file_info.filename.startswith("models/"):
                        zipf.extract(file_info.filename, ".")
            
            # Extract data if included
            if manifest.get("include_data", False):
                self.progress.emit(90)
                for file_info in zipf.infolist():
                    if file_info.filename.startswith("data/"):
                        zipf.extract(file_info.filename, ".")
            
            self.progress.emit(100)
        
        return imported_workflows

class ExportImportManager(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Export/Import Manager")
        title.setFont(QFont("Poppins", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Export section
        export_group = QGroupBox("Export Workflows")
        export_layout = QVBoxLayout()
        
        # Workflow selection
        self.workflow_list = QListWidget()
        self.workflow_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.load_workflows()
        export_layout.addWidget(QLabel("Select Workflows to Export:"))
        export_layout.addWidget(self.workflow_list)
        
        # Export options
        options_layout = QHBoxLayout()
        
        self.include_models_check = QCheckBox("Include Models")
        options_layout.addWidget(self.include_models_check)
        
        self.include_data_check = QCheckBox("Include Data")
        options_layout.addWidget(self.include_data_check)
        
        export_layout.addLayout(options_layout)
        
        # Export button
        export_button = QPushButton("Export Selected")
        export_button.clicked.connect(self.export_workflows)
        export_layout.addWidget(export_button)
        
        export_group.setLayout(export_layout)
        layout.addWidget(export_group)
        
        # Import section
        import_group = QGroupBox("Import Workflows")
        import_layout = QVBoxLayout()
        
        # Import file selection
        file_layout = QHBoxLayout()
        
        self.import_file_edit = QLineEdit()
        self.import_file_edit.setPlaceholderText("Select .nodebox file to import")
        file_layout.addWidget(self.import_file_edit)
        
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_import_file)
        file_layout.addWidget(browse_button)
        
        import_layout.addLayout(file_layout)
        
        # Import button
        import_button = QPushButton("Import")
        import_button.clicked.connect(self.import_workflows)
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
            QMessageBox.warning(self, "No Selection", "Please select workflows to export.")
            return
        
        workflows = [item.text() for item in selected_items]
        
        # Get export file path
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Workflows", f"nodebox_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.nodebox",
            "NodeBox Files (*.nodebox)"
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
            self.include_data_check.isChecked()
        )
        self.export_worker.progress.connect(self.progress_bar.setValue)
        self.export_worker.finished.connect(self.export_finished)
        self.export_worker.error.connect(self.export_error)
        self.export_worker.start()
    
    def export_finished(self, file_path):
        """Handle export completion"""
        self.progress_bar.setVisible(False)
        QMessageBox.information(self, "Export Complete", f"Workflows exported to:\n{file_path}")
    
    def export_error(self, error_message):
        """Handle export error"""
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Export Error", f"Failed to export workflows:\n{error_message}")
    
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
            QMessageBox.warning(self, "Invalid File", "Please select a valid .nodebox file.")
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
            self, "Import Complete", 
            f"Successfully imported {len(imported_workflows)} workflows:\n" + 
            "\n".join(imported_workflows)
        )
    
    def import_error(self, error_message):
        """Handle import error"""
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Import Error", f"Failed to import workflows:\n{error_message}")

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
