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

from nodebox.core.bus import get_performance_bus


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
        self.history = deque(maxlen=50)
        self.monitoring = True
        self._update_interval = 2000

        self.network_baseline = psutil.net_io_counters()

        self.init_ui()
        self._subscribe_bus()
        self.start_monitoring()

    def init_ui(self):
        self.setStyleSheet("background-color: #252526;")

        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Performance Monitor")
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #ffffff; margin-bottom: 8px;")
        layout.addWidget(title)

        subtitle = QLabel("System and NodeBox Performance Metrics")
        subtitle.setFont(QFont("Segoe UI", 13))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #a0a0a0; margin-bottom: 16px;")
        layout.addWidget(subtitle)

        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(12)

        self.start_button = QPushButton("  Start Monitoring")
        self.start_button.clicked.connect(self.start_monitoring)
        self.start_button.setFont(QFont("Segoe UI", 12))
        self.start_button.setMinimumHeight(44)
        self.start_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_button.setStyleSheet(
            """
            QPushButton {
                padding: 12px 24px;
                background-color: #0e639c;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:pressed {
                background-color: #0d5a8f;
            }
            QPushButton:disabled {
                background-color: #3e3e42;
                color: #888888;
            }
        """
        )
        controls_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("  Stop Monitoring")
        self.stop_button.clicked.connect(self.stop_monitoring)
        self.stop_button.setFont(QFont("Segoe UI", 12))
        self.stop_button.setMinimumHeight(44)
        self.stop_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.stop_button.setStyleSheet(
            """
            QPushButton {
                padding: 12px 24px;
                background-color: #a74444;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #c55555;
            }
            QPushButton:pressed {
                background-color: #943a3a;
            }
            QPushButton:disabled {
                background-color: #3e3e42;
                color: #888888;
            }
        """
        )
        controls_layout.addWidget(self.stop_button)

        self.reset_button = QPushButton("  Reset Data")
        self.reset_button.clicked.connect(self.reset_metrics)
        self.reset_button.setFont(QFont("Segoe UI", 12))
        self.reset_button.setMinimumHeight(44)
        self.reset_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.reset_button.setStyleSheet(
            """
            QPushButton {
                padding: 12px 24px;
                background-color: #0d7d3a;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #0f9d4a;
            }
            QPushButton:pressed {
                background-color: #0b6d32;
            }
        """
        )
        controls_layout.addWidget(self.reset_button)

        layout.addLayout(controls_layout)

        system_group = QGroupBox("System Metrics")
        system_group.setFont(QFont("Segoe UI", 14, QFont.Weight.DemiBold))
        system_group.setStyleSheet(
            """
            QGroupBox {
                font-weight: bold;
                border: 1px solid #3e3e42;
                border-radius: 6px;
                padding: 16px;
                margin-top: 12px;
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
                color: #ffffff;
            }
        """
        )
        system_layout = QGridLayout()
        system_layout.setSpacing(12)
        system_layout.setContentsMargins(16, 20, 16, 16)

        self.cpu_label = QLabel("CPU Usage:")
        self.cpu_label.setFont(QFont("Segoe UI", 12))
        self.cpu_label.setStyleSheet("color: #e0e0e0;")
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setRange(0, 100)
        self.cpu_progress.setMinimumHeight(24)
        self.cpu_progress.setStyleSheet(
            """
            QProgressBar {
                border: 1px solid #3e3e42;
                border-radius: 4px;
                text-align: center;
                background-color: #2d2d30;
                color: #ffffff;
                font-weight: 600;
            }
            QProgressBar::chunk {
                background-color: #44ff44;
                border-radius: 3px;
            }
        """
        )
        system_layout.addWidget(self.cpu_label, 0, 0)
        system_layout.addWidget(self.cpu_progress, 0, 1)

        self.memory_label = QLabel("Memory Usage:")
        self.memory_label.setFont(QFont("Segoe UI", 12))
        self.memory_label.setStyleSheet("color: #e0e0e0;")
        self.memory_progress = QProgressBar()
        self.memory_progress.setRange(0, 100)
        self.memory_progress.setMinimumHeight(24)
        self.memory_progress.setStyleSheet(
            """
            QProgressBar {
                border: 1px solid #3e3e42;
                border-radius: 4px;
                text-align: center;
                background-color: #2d2d30;
                color: #ffffff;
                font-weight: 600;
            }
            QProgressBar::chunk {
                background-color: #44ff44;
                border-radius: 3px;
            }
        """
        )
        system_layout.addWidget(self.memory_label, 1, 0)
        system_layout.addWidget(self.memory_progress, 1, 1)

        self.disk_label = QLabel("Disk Usage:")
        self.disk_label.setFont(QFont("Segoe UI", 12))
        self.disk_label.setStyleSheet("color: #e0e0e0;")
        self.disk_progress = QProgressBar()
        self.disk_progress.setRange(0, 100)
        self.disk_progress.setMinimumHeight(24)
        self.disk_progress.setStyleSheet(
            """
            QProgressBar {
                border: 1px solid #3e3e42;
                border-radius: 4px;
                text-align: center;
                background-color: #2d2d30;
                color: #ffffff;
                font-weight: 600;
            }
            QProgressBar::chunk {
                background-color: #44ff44;
                border-radius: 3px;
            }
        """
        )
        system_layout.addWidget(self.disk_label, 2, 0)
        system_layout.addWidget(self.disk_progress, 2, 1)

        system_group.setLayout(system_layout)
        layout.addWidget(system_group)

        nodebox_group = QGroupBox("NodeBox Metrics")
        nodebox_group.setFont(QFont("Segoe UI", 14, QFont.Weight.DemiBold))
        nodebox_group.setStyleSheet(
            """
            QGroupBox {
                font-weight: bold;
                border: 1px solid #3e3e42;
                border-radius: 6px;
                padding: 16px;
                margin-top: 12px;
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
                color: #ffffff;
            }
        """
        )
        nodebox_layout = QGridLayout()
        nodebox_layout.setSpacing(12)
        nodebox_layout.setContentsMargins(16, 20, 16, 16)

        self.active_nodes_label = QLabel("Active Nodes: 0")
        self.active_nodes_label.setFont(QFont("Segoe UI", 12))
        self.active_nodes_label.setStyleSheet("color: #e0e0e0; padding: 8px;")
        nodebox_layout.addWidget(self.active_nodes_label, 0, 0)

        self.total_nodes_label = QLabel("Total Nodes: 0")
        self.total_nodes_label.setFont(QFont("Segoe UI", 12))
        self.total_nodes_label.setStyleSheet("color: #e0e0e0; padding: 8px;")
        nodebox_layout.addWidget(self.total_nodes_label, 0, 1)

        self.workflows_label = QLabel("Running Workflows: 0")
        self.workflows_label.setFont(QFont("Segoe UI", 12))
        self.workflows_label.setStyleSheet("color: #e0e0e0; padding: 8px;")
        nodebox_layout.addWidget(self.workflows_label, 1, 0)

        self.execution_time_label = QLabel("Avg Execution Time: 0.0s")
        self.execution_time_label.setFont(QFont("Segoe UI", 12))
        self.execution_time_label.setStyleSheet("color: #e0e0e0; padding: 8px;")
        nodebox_layout.addWidget(self.execution_time_label, 1, 1)

        self.error_count_label = QLabel("Errors: 0")
        self.error_count_label.setFont(QFont("Segoe UI", 12))
        self.error_count_label.setStyleSheet("color: #e0e0e0; padding: 8px;")
        nodebox_layout.addWidget(self.error_count_label, 2, 0)

        nodebox_group.setLayout(nodebox_layout)
        layout.addWidget(nodebox_group)

        history_group = QGroupBox("Performance History")
        history_group.setFont(QFont("Segoe UI", 14, QFont.Weight.DemiBold))
        history_group.setStyleSheet(
            """
            QGroupBox {
                font-weight: bold;
                border: 1px solid #3e3e42;
                border-radius: 6px;
                padding: 16px;
                margin-top: 12px;
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
                color: #ffffff;
            }
        """
        )
        history_layout = QVBoxLayout()
        history_layout.setContentsMargins(16, 20, 16, 16)

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels(
            ["Time", "CPU %", "Memory %", "Disk %", "Active Nodes", "Errors"]
        )
        self.history_table.setFont(QFont("Segoe UI", 11))
        self.history_table.setMinimumHeight(300)
        self.history_table.setAlternatingRowColors(True)
        self.history_table.horizontalHeader().setStretchLastSection(True)
        self.history_table.setStyleSheet(
            """
            QTableWidget {
                border: 1px solid #3e3e42;
                border-radius: 6px;
                background-color: #2d2d30;
                color: #e0e0e0;
                gridline-color: #3e3e42;
                selection-background-color: #0e639c;
                alternate-background-color: #252526;
            }
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #3e3e42;
                min-height: 20px;
            }
            QTableWidget::item:selected {
                background-color: #0e639c;
                color: #ffffff;
            }
            QHeaderView::section {
                background-color: #2d2d30;
                color: #ffffff;
                padding: 10px;
                border: 1px solid #3e3e42;
                font-weight: 600;
                min-height: 25px;
            }
        """
        )
        history_layout.addWidget(self.history_table)

        history_group.setLayout(history_layout)
        layout.addWidget(history_group, 1)

        self.setLayout(layout)

    def start_monitoring(self):
        self.monitoring = True
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_metrics)
        self.timer.start(self._update_interval)
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def _subscribe_bus(self):
        try:
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
        self.monitoring = False
        if hasattr(self, "timer"):
            self.timer.stop()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def update_metrics(self):
        if not self.monitoring:
            return

        try:
            self.metrics.cpu_usage = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            self.metrics.memory_usage = memory.percent

            if (
                not hasattr(self, "_disk_update_counter")
                or self._disk_update_counter % 5 == 0
            ):
                disk = psutil.disk_usage("/")
                self.metrics.disk_usage = (disk.used / disk.total) * 100
                self._disk_update_counter = 0
            self._disk_update_counter = getattr(self, "_disk_update_counter", 0) + 1

            current_network = psutil.net_io_counters()
            self.metrics.network_sent = (
                current_network.bytes_sent - self.network_baseline.bytes_sent
            )
            self.metrics.network_recv = (
                current_network.bytes_recv - self.network_baseline.bytes_recv
            )
            self.network_baseline = current_network

            self.metrics.timestamp = datetime.now()

            self.update_ui()
            self.add_to_history()
            self.metrics_updated.emit(self.metrics)
        except Exception:
            pass

    def update_ui(self):
        self.cpu_progress.setValue(int(self.metrics.cpu_usage))
        self.cpu_label.setText(f"CPU Usage: {self.metrics.cpu_usage:.1f}%")

        self.memory_progress.setValue(int(self.metrics.memory_usage))
        self.memory_label.setText(f"Memory Usage: {self.metrics.memory_usage:.1f}%")

        self.disk_progress.setValue(int(self.metrics.disk_usage))
        self.disk_label.setText(f"Disk Usage: {self.metrics.disk_usage:.1f}%")

        self.active_nodes_label.setText(f"Active Nodes: {self.metrics.active_nodes}")
        self.total_nodes_label.setText(f"Total Nodes: {self.metrics.total_nodes}")
        self.workflows_label.setText(
            f"Running Workflows: {self.metrics.workflows_running}"
        )
        self.execution_time_label.setText(
            f"Avg Execution Time: {self.metrics.execution_time:.3f}s"
        )
        self.error_count_label.setText(f"Errors: {self.metrics.error_count}")

        self.update_progress_colors()

    def update_progress_colors(self):
        color = "#44ff44"
        if self.metrics.cpu_usage > 80:
            color = "#ff4444"
        elif self.metrics.cpu_usage > 60:
            color = "#ffaa44"

        style = f"""
            QProgressBar {{
                border: 1px solid #3e3e42;
                border-radius: 4px;
                text-align: center;
                background-color: #2d2d30;
                color: #ffffff;
                font-weight: 600;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 3px;
            }}
        """
        self.cpu_progress.setStyleSheet(style)

    def add_to_history(self):
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

        if (
            not hasattr(self, "_history_update_counter")
            or self._history_update_counter % 5 == 0
        ):
            self.update_history_table()
            self._history_update_counter = 0
        self._history_update_counter = getattr(self, "_history_update_counter", 0) + 1

    def update_history_table(self):
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

        self.history_table.resizeColumnsToContents()
        for col in range(self.history_table.columnCount()):
            if self.history_table.columnWidth(col) < 80:
                self.history_table.setColumnWidth(col, 80)
        self.history_table.scrollToBottom()

    def update_nodebox_metrics(
        self, active_nodes, total_nodes, workflows_running, execution_time, error_count
    ):
        self.metrics.active_nodes = active_nodes
        self.metrics.total_nodes = total_nodes
        self.metrics.workflows_running = workflows_running
        self.metrics.execution_time = execution_time
        self.metrics.error_count = error_count

    def reset_metrics(self):
        self.history.clear()
        self.metrics = PerformanceMetrics()
        self.network_baseline = psutil.net_io_counters()
        self.update_ui()
        self.history_table.setRowCount(0)
        self._disk_update_counter = 0
        self._history_update_counter = 0

    def export_metrics(self, filename=None):
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


__all__ = ["PerformanceMetrics", "PerformanceMonitor"]
