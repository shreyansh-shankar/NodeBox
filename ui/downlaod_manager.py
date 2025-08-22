import sys
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QProgressBar, QTextEdit
)
from PyQt6.QtCore import QThread, pyqtSignal

# Worker thread for downloading
class DownloadWorker(QThread):
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(bool)

    def __init__(self, model_name, model_size):
        super().__init__()
        self.model_name = model_name
        self.model_size = model_size
        self.process = None

    def run(self):
        try:
            self.status.emit(f"Starting download: {self.model_name}:{self.model_size}")
            cmd = ["ollama", "pull", f"{self.model_name}:{self.model_size}"]

            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

            for line in self.process.stdout:
                self.status.emit(line.strip())
                # crude progress estimation (we can refine later)
                if "%" in line:
                    try:
                        percent = int(line.split("%")[0].split()[-1])
                        self.progress.emit(percent)
                    except:
                        pass

            self.process.wait()
            if self.process.returncode == 0:
                self.finished.emit(True)
            else:
                self.finished.emit(False)

        except Exception as e:
            self.status.emit(str(e))
            self.finished.emit(False)

    def stop(self):
        if self.process:
            self.process.terminate()


# Download Manager Window
class DownloadManager(QDialog):
    def __init__(self, model_name, sizes, parent=None):
        super().__init__(parent)
        self.model_name = model_name
        self.sizes = sizes

        self.setWindowTitle("Download Manager")
        self.setModal(True)
        self.resize(400, 300)

        layout = QVBoxLayout()

        self.label = QLabel(f"Download model: {model_name}")
        layout.addWidget(self.label)

        self.size_combo = QComboBox()
        self.size_combo.addItems(sizes)
        layout.addWidget(self.size_combo)

        self.start_btn = QPushButton("Start Download")
        layout.addWidget(self.start_btn)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setEnabled(False)
        layout.addWidget(self.cancel_btn)

        self.setLayout(layout)

        self.worker = None
        self.model_name = model_name

        self.start_btn.clicked.connect(self.start_download)
        self.cancel_btn.clicked.connect(self.cancel_download)

    def start_download(self):
        size = self.size_combo.currentText()
        self.worker = DownloadWorker(self.model_name, size)
        self.worker.progress.connect(self.update_progress)
        self.worker.status.connect(self.update_log)
        self.worker.finished.connect(self.download_finished)

        self.start_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.worker.start()

    def cancel_download(self):
        if self.worker:
            self.worker.stop()
            self.update_log("Download canceled.")
            self.cancel_btn.setEnabled(False)
            self.start_btn.setEnabled(True)

    def update_progress(self, val):
        self.progress.setValue(val)

    def update_log(self, msg):
        self.log.append(msg)

    def download_finished(self, success):
        if success:
            self.update_log("✅ Download completed successfully.")
        else:
            self.update_log("❌ Download failed.")
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)