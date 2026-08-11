import datetime
import json
from collections import deque

from PyQt6.QtCore import Qt, QThread, QTimer, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QFont, QTextCursor
from PyQt6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class LogExport(QThread):
    finished = pyqtSignal()

    def __init__(self, logs, fname) -> None:
        super().__init__()
        self.log_dict = logs
        self.fname = fname

    @pyqtSlot()
    def run(self):
        try:
            with open(self.fname, "w") as f:
                json.dump(self.log_dict, f, separators=(",", ":"))
        except Exception as e:
            print(e)
        self.finished.emit()


class LogEntry:
    __slots__ = ["timestamp", "level", "message", "node_id", "node_name"]

    def __init__(self, timestamp, level, message, node_id=None, node_name=None):
        self.timestamp = timestamp
        self.level = level
        self.message = message
        self.node_id = node_id
        self.node_name = node_name


class DebugConsole(QWidget):
    log_added = pyqtSignal(LogEntry)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logs = deque(maxlen=500)
        self._node_names = set()
        self._cached_metrics = {}
        self._update_timer = QTimer()
        self._update_timer.timeout.connect(self.update_metrics)
        self._update_timer.start(5000)

        self._current_level_filter = "All"
        self._current_node_filter = "All"

        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(28, 28, 28, 28)
        self.layout.setSpacing(20)

        title = QLabel("Debug Console")
        title.setFont(QFont("Poppins", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #F0F2F8; background: transparent;")
        self.layout.addWidget(title)

        subtitle = QLabel("Live Application Trace Logs & Metric Stream")
        subtitle.setFont(QFont("Poppins", 11))
        subtitle.setStyleSheet("color: #4A5578; margin-bottom: 4px;")
        self.layout.addWidget(subtitle)

        # Controls row (no group box for cleaner look)
        controls_row = QHBoxLayout()
        controls_row.setSpacing(10)

        level_label = QLabel("Level")
        level_label.setFont(QFont("Poppins", 10, QFont.Weight.DemiBold))
        level_label.setStyleSheet("color: #4A5578; letter-spacing: 0.5px;")
        controls_row.addWidget(level_label)

        self.level_combo = QComboBox()
        self.level_combo.addItems(["All", "ERROR", "WARNING", "INFO", "DEBUG"])
        self.level_combo.setFixedHeight(34)
        self.level_combo.setMinimumWidth(110)
        self.level_combo.currentTextChanged.connect(self.filter_logs)
        controls_row.addWidget(self.level_combo)

        node_label = QLabel("Node")
        node_label.setFont(QFont("Poppins", 10, QFont.Weight.DemiBold))
        node_label.setStyleSheet("color: #4A5578; letter-spacing: 0.5px; margin-left: 8px;")
        controls_row.addWidget(node_label)

        self.node_combo = QComboBox()
        self.node_combo.addItem("All")
        self.node_combo.setFixedHeight(34)
        self.node_combo.setMinimumWidth(130)
        self.node_combo.currentTextChanged.connect(self.filter_logs)
        controls_row.addWidget(self.node_combo)

        controls_row.addStretch()

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_logs)
        self.clear_button.setFixedHeight(34)
        self.clear_button.setFont(QFont("Poppins", 10, QFont.Weight.Medium))
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #161922;
                color: #8892B0;
                border: 1px solid #1E2538;
                border-radius: 8px;
                padding: 4px 16px;
            }
            QPushButton:hover {
                background-color: #1C2235;
                border-color: #6366F1;
                color: #F0F2F8;
            }
        """)
        controls_row.addWidget(self.clear_button)

        self.export_button = QPushButton("Export Logs")
        self.export_button.clicked.connect(self.export_logs)
        self.export_button.setFixedHeight(34)
        self.export_button.setFont(QFont("Poppins", 10, QFont.Weight.DemiBold))
        self.export_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(99,102,241,0.15);
                color: #818CF8;
                border: 1px solid rgba(99,102,241,0.3);
                border-radius: 8px;
                padding: 4px 16px;
            }
            QPushButton:hover {
                background-color: rgba(99,102,241,0.25);
                border-color: #6366F1;
                color: #A5B4FC;
            }
        """)
        controls_row.addWidget(self.export_button)

        self.layout.addLayout(controls_row)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.splitter.addWidget(self.log_display)

        self.metrics_widget = self.create_metrics_widget()
        self.splitter.addWidget(self.metrics_widget)

        self.splitter.setSizes([800, 400])
        self.splitter.setHandleWidth(10)
        self.layout.addWidget(self.splitter)

    def create_metrics_widget(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        metrics_group = QGroupBox("Log Metrics")
        metrics_group.setFont(QFont("Poppins", 12, QFont.Weight.Bold))

        group_layout = QVBoxLayout(metrics_group)
        self.metrics_table = QTableWidget()
        self.metrics_table.setColumnCount(2)
        self.metrics_table.setHorizontalHeaderLabels(["Metric", "Value"])
        self.metrics_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        group_layout.addWidget(self.metrics_table)

        layout.addWidget(metrics_group)
        self.update_metrics()
        return widget

    def apply_styles(self):
        self.setStyleSheet("QWidget { background-color: #0A0C10; color: #F0F2F8; }")
        self.log_display.setFont(QFont("Consolas", 11))
        self.log_display.setStyleSheet("""
            QTextEdit {
                border: 1px solid #1E2538;
                border-radius: 10px;
                padding: 12px;
                background-color: #06080E;
                color: #A8B4C8;
                selection-background-color: rgba(99,102,241,0.35);
            }
        """)

    def _log_matches_filter(self, log_entry):
        level_match = (
            self._current_level_filter == "All"
            or log_entry.level == self._current_level_filter
        )
        node_match = (
            self._current_node_filter == "All"
            or log_entry.node_name == self._current_node_filter
        )
        return level_match and node_match

    def add_log(self, level, message, node_id=None, node_name=None):
        level = level.upper()
        log_entry = LogEntry(
            datetime.datetime.now(), level, message, node_id, node_name
        )
        self.logs.append(log_entry)

        if node_name and node_name not in self._node_names:
            self._node_names.add(node_name)
            self.node_combo.addItem(node_name)

        self.log_added.emit(log_entry)

        if self._log_matches_filter(log_entry):
            self._append_single_log(log_entry)

    def _append_single_log(self, log_entry):
        cursor = self.log_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        if not self.log_display.toPlainText().strip() == "":
            cursor.insertText("\n")

        cursor.insertText(self._format_log_entry(log_entry))
        self.log_display.moveCursor(QTextCursor.MoveOperation.End)

    def update_log_display(self):
        self.log_display.clear()
        level_filter = self.level_combo.currentText()
        node_filter = self.node_combo.currentText()

        filtered_logs = [
            log
            for log in self.logs
            if (level_filter == "All" or log.level == level_filter)
            and (node_filter == "All" or log.node_name == node_filter)
        ]

        if filtered_logs:
            log_text = "\n".join(self._format_log_entry(log) for log in filtered_logs)
            self.log_display.setPlainText(log_text)

        self.log_display.moveCursor(QTextCursor.MoveOperation.End)

    def _format_log_entry(self, log):
        timestamp_str = log.timestamp.strftime("%H:%M:%S")
        node_info = f" [{log.node_name}]" if log.node_name else ""
        return f"[{timestamp_str}] {log.level}{node_info}: {log.message}"

    def filter_logs(self):
        self._current_level_filter = self.level_combo.currentText()
        self._current_node_filter = self.node_combo.currentText()
        self.update_log_display()

    def clear_logs(self):
        self.logs.clear()
        self.log_display.clear()
        self._node_names.clear()
        self._cached_metrics.clear()
        self.node_combo.clear()
        self.node_combo.addItem("All")
        self.update_metrics()

    def export_logs(self):
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"nodebox_logs_{timestamp}.json"
            logs_data = [
                {
                    "timestamp": log.timestamp.isoformat(),
                    "level": log.level,
                    "message": log.message,
                    "node_id": log.node_id,
                    "node_name": log.node_name,
                }
                for log in self.logs
            ]

            def on_thread_complete():
                self.export_button.setEnabled(True)
                self.clear_button.setEnabled(True)
                self.export_button.setText("Export Logs")
                self.add_log("INFO", f"Logs exported to {filename}")
                del self.worker

            self.worker = LogExport(logs_data, filename)
            self.worker.finished.connect(on_thread_complete)
            self.worker.finished.connect(self.worker.deleteLater)
            self.export_button.setEnabled(False)
            self.clear_button.setEnabled(False)
            self.export_button.setText("Exporting...")
            self.worker.start()
        except Exception as e:
            self.add_log("ERROR", f"Export failed: {str(e)}")

    def update_metrics(self):
        total_logs = len(self.logs)
        error_count = sum(1 for log in self.logs if log.level == "ERROR")
        warning_count = sum(1 for log in self.logs if log.level == "WARNING")

        current_metrics = {
            "Total Logs": str(total_logs),
            "Errors": str(error_count),
            "Warnings": str(warning_count),
            "Error Rate": (
                f"{(error_count / total_logs * 100):.1f}%" if total_logs > 0 else "0%"
            ),
            "Last Update": datetime.datetime.now().strftime("%H:%M:%S"),
        }

        if self.metrics_table.rowCount() == 0:
            self.metrics_table.setRowCount(len(current_metrics))
            for i, metric_name in enumerate(current_metrics.keys()):
                self.metrics_table.setItem(i, 0, QTableWidgetItem(metric_name))
                self.metrics_table.setItem(
                    i, 1, QTableWidgetItem(current_metrics[metric_name])
                )
            self._cached_metrics = current_metrics.copy()
            return

        for i, (metric_name, new_value) in enumerate(current_metrics.items()):
            if self._cached_metrics.get(metric_name) != new_value:
                self.metrics_table.setItem(i, 1, QTableWidgetItem(new_value))
                self._cached_metrics[metric_name] = new_value

    def log_node_execution(self, node_name, success, execution_time, error=None):
        if success:
            self.add_log(
                "INFO",
                f"Node '{node_name}' executed successfully in {execution_time:.3f}s",
                node_name=node_name,
            )
        else:
            self.add_log(
                "ERROR", f"Node '{node_name}' failed: {error}", node_name=node_name
            )

    def log_workflow_start(self, workflow_name):
        self.add_log("INFO", f"Starting workflow: {workflow_name}")

    def log_workflow_end(self, workflow_name, success, total_time):
        if success:
            self.add_log(
                "INFO",
                f"Workflow '{workflow_name}' completed successfully in {total_time:.3f}s",
            )
        else:
            self.add_log(
                "ERROR", f"Workflow '{workflow_name}' failed after {total_time:.3f}s"
            )


__all__ = ["DebugConsole", "LogEntry", "LogExport"]
