from PyQt6.QtCore import QDateTime, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QTextCharFormat, QTextCursor
from PyQt6.QtWidgets import QTextEdit


class OutputConsole(QTextEdit):
    log_signal = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setFont(QFont("Consolas", 10))
        self.setStyleSheet(
            """
            QTextEdit {
                background-color: #0F1117;
                color: #F9FAFB;
                border: 1px solid #2E3444;
                border-radius: 8px;
                padding: 10px;
            }
        """
        )
        self.log_signal.connect(self._append_log)

    def _append_log(self, message: str, msg_type: str = "info"):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        fmt = QTextCharFormat()

        fmt.setForeground(QColor("#6B7280"))
        timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
        cursor.insertText(f"[{timestamp}] ", fmt)

        msg_str = message.strip()
        if msg_type == "error" or "error" in msg_str.lower() or "[error]" in msg_str.lower():
            fmt.setForeground(QColor("#EF4444"))
        elif "success" in msg_str.lower() or "[ok]" in msg_str.lower() or "completed" in msg_str.lower():
            fmt.setForeground(QColor("#10B981"))
        elif "starting" in msg_str.lower():
            fmt.setForeground(QColor("#818CF8"))
        else:
            fmt.setForeground(QColor("#E5E7EB"))

        cursor.insertText(msg_str + "\n", fmt)
        self.setTextCursor(cursor)
        self.ensureCursorVisible()

    def clear_output(self):
        self.clear()

    def appendPlainText(self, text: str):
        try:
            self.log_signal.emit(str(text), "info")
        except Exception:
            try:
                self._append_log(str(text), "info")
            except Exception:
                pass

    def appendError(self, text: str):
        try:
            self.log_signal.emit(str(text), "error")
        except Exception:
            try:
                self._append_log(str(text), "error")
            except Exception:
                pass


__all__ = ["OutputConsole"]
