"""
Optimized Debug Console - Efficient logging and monitoring
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QTextEdit, QComboBox, QSplitter, QTableWidget, QTableWidgetItem, 
                             QHeaderView)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QTextCharFormat, QColor, QTextCursor
import json
import datetime
from collections import deque

class LogEntry:
    __slots__ = ['timestamp', 'level', 'message', 'node_id', 'node_name']
    
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
        self._update_timer = QTimer()
        self._update_timer.timeout.connect(self.update_metrics)
        self._update_timer.start(5000)  # Update metrics every 5 seconds
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Minimalist title
        title = QLabel("Debug Console")
        title.setFont(QFont("Poppins", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Compact controls
        controls_layout = QHBoxLayout()
        
        self.level_combo = QComboBox()
        self.level_combo.addItems(["All", "ERROR", "WARNING", "INFO", "DEBUG"])
        self.level_combo.currentTextChanged.connect(self.filter_logs)
        controls_layout.addWidget(QLabel("Level:"))
        controls_layout.addWidget(self.level_combo)
        
        self.node_combo = QComboBox()
        self.node_combo.addItem("All")
        self.node_combo.currentTextChanged.connect(self.filter_logs)
        controls_layout.addWidget(QLabel("Node:"))
        controls_layout.addWidget(self.node_combo)
        
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.clear_logs)
        clear_button.setStyleSheet("QPushButton { padding: 4px 8px; }")
        controls_layout.addWidget(clear_button)
        
        export_button = QPushButton("Export")
        export_button.clicked.connect(self.export_logs)
        export_button.setStyleSheet("QPushButton { padding: 4px 8px; }")
        controls_layout.addWidget(export_button)
        
        layout.addLayout(controls_layout)
        
        # Main content area
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QFont("Consolas", 10))
        splitter.addWidget(self.log_display)
        
        # Performance metrics
        self.metrics_widget = self.create_metrics_widget()
        splitter.addWidget(self.metrics_widget)
        
        splitter.setSizes([800, 400])
        layout.addWidget(splitter)
        
        self.setLayout(layout)
    
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
        self.metrics_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.metrics_table)
        
        # Update metrics
        self.update_metrics()
        
        widget.setLayout(layout)
        return widget
    
    def setup_logging(self):
        """Setup logging capture"""
        # This would integrate with Python's logging module
        pass
    
    def add_log(self, level, message, node_id=None, node_name=None):
        """Optimized log entry addition"""
        log_entry = LogEntry(datetime.datetime.now(), level, message, node_id, node_name)
        
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
            log for log in self.logs
            if (level_filter == "All" or log.level == level_filter) and
               (node_filter == "All" or log.node_name == node_filter)
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
                    "node_name": log.node_name
                }
                for log in self.logs
            ]
            
            with open(filename, "w") as f:
                json.dump(logs_data, f, separators=(',', ':'))  # Compact JSON
            
            self.add_log("INFO", f"Logs exported to {filename}")
        except Exception as e:
            self.add_log("ERROR", f"Export failed: {str(e)}")
    
    def update_metrics(self):
        """Update performance metrics"""
        self.metrics_table.setRowCount(0)
        
        # Calculate metrics
        total_logs = len(self.logs)
        error_count = len([log for log in self.logs if log.level == "ERROR"])
        warning_count = len([log for log in self.logs if log.level == "WARNING"])
        
        # Add metrics to table
        metrics = [
            ("Total Logs", str(total_logs)),
            ("Errors", str(error_count)),
            ("Warnings", str(warning_count)),
            ("Error Rate", f"{(error_count/total_logs*100):.1f}%" if total_logs > 0 else "0%"),
            ("Last Update", datetime.datetime.now().strftime("%H:%M:%S"))
        ]
        
        self.metrics_table.setRowCount(len(metrics))
        for i, (metric, value) in enumerate(metrics):
            self.metrics_table.setItem(i, 0, QTableWidgetItem(metric))
            self.metrics_table.setItem(i, 1, QTableWidgetItem(value))
    
    def log_node_execution(self, node_name, success, execution_time, error=None):
        """Log node execution details"""
        if success:
            self.add_log("INFO", f"Node '{node_name}' executed successfully in {execution_time:.3f}s", node_name=node_name)
        else:
            self.add_log("ERROR", f"Node '{node_name}' failed: {error}", node_name=node_name)
    
    def log_workflow_start(self, workflow_name):
        """Log workflow start"""
        self.add_log("INFO", f"Starting workflow: {workflow_name}")
    
    def log_workflow_end(self, workflow_name, success, total_time):
        """Log workflow completion"""
        if success:
            self.add_log("INFO", f"Workflow '{workflow_name}' completed successfully in {total_time:.3f}s")
        else:
            self.add_log("ERROR", f"Workflow '{workflow_name}' failed after {total_time:.3f}s")
