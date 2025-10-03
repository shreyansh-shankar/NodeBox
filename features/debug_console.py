"""
Optimized Debug Console - Efficient logging and monitoring
"""
import datetime
import json
from collections import deque

from PyQt6.QtCore import Qt, QThread, QTimer, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QFont, QTextCursor
from PyQt6.QtWidgets import (
    QComboBox,
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
                json.dump(self.log_dict, f, separators=(",", ":"))  # Compact JSON
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
        self.logs = deque(maxlen=500)  # Use deque for efficient append/pop
        self.max_logs = 500
        self._node_names = set()
        self._cached_metrics = {}  # Cache for previous metric values
        self._update_timer = QTimer()
        self._update_timer.timeout.connect(self.update_metrics)
        self._update_timer.start(5000)  # Update metrics every 5 seconds
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()

        # Minimalist title
        self.title = QLabel("Debug Console")
        self.title.setFont(QFont("Poppins", 14, QFont.Weight.Bold))
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.title)

        # Compact controls
        self.controls_layout = QHBoxLayout()

        self.level_combo = QComboBox()
        self.level_combo.addItems(["All", "ERROR", "WARNING", "INFO", "DEBUG"])
        self.level_combo.currentTextChanged.connect(self.filter_logs)
        self.controls_layout.addWidget(QLabel("Level:"))
        self.controls_layout.addWidget(self.level_combo)

        self.node_combo = QComboBox()
        self.node_combo.addItem("All")
        self.node_combo.currentTextChanged.connect(self.filter_logs)
        self.controls_layout.addWidget(QLabel("Node:"))
        self.controls_layout.addWidget(self.node_combo)

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_logs)
        self.clear_button.setStyleSheet("QPushButton { padding: 4px 8px; }")
        self.controls_layout.addWidget(self.clear_button)

        self.export_button = QPushButton("Export")
        self.export_button.clicked.connect(self.export_logs)
        self.export_button.setStyleSheet("QPushButton { padding: 4px 8px; }")
        self.controls_layout.addWidget(self.export_button)

        self.layout.addLayout(self.controls_layout)

        # Main content area
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QFont("Consolas", 10))
        self.splitter.addWidget(self.log_display)

        # Performance metrics
        self.metrics_widget = self.create_metrics_widget()
        self.splitter.addWidget(self.metrics_widget)

        self.splitter.setSizes([800, 400])
        self.layout.addWidget(self.splitter)

        self.setLayout(self.layout)

    def create_metrics_widget(self):
        """Create performance metrics widget"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Title
        title = QLabel("Performance Metrics")
        title.setFont(QFont("Poppins", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        # Metrics table
        self.metrics_table = QTableWidget()
        self.metrics_table.setColumnCount(2)
        self.metrics_table.setHorizontalHeaderLabels(["Metric", "Value"])
        self.metrics_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        layout.addWidget(self.metrics_table)

        # Update metrics
        self.update_metrics()

        widget.setLayout(layout)
        return widget

    def setup_logging(self):
        """Setup logging capture"""
        # This would integrate with Python's logging module

    def add_log(self, level, message, node_id=None, node_name=None):
        """Optimized log entry addition"""
        level = level.upper()  # Normalize log level to uppercase
        log_entry = LogEntry(
            datetime.datetime.now(), level, message, node_id, node_name
        )

        self.logs.append(log_entry)  # deque automatically handles maxlen

        # Update node combo if new node
        if node_name and node_name not in self._node_names:
            self._node_names.add(node_name)
            self.node_combo.addItem(node_name)

        self.log_added.emit(log_entry)
        self.update_log_display()

    def update_log_display(self):
        """Optimized log display update"""
        self.log_display.clear()

        level_filter = self.level_combo.currentText()
        node_filter = self.node_combo.currentText()

        # Filter logs efficiently
        filtered_logs = [
            log
            for log in self.logs
            if (level_filter == "All" or log.level == level_filter)
            and (node_filter == "All" or log.node_name == node_filter)
        ]

        # Build display text efficiently
        log_text = "\n".join(self._format_log_entry(log) for log in filtered_logs)
        self.log_display.setPlainText(log_text)
        self.log_display.moveCursor(QTextCursor.MoveOperation.End)

    def _format_log_entry(self, log):
        """Format a single log entry for display"""
        timestamp_str = log.timestamp.strftime("%H:%M:%S")
        node_info = f" [{log.node_name}]" if log.node_name else ""
        return f"[{timestamp_str}] {log.level}{node_info}: {log.message}"

    def filter_logs(self):
        """Filter logs based on current filters"""
        self.update_log_display()

    def clear_logs(self):
        """Clear all logs efficiently"""
        self.logs.clear()
        self.log_display.clear()
        self._node_names.clear()
        self._cached_metrics.clear()  # Clear cached metrics
        self.node_combo.clear()
        self.node_combo.addItem("All")
        self.update_metrics()

    def export_logs(self):
        """Optimized log export"""
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
                self.export_button.setText("Export")
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
        """Update performance metrics - optimized to only update changed values"""
        # Calculate current metrics
        total_logs = len(self.logs)
        error_count = len([log for log in self.logs if log.level == "ERROR"])
        warning_count = len([log for log in self.logs if log.level == "WARNING"])

        current_metrics = {
            "Total Logs": str(total_logs),
            "Errors": str(error_count),
            "Warnings": str(warning_count),
            "Error Rate": f"{(error_count/total_logs*100):.1f}%"
            if total_logs > 0
            else "0%",
            "Last Update": datetime.datetime.now().strftime("%H:%M:%S"),
        }

        # Initialize table if empty
        if self.metrics_table.rowCount() == 0:
            self.metrics_table.setRowCount(len(current_metrics))
            for i, metric_name in enumerate(current_metrics.keys()):
                self.metrics_table.setItem(i, 0, QTableWidgetItem(metric_name))
                self.metrics_table.setItem(
                    i, 1, QTableWidgetItem(current_metrics[metric_name])
                )
            self._cached_metrics = current_metrics.copy()
            return

        # Update only changed cells
        for i, (metric_name, new_value) in enumerate(current_metrics.items()):
            cached_value = self._cached_metrics.get(metric_name)
            if cached_value != new_value:
                # Only update the value cell if it has changed
                self.metrics_table.setItem(i, 1, QTableWidgetItem(new_value))
                self._cached_metrics[metric_name] = new_value

    def log_node_execution(self, node_name, success, execution_time, error=None):
        """Log node execution details"""
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
        """Log workflow start"""
        self.add_log("INFO", f"Starting workflow: {workflow_name}")

    def log_workflow_end(self, workflow_name, success, total_time):
        """Log workflow completion"""
        if success:
            self.add_log(
                "INFO",
                f"Workflow '{workflow_name}' completed successfully in {total_time:.3f}s",
            )
        else:
            self.add_log(
                "ERROR", f"Workflow '{workflow_name}' failed after {total_time:.3f}s"
            )
