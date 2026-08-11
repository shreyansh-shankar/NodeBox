import json
import os
import zipfile
from datetime import datetime
from pathlib import Path
from PyQt6.QtCore import QThread, pyqtSignal


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
        os.makedirs(self._workflows_dir, exist_ok=True)
        with zipfile.ZipFile(
            self.export_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6
        ) as zipf:
            total_items = len(self.workflows)
            if self.include_models and self._models_dir.exists():
                total_items += len(list(self._models_dir.rglob("*")))
            if self.include_data and self._data_dir.exists():
                total_items += len(list(self._data_dir.rglob("*")))

            for idx, workflow in enumerate(self.workflows):
                workflow_file = self._workflows_dir / f"{workflow}.json"
                if workflow_file.exists():
                    zipf.write(workflow_file, f"workflows/{workflow}.json")
                self.progress.emit(int((idx / max(1, total_items)) * 80))

            if self.include_models and self._models_dir.exists():
                for file_path in self._models_dir.rglob("*"):
                    if file_path.is_file():
                        zipf.write(file_path, file_path.relative_to(Path(".")))
                self.progress.emit(85)

            if self.include_data and self._data_dir.exists():
                for file_path in self._data_dir.rglob("*"):
                    if file_path.is_file():
                        zipf.write(file_path, file_path.relative_to(Path(".")))
                self.progress.emit(90)

            manifest = {
                "version": "2.0",
                "exported_at": datetime.now().isoformat(),
                "workflows": self.workflows,
                "models_included": self.include_models,
                "data_included": self.include_data,
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
        imported_workflows = []

        with zipfile.ZipFile(self.import_path, "r") as zipf:
            manifest_data = zipf.read("manifest.json")
            manifest = json.loads(manifest_data)

            workflows = manifest.get("workflows", [])
            total_items = len(workflows)
            if manifest.get("models_included"):
                total_items += 1
            if manifest.get("data_included"):
                total_items += 1

            os.makedirs("workflows", exist_ok=True)

            for idx, workflow in enumerate(workflows):
                workflow_file = f"workflows/{workflow}.json"
                if workflow_file in zipf.namelist():
                    zipf.extract(workflow_file, ".")
                    imported_workflows.append(workflow)
                self.progress.emit(int((idx / max(1, total_items)) * 80))

            if manifest.get("models_included"):
                for file_info in zipf.infolist():
                    if file_info.filename.startswith("models/"):
                        zipf.extract(file_info.filename, ".")
                self.progress.emit(90)

            if manifest.get("data_included"):
                for file_info in zipf.infolist():
                    if file_info.filename.startswith("data/"):
                        zipf.extract(file_info.filename, ".")
                self.progress.emit(95)

            self.progress.emit(100)

        return imported_workflows


__all__ = ["ExportWorker", "ImportWorker"]
