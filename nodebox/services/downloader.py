import subprocess
from PyQt6.QtCore import QThread, pyqtSignal


class DownloadWorker(QThread):
    """Worker thread for pulling models via Ollama CLI."""

    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(bool)

    def __init__(self, model_name: str, model_size: str):
        super().__init__()
        self.model_name = model_name
        self.model_size = model_size
        self.process = None

    def run(self):
        try:
            self.status.emit(f"Starting download: {self.model_name}:{self.model_size}")
            cmd = ["ollama", "pull", f"{self.model_name}:{self.model_size}"]

            self.process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
            )

            for line in self.process.stdout:
                self.status.emit(line.strip())
                if "%" in line:
                    try:
                        percent = int(line.split("%")[0].split()[-1])
                        self.progress.emit(percent)
                    except (ValueError, IndexError):
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


__all__ = ["DownloadWorker"]
