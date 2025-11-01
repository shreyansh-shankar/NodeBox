from PyQt6.QtCore import QDateTime, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QTextCharFormat, QTextCursor
from PyQt6.QtWidgets import QTextEdit


class OutputConsole(QTextEdit):
    log_signal = pyqtSignal(str, str)  # message, type ('info' or 'error')

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setFont(QFont("Consolas", 10))
        self.setStyleSheet("background-color: #111; color: #EEE; border: none;")
        self.log_signal.connect(self._append_log)

    def _append_log(self, message: str, msg_type: str = "info"):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        fmt = QTextCharFormat()
        if msg_type == "error":
            fmt.setForeground(QColor("#FF5555"))
        else:
            fmt.setForeground(QColor("#AAAAAA"))

        timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
        cursor.insertText(f"[{timestamp}] ", fmt)

        fmt.setForeground(
            QColor("#FFFFFF") if msg_type == "info" else QColor("#FF8888")
        )
        cursor.insertText(message.strip() + "\n", fmt)
        self.setTextCursor(cursor)
        self.ensureCursorVisible()

    def clear_output(self):
        self.clear()

    # Backwards-compatible convenience methods used elsewhere in the codebase
    def appendPlainText(self, text: str):
        """Append informational text to the console (keeps timestamp and formatting)."""
        try:
            self.log_signal.emit(str(text), "info")
        except Exception:
            # Fallback to direct insert if signal fails
            try:
                self._append_log(str(text), "info")
            except Exception:
                pass

    def appendError(self, text: str):
        """Append an error message with error styling."""
        try:
            self.log_signal.emit(str(text), "error")
        except Exception:
            try:
                self._append_log(str(text), "error")
            except Exception:
                pass
