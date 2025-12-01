from __future__ import annotations

import subprocess
import sys
import threading
from contextlib import suppress

from PyQt6.QtCore import QObject, QThread, pyqtSignal

from utils.node_runner import (
    NODE_OUTPUT_MARKER,
    build_temp_node_script,
    cleanup_temp_script,
    parse_node_process_result,
)


class LiveCodeRunner(QObject):
    """Runs node code in a background thread with cancellable subprocess support."""

    stdout = pyqtSignal(str)
    stderr = pyqtSignal(str)
    finished = pyqtSignal(dict)
    failed = pyqtSignal(str)
    cancelled = pyqtSignal()
    state_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._thread: QThread | None = None
        self._worker: _RunnerWorker | None = None

    def is_running(self) -> bool:
        return self._worker is not None

    def run(self, code: str, inputs: dict) -> bool:
        if self.is_running():
            return False

        self._thread = QThread()
        self._worker = _RunnerWorker(code, inputs)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.execute)
        self._worker.finished.connect(self._thread.quit)
        self._worker.failed.connect(self._thread.quit)
        self._worker.cancelled.connect(self._thread.quit)
        self._thread.finished.connect(self._teardown)

        self._worker.stdout.connect(self.stdout.emit)
        self._worker.stderr.connect(self.stderr.emit)
        self._worker.finished.connect(self.finished.emit)
        self._worker.failed.connect(self.failed.emit)
        self._worker.cancelled.connect(self.cancelled.emit)
        self._worker.state_changed.connect(self.state_changed.emit)

        self._thread.start()
        self.state_changed.emit("starting")
        return True

    def stop(self):
        if self._worker:
            self._worker.stop()

    def _teardown(self):
        self.state_changed.emit("idle")
        if self._thread:
            self._thread.wait()
        self._thread = None
        self._worker = None


class _RunnerWorker(QObject):
    stdout = pyqtSignal(str)
    stderr = pyqtSignal(str)
    finished = pyqtSignal(dict)
    failed = pyqtSignal(str)
    cancelled = pyqtSignal()
    state_changed = pyqtSignal(str)

    def __init__(self, code: str, inputs: dict):
        super().__init__()
        self._code = code
        self._inputs = inputs or {}
        self._proc: subprocess.Popen | None = None
        self._temp_name: str | None = None
        self._marker = NODE_OUTPUT_MARKER
        self._prelude_lines = 0
        self._cancel_requested = False

    def execute(self):
        self.state_changed.emit("running")
        try:
            self._temp_name, self._marker, self._prelude_lines = build_temp_node_script(
                self._code, self._inputs, marker=self._marker
            )
            self._proc = subprocess.Popen(
                [sys.executable, self._temp_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )

            stdout_lines: list[str] = []
            stderr_lines: list[str] = []
            marker_state = {"seen": False}

            def pump(stream, signal, store, filter_marker=False):
                for line in iter(stream.readline, ""):
                    if not line:
                        break
                    store.append(line)
                    if filter_marker:
                        if self._marker in line:
                            marker_state["seen"] = True
                            continue
                        if marker_state["seen"]:
                            continue
                    signal.emit(line.rstrip("\n"))
                stream.close()

            threads = [
                threading.Thread(
                    target=pump,
                    args=(self._proc.stdout, self.stdout, stdout_lines, True),
                    daemon=True,
                ),
                threading.Thread(
                    target=pump,
                    args=(self._proc.stderr, self.stderr, stderr_lines, False),
                    daemon=True,
                ),
            ]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

            return_code = self._proc.wait()
            if self._cancel_requested:
                self.cancelled.emit()
                return

            result = parse_node_process_result(
                "".join(stdout_lines), "".join(stderr_lines), return_code, self._marker
            )
            result["prelude_lines"] = self._prelude_lines
            self.finished.emit(result)
        except Exception as exc:
            self.failed.emit(str(exc))
        finally:
            if self._temp_name:
                cleanup_temp_script(self._temp_name)
            self.state_changed.emit("idle")

    def stop(self):
        self._cancel_requested = True
        if self._proc and self._proc.poll() is None:
            with suppress(Exception):
                self._proc.terminate()
            threading.Timer(0.75, self._force_kill).start()

    def _force_kill(self):
        if self._proc and self._proc.poll() is None:
            with suppress(Exception):
                self._proc.kill()

