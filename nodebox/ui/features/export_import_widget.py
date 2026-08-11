import os
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from nodebox.services.storage import ExportWorker, ImportWorker


class ExportImportManager(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("QWidget { background-color: #0A0C10; color: #F0F2F8; }")

        layout = QVBoxLayout()
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(20)

        title = QLabel("Export & Import Workflows")
        title.setFont(QFont("Poppins", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #F0F2F8;")
        layout.addWidget(title)

        subtitle = QLabel("Package automations into standalone .nodebox archives for backup or sharing")
        subtitle.setFont(QFont("Poppins", 11))
        subtitle.setStyleSheet("color: #4A5578; margin-bottom: 4px;")
        layout.addWidget(subtitle)

        export_group = QGroupBox("Export Automations")
        export_group.setFont(QFont("Poppins", 13, QFont.Weight.Bold))
        export_layout = QVBoxLayout()
        export_layout.setSpacing(14)

        self.workflow_list = QListWidget()
        self.workflow_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.workflow_list.setMaximumHeight(140)
        self.load_workflows()
        export_layout.addWidget(QLabel("Select Workflows to Package:"))
        export_layout.addWidget(self.workflow_list)

        options_layout = QHBoxLayout()
        self.include_models_check = QCheckBox("Bundle Associated AI Models")
        self.include_data_check = QCheckBox("Bundle Custom Data Dependencies")
        self.include_models_check.setFont(QFont("Poppins", 10))
        self.include_data_check.setFont(QFont("Poppins", 10))
        options_layout.addWidget(self.include_models_check)
        options_layout.addWidget(self.include_data_check)
        export_layout.addLayout(options_layout)

        export_button = QPushButton("Export Selected Workflows")
        export_button.setFont(QFont("Poppins", 10, QFont.Weight.DemiBold))
        export_button.setMinimumHeight(40)
        export_button.setCursor(Qt.CursorShape.PointingHandCursor)
        export_button.setStyleSheet("""
            QPushButton {
                background-color: #6366F1;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 6px 20px;
            }
            QPushButton:hover { background-color: #5153D6; }
        """)
        export_button.clicked.connect(self.export_workflows)
        export_layout.addWidget(export_button)
        export_group.setLayout(export_layout)
        layout.addWidget(export_group)

        import_group = QGroupBox("Import Automation Package")
        import_group.setFont(QFont("Poppins", 13, QFont.Weight.Bold))
        import_layout = QVBoxLayout()
        import_layout.setSpacing(14)

        file_layout = QHBoxLayout()
        file_layout.setSpacing(12)

        self.import_file_edit = QLineEdit()
        self.import_file_edit.setPlaceholderText("Select .nodebox archive file...")
        self.import_file_edit.setMinimumHeight(42)
        file_layout.addWidget(self.import_file_edit)

        browse_button = QPushButton("Browse")
        browse_button.setFont(QFont("Poppins", 10, QFont.Weight.Medium))
        browse_button.setMinimumHeight(42)
        browse_button.setCursor(Qt.CursorShape.PointingHandCursor)
        browse_button.setStyleSheet("""
            QPushButton {
                background-color: #161922;
                color: #8892B0;
                border: 1px solid #1E2538;
                border-radius: 8px;
                padding: 0 18px;
            }
            QPushButton:hover {
                background-color: #1C2235;
                border-color: #6366F1;
                color: #F0F2F8;
            }
        """)
        browse_button.clicked.connect(self.browse_import_file)
        file_layout.addWidget(browse_button)
        import_layout.addLayout(file_layout)

        import_button = QPushButton("Import Package")
        import_button.setFont(QFont("Poppins", 10, QFont.Weight.DemiBold))
        import_button.setMinimumHeight(40)
        import_button.setCursor(Qt.CursorShape.PointingHandCursor)
        import_button.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 6px 20px;
            }
            QPushButton:hover { background-color: #059669; }
        """)
        import_button.clicked.connect(self.import_workflows)
        import_layout.addWidget(import_button)

        import_group.setLayout(import_layout)
        layout.addWidget(import_group)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

    def load_workflows(self):
        self.workflow_list.clear()
        workflows_dir = Path("workflows")
        if workflows_dir.exists():
            for workflow_file in workflows_dir.glob("*.json"):
                item = QListWidgetItem(workflow_file.stem)
                self.workflow_list.addItem(item)

    def export_workflows(self):
        selected_items = self.workflow_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(
                self, "No Selection", "Please select workflows to export."
            )
            return

        workflows = [item.text() for item in selected_items]

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Workflows",
            f"exports/nodebox_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.nodebox",
            "NodeBox Files (*.nodebox)",
        )
        if not file_path:
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

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
        self.progress_bar.setVisible(False)
        QMessageBox.information(
            self, "Export Complete", f"Workflows exported to:\n{file_path}"
        )

    def export_error(self, error_message):
        self.progress_bar.setVisible(False)
        QMessageBox.critical(
            self, "Export Error", f"Failed to export workflows:\n{error_message}"
        )

    def browse_import_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Workflows", "", "NodeBox Files (*.nodebox)"
        )
        if file_path:
            self.import_file_edit.setText(file_path)

    def import_workflows(self):
        file_path = self.import_file_edit.text()
        if not file_path or not os.path.exists(file_path):
            QMessageBox.warning(
                self, "Invalid File", "Please select a valid .nodebox file."
            )
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        self.import_worker = ImportWorker(file_path)
        self.import_worker.progress.connect(self.progress_bar.setValue)
        self.import_worker.finished.connect(self.import_finished)
        self.import_worker.error.connect(self.import_error)
        self.import_worker.start()

    def import_finished(self, imported_workflows):
        self.progress_bar.setVisible(False)
        self.load_workflows()
        QMessageBox.information(
            self,
            "Import Complete",
            f"Successfully imported {len(imported_workflows)} workflows:\n"
            + "\n".join(imported_workflows),
        )

    def import_error(self, error_message):
        self.progress_bar.setVisible(False)
        QMessageBox.critical(
            self, "Import Error", f"Failed to import workflows:\n{error_message}"
        )


__all__ = ["ExportImportManager"]
