"""
Workflow Scheduler - Built-in scheduling for automations
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QTableWidget, QTableWidgetItem, QDateTimeEdit, QComboBox,
                             QLineEdit, QCheckBox, QMessageBox, QDialog, QFormLayout)
from PyQt6.QtCore import Qt, QTimer, QDateTime, pyqtSignal
from PyQt6.QtGui import QFont
import json
import os
from datetime import datetime, timedelta

class ScheduleItem:
    def __init__(self, name, automation_name, schedule_type, schedule_value, enabled=True):
        self.name = name
        self.automation_name = automation_name
        self.schedule_type = schedule_type  # "once", "interval", "cron"
        self.schedule_value = schedule_value
        self.enabled = enabled
        self.last_run = None
        self.next_run = None
        self.run_count = 0

class WorkflowScheduler(QWidget):
    schedule_triggered = pyqtSignal(str)  # Emits automation name when scheduled
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.schedules = []
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_schedules)
        self.timer.start(60000)  # Check every minute
        self.init_ui()
        self.load_schedules()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Workflow Scheduler")
        title.setFont(QFont("Poppins", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Add schedule button
        add_button = QPushButton("Add Schedule")
        add_button.clicked.connect(self.add_schedule_dialog)
        layout.addWidget(add_button)
        
        # Schedules table
        self.schedules_table = QTableWidget()
        self.schedules_table.setColumnCount(6)
        self.schedules_table.setHorizontalHeaderLabels([
            "Name", "Automation", "Type", "Schedule", "Status", "Next Run"
        ])
        layout.addWidget(self.schedules_table)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.toggle_button = QPushButton("Toggle Selected")
        self.toggle_button.clicked.connect(self.toggle_selected)
        button_layout.addWidget(self.toggle_button)
        
        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.clicked.connect(self.delete_selected)
        button_layout.addWidget(self.delete_button)
        
        self.run_now_button = QPushButton("Run Now")
        self.run_now_button.clicked.connect(self.run_selected_now)
        button_layout.addWidget(self.run_now_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def add_schedule_dialog(self):
        dialog = ScheduleDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            schedule = dialog.get_schedule()
            self.add_schedule(schedule)
    
    def add_schedule(self, schedule):
        self.schedules.append(schedule)
        self.update_table()
        self.save_schedules()
    
    def update_table(self):
        self.schedules_table.setRowCount(len(self.schedules))
        
        for i, schedule in enumerate(self.schedules):
            self.schedules_table.setItem(i, 0, QTableWidgetItem(schedule.name))
            self.schedules_table.setItem(i, 1, QTableWidgetItem(schedule.automation_name))
            self.schedules_table.setItem(i, 2, QTableWidgetItem(schedule.schedule_type))
            self.schedules_table.setItem(i, 3, QTableWidgetItem(str(schedule.schedule_value)))
            self.schedules_table.setItem(i, 4, QTableWidgetItem("Enabled" if schedule.enabled else "Disabled"))
            self.schedules_table.setItem(i, 5, QTableWidgetItem(
                schedule.next_run.strftime("%Y-%m-%d %H:%M") if schedule.next_run else "Not scheduled"
            ))
    
    def check_schedules(self):
        """Check if any schedules need to run"""
        now = datetime.now()
        
        for schedule in self.schedules:
            if not schedule.enabled:
                continue
                
            if schedule.next_run and now >= schedule.next_run:
                self.schedule_triggered.emit(schedule.automation_name)
                schedule.last_run = now
                schedule.run_count += 1
                self.update_next_run(schedule)
        
        self.update_table()
    
    def update_next_run(self, schedule):
        """Update the next run time for a schedule"""
        now = datetime.now()
        
        if schedule.schedule_type == "interval":
            # Schedule for next interval
            interval_minutes = int(schedule.schedule_value)
            schedule.next_run = now + timedelta(minutes=interval_minutes)
        elif schedule.schedule_type == "once":
            # One-time schedule, disable after run
            schedule.enabled = False
            schedule.next_run = None
        # Cron scheduling would be more complex to implement
    
    def toggle_selected(self):
        """Toggle enabled status of selected schedule"""
        current_row = self.schedules_table.currentRow()
        if current_row >= 0:
            self.schedules[current_row].enabled = not self.schedules[current_row].enabled
            self.update_table()
            self.save_schedules()
    
    def delete_selected(self):
        """Delete selected schedule"""
        current_row = self.schedules_table.currentRow()
        if current_row >= 0:
            del self.schedules[current_row]
            self.update_table()
            self.save_schedules()
    
    def run_selected_now(self):
        """Run selected automation immediately"""
        current_row = self.schedules_table.currentRow()
        if current_row >= 0:
            automation_name = self.schedules[current_row].automation_name
            self.schedule_triggered.emit(automation_name)
    
    def save_schedules(self):
        """Save schedules to file"""
        schedules_data = []
        for schedule in self.schedules:
            schedules_data.append({
                "name": schedule.name,
                "automation_name": schedule.automation_name,
                "schedule_type": schedule.schedule_type,
                "schedule_value": schedule.schedule_value,
                "enabled": schedule.enabled,
                "last_run": schedule.last_run.isoformat() if schedule.last_run else None,
                "next_run": schedule.next_run.isoformat() if schedule.next_run else None,
                "run_count": schedule.run_count
            })
        
        os.makedirs("data", exist_ok=True)
        with open("data/schedules.json", "w") as f:
            json.dump(schedules_data, f, indent=2)
    
    def load_schedules(self):
        """Load schedules from file"""
        try:
            with open("data/schedules.json", "r") as f:
                schedules_data = json.load(f)
            
            self.schedules = []
            for data in schedules_data:
                schedule = ScheduleItem(
                    data["name"],
                    data["automation_name"],
                    data["schedule_type"],
                    data["schedule_value"],
                    data["enabled"]
                )
                schedule.last_run = datetime.fromisoformat(data["last_run"]) if data["last_run"] else None
                schedule.next_run = datetime.fromisoformat(data["next_run"]) if data["next_run"] else None
                schedule.run_count = data.get("run_count", 0)
                self.schedules.append(schedule)
            
            self.update_table()
        except FileNotFoundError:
            pass  # No schedules file yet

class ScheduleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Schedule")
        self.setModal(True)
        self.init_ui()
    
    def init_ui(self):
        layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        layout.addRow("Schedule Name:", self.name_edit)
        
        self.automation_edit = QLineEdit()
        layout.addRow("Automation Name:", self.automation_edit)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["once", "interval", "cron"])
        layout.addRow("Schedule Type:", self.type_combo)
        
        self.value_edit = QLineEdit()
        self.value_edit.setPlaceholderText("For interval: minutes, for cron: cron expression")
        layout.addRow("Schedule Value:", self.value_edit)
        
        self.enabled_check = QCheckBox("Enabled")
        self.enabled_check.setChecked(True)
        layout.addRow("", self.enabled_check)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addRow(button_layout)
        self.setLayout(layout)
    
    def get_schedule(self):
        """Get the schedule from the dialog"""
        return ScheduleItem(
            self.name_edit.text(),
            self.automation_edit.text(),
            self.type_combo.currentText(),
            self.value_edit.text(),
            self.enabled_check.isChecked()
        )
