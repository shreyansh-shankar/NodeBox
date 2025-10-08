"""
Optimized and restyled Debug Console with incremental updates
"""
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
        
        # Cache current filter state for optimization
        self._current_level_filter = "All"
        self._current_node_filter = "All"
        
        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        # Main layout consistent with Home tab
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(24, 24, 24, 24)
        self.layout.setSpacing(16)

        # Title and Subtitle, matching Home tab style
        title = QLabel("Debug Console")
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(title)

        subtitle = QLabel("Live application logs and performance metrics")
        subtitle.setFont(QFont("Segoe UI", 13))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #a0a0a0; margin-bottom: 16px;")
        self.layout.addWidget(subtitle)

        # GroupBox for controls, for a cleaner look
        controls_group = QGroupBox("Filters & Actions")
        controls_group.setFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))

        self.controls_layout = QHBoxLayout()
        self.controls_layout.setSpacing(12)

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

        self.controls_layout.addStretch()  # Add space to push buttons to the right

        self.clear_button = QPushButton("Clear Logs")
        self.clear_button.clicked.connect(self.clear_logs)
        self.controls_layout.addWidget(self.clear_button)

        self.export_button = QPushButton("Export Logs")
        self.export_button.clicked.connect(self.export_logs)
        self.controls_layout.addWidget(self.export_button)

        controls_group.setLayout(self.controls_layout)
        self.layout.addWidget(controls_group)

        # Main content area with a splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.splitter.addWidget(self.log_display)

        self.metrics_widget = self.create_metrics_widget()
        self.splitter.addWidget(self.metrics_widget)

        self.splitter.setSizes([800, 400])  # Initial size ratio
        self.splitter.setHandleWidth(10)  # Make the splitter handle more visible
        self.layout.addWidget(self.splitter)

    def create_metrics_widget(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # GroupBox for metrics
        metrics_group = QGroupBox("Performance Metrics")
        metrics_group.setFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))

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
        """Apply styles consistent with the Home tab"""
        self.setStyleSheet(
            """
            QGroupBox {
                border: 1px solid #3e3e42;
                border-radius: 6px;
                margin-top: 10px;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                left: 10px;
            }
            QPushButton {
                padding: 8px 16px;
                background-color: #3e3e42;
                border: 1px solid #555555;
                border-radius: 4px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #4f4f53;
            }
            QPushButton:pressed {
                background-color: #2d2d30;
            }
            QComboBox {
                padding: 8px;
                border: 1px solid #3e3e42;
                border-radius: 4px;
                background-color: #2d2d30;
            }
            QSplitter::handle {
                background-color: #3e3e42;
            }
            QTableWidget {
                border: none;
                gridline-color: #3e3e42;
            }
            QHeaderView::section {
                background-color: #2d2d30;
                padding: 4px;
                border: 1px solid #3e3e42;
            }
        """
        )
        self.log_display.setFont(QFont("Consolas", 10))
        self.log_display.setStyleSheet(
            """
            QTextEdit {
                border: 1px solid #3e3e42;
                border-radius: 6px;
                padding: 8px;
                background-color: #1e1e1e;
            }
        """
        )

    def _log_matches_filter(self, log_entry):
        """Check if log entry matches current filters"""
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
        """Optimized: Only append new log if it matches current filters"""
        level = level.upper()
        log_entry = LogEntry(datetime.datetime.now(), level, message, node_id, node_name)
        self.logs.append(log_entry)

        if node_name and node_name not in self._node_names:
            self._node_names.add(node_name)
            self.node_combo.addItem(node_name)

        self.log_added.emit(log_entry)

        #  OPTIMIZATION: Only append if log matches current filters
        if self._log_matches_filter(log_entry):
            self._append_single_log(log_entry)

    def _append_single_log(self, log_entry):
        """Incrementally append a single log entry without rebuilding"""
        cursor = self.log_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        # Add newline if not first entry
        if not self.log_display.toPlainText().strip() == "":
            cursor.insertText("\n")

        cursor.insertText(self._format_log_entry(log_entry))
        
        # Auto-scroll to bottom
        self.log_display.moveCursor(QTextCursor.MoveOperation.End)

    def update_log_display(self):
        """Full rebuild - only called when filters change"""
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
        """Format a single log entry for display"""
        timestamp_str = log.timestamp.strftime("%H:%M:%S")
        node_info = f" [{log.node_name}]" if log.node_name else ""
        return f"[{timestamp_str}] {log.level}{node_info}: {log.message}"

    def filter_logs(self):
        """Called when filter combo boxes change"""
        # Update cached filter state
        self._current_level_filter = self.level_combo.currentText()
        self._current_node_filter = self.node_combo.currentText()
        
        # Rebuild display with new filters
        self.update_log_display()

    def clear_logs(self):
        """Clear all logs efficiently"""
        self.logs.clear()
        self.log_display.clear()
        self._node_names.clear()
        self._cached_metrics.clear()
        self.node_combo.clear()
        self.node_combo.addItem("All")
        self.update_metrics()

    def export_logs(self):
        """Export logs to JSON file"""
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
        """Update performance metrics - only updates changed cells"""
        total_logs = len(self.logs)
        error_count = sum(1 for log in self.logs if log.level == "ERROR")
        warning_count = sum(1 for log in self.logs if log.level == "WARNING")
        
        current_metrics = {
            "Total Logs": str(total_logs),
            "Errors": str(error_count),
            "Warnings": str(warning_count),
            "Error Rate": f"{(error_count / total_logs * 100):.1f}%"
            if total_logs > 0
            else "0%",
            "Last Update": datetime.datetime.now().strftime("%H:%M:%S"),
        }

        if self.metrics_table.rowCount() == 0:
            self.metrics_table.setRowCount(len(current_metrics))
            for i, metric_name in enumerate(current_metrics.keys()):
                self.metrics_table.setItem(i, 0, QTableWidgetItem(metric_name))
                self.metrics_table.setItem(i, 1, QTableWidgetItem(current_metrics[metric_name]))
            self._cached_metrics = current_metrics.copy()
            return

        for i, (metric_name, new_value) in enumerate(current_metrics.items()):
            if self._cached_metrics.get(metric_name) != new_value:
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
            self.add_log("ERROR", f"Node '{node_name}' failed: {error}", node_name=node_name)

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
