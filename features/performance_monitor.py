"""
Optimized Performance Monitor - Minimal resource usage
"""
import json
from collections import deque
from datetime import datetime

import psutil
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class PerformanceMetrics:
    __slots__ = [
        "cpu_usage",
        "memory_usage",
        "disk_usage",
        "network_sent",
        "network_recv",
        "timestamp",
        "active_nodes",
        "total_nodes",
        "workflows_running",
        "execution_time",
        "error_count",
    ]

    def __init__(self):
        self.cpu_usage = 0.0
        self.memory_usage = 0.0
        self.disk_usage = 0.0
        self.network_sent = 0
        self.network_recv = 0
        self.timestamp = datetime.now()

        # NodeBox specific metrics
        self.active_nodes = 0
        self.total_nodes = 0
        self.workflows_running = 0
        self.execution_time = 0.0
        self.error_count = 0


class PerformanceMonitor(QWidget):
    metrics_updated = pyqtSignal(PerformanceMetrics)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.metrics = PerformanceMetrics()
        self.history = deque(maxlen=50)  # Reduced history size
        self.monitoring = True
        self._update_interval = 2000  # 2 seconds for better performance

        # Network baseline
        self.network_baseline = psutil.net_io_counters()

        self.init_ui()
        self._subscribe_bus()
        self.start_monitoring()

    def init_ui(self):
        layout = QVBoxLayout()

        # Minimalist title
        title = QLabel("Performance")
        title.setFont(QFont("Poppins", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Compact controls
        controls_layout = QHBoxLayout()

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_monitoring)
        self.start_button.setStyleSheet("QPushButton { padding: 4px 8px; }")
        controls_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_monitoring)
        self.stop_button.setStyleSheet("QPushButton { padding: 4px 8px; }")
        controls_layout.addWidget(self.stop_button)

        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_metrics)
        self.reset_button.setStyleSheet("QPushButton { padding: 4px 8px; }")
        controls_layout.addWidget(self.reset_button)

        layout.addLayout(controls_layout)

        # System metrics
        system_group = QGroupBox("System Metrics")
        system_layout = QGridLayout()

        # CPU Usage
        self.cpu_label = QLabel("CPU Usage:")
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setRange(0, 100)
        system_layout.addWidget(self.cpu_label, 0, 0)
        system_layout.addWidget(self.cpu_progress, 0, 1)

        # Memory Usage
        self.memory_label = QLabel("Memory Usage:")
        self.memory_progress = QProgressBar()
        self.memory_progress.setRange(0, 100)
        system_layout.addWidget(self.memory_label, 1, 0)
        system_layout.addWidget(self.memory_progress, 1, 1)

        # Disk Usage
        self.disk_label = QLabel("Disk Usage:")
        self.disk_progress = QProgressBar()
        self.disk_progress.setRange(0, 100)
        system_layout.addWidget(self.disk_label, 2, 0)
        system_layout.addWidget(self.disk_progress, 2, 1)

        system_group.setLayout(system_layout)
        layout.addWidget(system_group)

        # NodeBox metrics
        nodebox_group = QGroupBox("NodeBox Metrics")
        nodebox_layout = QGridLayout()

        self.active_nodes_label = QLabel("Active Nodes: 0")
        nodebox_layout.addWidget(self.active_nodes_label, 0, 0)

        self.total_nodes_label = QLabel("Total Nodes: 0")
        nodebox_layout.addWidget(self.total_nodes_label, 0, 1)

        self.workflows_label = QLabel("Running Workflows: 0")
        nodebox_layout.addWidget(self.workflows_label, 1, 0)

        self.execution_time_label = QLabel("Avg Execution Time: 0.0s")
        nodebox_layout.addWidget(self.execution_time_label, 1, 1)

        self.error_count_label = QLabel("Errors: 0")
        nodebox_layout.addWidget(self.error_count_label, 2, 0)

        nodebox_group.setLayout(nodebox_layout)
        layout.addWidget(nodebox_group)

        # Performance history table
        history_group = QGroupBox("Performance History")
        history_layout = QVBoxLayout()

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels(
            ["Time", "CPU %", "Memory %", "Disk %", "Active Nodes", "Errors"]
        )
        history_layout.addWidget(self.history_table)

        history_group.setLayout(history_layout)
        layout.addWidget(history_group)

        self.setLayout(layout)

    def start_monitoring(self):
        """Start optimized performance monitoring"""
        self.monitoring = True
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_metrics)
        self.timer.start(self._update_interval)  # Configurable interval
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def _subscribe_bus(self):
        try:
            from utils.performance_bus import get_performance_bus

            bus = get_performance_bus()
            bus.metrics_signal.connect(self._on_app_metrics)
        except Exception:
            pass

    def _on_app_metrics(self, data: dict):
        try:
            self.update_nodebox_metrics(
                active_nodes=int(data.get("active_nodes", 0)),
                total_nodes=int(data.get("total_nodes", 0)),
                workflows_running=int(data.get("workflows_running", 0)),
                execution_time=float(data.get("execution_time", 0.0)),
                error_count=int(data.get("error_count", 0)),
            )
            self.update_ui()
            self.add_to_history()
        except Exception:
            pass

    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring = False
        if hasattr(self, "timer"):
            self.timer.stop()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def update_metrics(self):
        """Optimized metrics update"""
        if not self.monitoring:
            return

        try:
            # System metrics - optimized
            self.metrics.cpu_usage = psutil.cpu_percent(interval=None)  # Non-blocking
            memory = psutil.virtual_memory()
            self.metrics.memory_usage = memory.percent

            # Only update disk usage occasionally to reduce I/O
            if (
                not hasattr(self, "_disk_update_counter")
                or self._disk_update_counter % 5 == 0
            ):
                disk = psutil.disk_usage("/")
                self.metrics.disk_usage = (disk.used / disk.total) * 100
                self._disk_update_counter = 0
            self._disk_update_counter = getattr(self, "_disk_update_counter", 0) + 1

            # Network metrics
            current_network = psutil.net_io_counters()
            self.metrics.network_sent = (
                current_network.bytes_sent - self.network_baseline.bytes_sent
            )
            self.metrics.network_recv = (
                current_network.bytes_recv - self.network_baseline.bytes_recv
            )
            self.network_baseline = current_network

            self.metrics.timestamp = datetime.now()

            # Update UI
            self.update_ui()

            # Add to history
            self.add_to_history()

            # Emit signal
            self.metrics_updated.emit(self.metrics)
        except Exception:
            pass  # Silently handle psutil errors

    def update_ui(self):
        """Update the UI with current metrics"""
        # System metrics
        self.cpu_progress.setValue(int(self.metrics.cpu_usage))
        self.cpu_label.setText(f"CPU Usage: {self.metrics.cpu_usage:.1f}%")

        self.memory_progress.setValue(int(self.metrics.memory_usage))
        self.memory_label.setText(f"Memory Usage: {self.metrics.memory_usage:.1f}%")

        self.disk_progress.setValue(int(self.metrics.disk_usage))
        self.disk_label.setText(f"Disk Usage: {self.metrics.disk_usage:.1f}%")

        # NodeBox metrics
        self.active_nodes_label.setText(f"Active Nodes: {self.metrics.active_nodes}")
        self.total_nodes_label.setText(f"Total Nodes: {self.metrics.total_nodes}")
        self.workflows_label.setText(
            f"Running Workflows: {self.metrics.workflows_running}"
        )
        self.execution_time_label.setText(
            f"Avg Execution Time: {self.metrics.execution_time:.3f}s"
        )
        self.error_count_label.setText(f"Errors: {self.metrics.error_count}")

        # Color coding for progress bars
        self.update_progress_colors()

    def update_progress_colors(self):
        """Update progress bar colors based on usage levels"""
        # CPU
        if self.metrics.cpu_usage > 80:
            self.cpu_progress.setStyleSheet(
                "QProgressBar::chunk { background-color: #ff4444; }"
            )
        elif self.metrics.cpu_usage > 60:
            self.cpu_progress.setStyleSheet(
                "QProgressBar::chunk { background-color: #ffaa44; }"
            )
        else:
            self.cpu_progress.setStyleSheet(
                "QProgressBar::chunk { background-color: #44ff44; }"
            )

        # Memory
        if self.metrics.memory_usage > 80:
            self.memory_progress.setStyleSheet(
                "QProgressBar::chunk { background-color: #ff4444; }"
            )
        elif self.metrics.memory_usage > 60:
            self.memory_progress.setStyleSheet(
                "QProgressBar::chunk { background-color: #ffaa44; }"
            )
        else:
            self.memory_progress.setStyleSheet(
                "QProgressBar::chunk { background-color: #44ff44; }"
            )

        # Disk
        if self.metrics.disk_usage > 90:
            self.disk_progress.setStyleSheet(
                "QProgressBar::chunk { background-color: #ff4444; }"
            )
        elif self.metrics.disk_usage > 80:
            self.disk_progress.setStyleSheet(
                "QProgressBar::chunk { background-color: #ffaa44; }"
            )
        else:
            self.disk_progress.setStyleSheet(
                "QProgressBar::chunk { background-color: #44ff44; }"
            )

    def add_to_history(self):
        """Optimized history management"""
        self.history.append(
            {
                "timestamp": self.metrics.timestamp,
                "cpu": self.metrics.cpu_usage,
                "memory": self.metrics.memory_usage,
                "disk": self.metrics.disk_usage,
                "active_nodes": self.metrics.active_nodes,
                "errors": self.metrics.error_count,
            }
        )

        # Update history table only every 5 updates to reduce UI overhead
        if (
            not hasattr(self, "_history_update_counter")
            or self._history_update_counter % 5 == 0
        ):
            self.update_history_table()
            self._history_update_counter = 0
        self._history_update_counter = getattr(self, "_history_update_counter", 0) + 1

    def update_history_table(self):
        """Update the history table"""
        self.history_table.setRowCount(len(self.history))

        for i, entry in enumerate(self.history):
            self.history_table.setItem(
                i, 0, QTableWidgetItem(entry["timestamp"].strftime("%H:%M:%S"))
            )
            self.history_table.setItem(i, 1, QTableWidgetItem(f"{entry['cpu']:.1f}%"))
            self.history_table.setItem(
                i, 2, QTableWidgetItem(f"{entry['memory']:.1f}%")
            )
            self.history_table.setItem(i, 3, QTableWidgetItem(f"{entry['disk']:.1f}%"))
            self.history_table.setItem(
                i, 4, QTableWidgetItem(str(entry["active_nodes"]))
            )
            self.history_table.setItem(i, 5, QTableWidgetItem(str(entry["errors"])))

    def update_nodebox_metrics(
        self, active_nodes, total_nodes, workflows_running, execution_time, error_count
    ):
        """Update NodeBox specific metrics"""
        self.metrics.active_nodes = active_nodes
        self.metrics.total_nodes = total_nodes
        self.metrics.workflows_running = workflows_running
        self.metrics.execution_time = execution_time
        self.metrics.error_count = error_count

    def reset_metrics(self):
        """Optimized metrics reset"""
        self.history.clear()
        self.metrics = PerformanceMetrics()
        self.network_baseline = psutil.net_io_counters()
        self.update_ui()
        self.history_table.setRowCount(0)
        # Reset internal counters
        self._disk_update_counter = 0
        self._history_update_counter = 0

    def export_metrics(self, filename=None):
        """Export metrics to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"nodebox_metrics_{timestamp}.json"

        export_data = {
            "export_time": datetime.now().isoformat(),
            "current_metrics": {
                "cpu_usage": self.metrics.cpu_usage,
                "memory_usage": self.metrics.memory_usage,
                "disk_usage": self.metrics.disk_usage,
                "active_nodes": self.metrics.active_nodes,
                "total_nodes": self.metrics.total_nodes,
                "workflows_running": self.metrics.workflows_running,
                "execution_time": self.metrics.execution_time,
                "error_count": self.metrics.error_count,
            },
            "history": [
                {
                    "timestamp": entry["timestamp"].isoformat(),
                    "cpu": entry["cpu"],
                    "memory": entry["memory"],
                    "disk": entry["disk"],
                    "active_nodes": entry["active_nodes"],
                    "errors": entry["errors"],
                }
                for entry in self.history
            ],
        }

        with open(filename, "w") as f:
            json.dump(export_data, f, indent=2)

        return filename
