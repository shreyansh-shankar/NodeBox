"""
Enhanced Debug Console - Better debugging and logging for NodeBox
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QTextEdit, QComboBox, QCheckBox, QSplitter, QTabWidget,
                             QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QTextCharFormat, QColor, QTextCursor
import json
import datetime
import traceback
import sys
from io import StringIO

class LogEntry:
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
        self.logs = []
        self.max_logs = 1000
        self.init_ui()
        self.setup_logging()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Debug Console")
        title.setFont(QFont("Poppins", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        # Log level filter
        self.level_combo = QComboBox()
        self.level_combo.addItems(["All", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.level_combo.currentTextChanged.connect(self.filter_logs)
        controls_layout.addWidget(QLabel("Level:"))
        controls_layout.addWidget(self.level_combo)
        
        # Node filter
        self.node_combo = QComboBox()
        self.node_combo.addItem("All Nodes")
        self.node_combo.currentTextChanged.connect(self.filter_logs)
        controls_layout.addWidget(QLabel("Node:"))
        controls_layout.addWidget(self.node_combo)
        
        # Clear button
        clear_button = QPushButton("Clear Logs")
        clear_button.clicked.connect(self.clear_logs)
        controls_layout.addWidget(clear_button)
        
        # Export button
        export_button = QPushButton("Export Logs")
        export_button.clicked.connect(self.export_logs)
        controls_layout.addWidget(export_button)
        
        controls_layout.addStretch()
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
        """Add a log entry"""
        timestamp = datetime.datetime.now()
        log_entry = LogEntry(timestamp, level, message, node_id, node_name)
        
        self.logs.append(log_entry)
        
        # Keep only the last max_logs entries
        if len(self.logs) > self.max_logs:
            self.logs = self.logs[-self.max_logs:]
        
        # Update node combo if new node
        if node_name and node_name not in [self.node_combo.itemText(i) for i in range(self.node_combo.count())]:
            self.node_combo.addItem(node_name)
        
        self.log_added.emit(log_entry)
        self.update_log_display()
    
    def update_log_display(self):
        """Update the log display with filtered logs"""
        self.log_display.clear()
        
        level_filter = self.level_combo.currentText()
        node_filter = self.node_combo.currentText()
        
        filtered_logs = []
        for log in self.logs:
            if level_filter != "All" and log.level != level_filter:
                continue
            if node_filter != "All Nodes" and log.node_name != node_filter:
                continue
            filtered_logs.append(log)
        
        for log in filtered_logs:
            self.append_log_to_display(log)
    
    def append_log_to_display(self, log):
        """Append a single log entry to the display"""
        cursor = self.log_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        # Format based on log level
        format = QTextCharFormat()
        if log.level == "ERROR" or log.level == "CRITICAL":
            format.setForeground(QColor(255, 100, 100))
        elif log.level == "WARNING":
            format.setForeground(QColor(255, 200, 100))
        elif log.level == "INFO":
            format.setForeground(QColor(100, 200, 255))
        else:
            format.setForeground(QColor(200, 200, 200))
        
        cursor.setCharFormat(format)
        
        # Format the log entry
        timestamp_str = log.timestamp.strftime("%H:%M:%S.%f")[:-3]
        node_info = f" [{log.node_name}]" if log.node_name else ""
        log_text = f"[{timestamp_str}] {log.level}{node_info}: {log.message}\n"
        
        cursor.insertText(log_text)
        self.log_display.setTextCursor(cursor)
        self.log_display.ensureCursorVisible()
    
    def filter_logs(self):
        """Filter logs based on current filters"""
        self.update_log_display()
    
    def clear_logs(self):
        """Clear all logs"""
        self.logs.clear()
        self.log_display.clear()
        self.update_metrics()
    
    def export_logs(self):
        """Export logs to file"""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"nodebox_logs_{timestamp}.json"
            
            logs_data = []
            for log in self.logs:
                logs_data.append({
                    "timestamp": log.timestamp.isoformat(),
                    "level": log.level,
                    "message": log.message,
                    "node_id": log.node_id,
                    "node_name": log.node_name
                })
            
            with open(filename, "w") as f:
                json.dump(logs_data, f, indent=2)
            
            self.add_log("INFO", f"Logs exported to {filename}")
        except Exception as e:
            self.add_log("ERROR", f"Failed to export logs: {str(e)}")
    
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
