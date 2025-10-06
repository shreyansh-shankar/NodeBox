"""
Workflow Scheduler - Professional UI matching Home tab design
"""

import json
import os
from datetime import datetime, timedelta

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateTimeEdit,
    QDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from utils.paths import resource_path


class ScheduleItem:
    __slots__ = [
        "name",
        "automation_name",
        "schedule_type",
        "schedule_value",
        "enabled",
        "last_run",
        "next_run",
        "run_count",
    ]

    def __init__(
        self, name, automation_name, schedule_type, schedule_value, enabled=True
    ):
        self.name = name
        self.automation_name = automation_name
        self.schedule_type = schedule_type  # "once", "interval", "daily"
        self.schedule_value = schedule_value
        self.enabled = enabled
        self.last_run = None
        self.next_run = None
        self.run_count = 0


class WorkflowScheduler(QWidget):
    schedule_triggered = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.schedules = []
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_schedules)
        self.timer.start(30000)  # Check every 30 seconds
        self._schedules_file = "data/schedules.json"
        self.init_ui()
        self.load_schedules()

    def get_icon(self, icon_name):
        """Get white icon from assets"""
        icon_path = resource_path(f"assets/icons/{icon_name}.svg")
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        return QIcon()

    def init_ui(self):
        """Setup the UI with modern styling matching Home tab"""
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        # Title section
        title = QLabel("Workflow Scheduler")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #ffffff;")
        main_layout.addWidget(title)

        subtitle = QLabel("Schedule automations to run at specific times")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet("color: #a0a0a0; margin-bottom: 10px;")
        main_layout.addWidget(subtitle)

        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(
            """
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #2d2d30;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #3e3e42;
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #4e4e52;
            }
        """
        )

        # Container for scrollable content
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setSpacing(20)

        # Action buttons row
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(12)

        add_button = QPushButton("  Add Schedule")
        add_button.setIcon(self.get_icon("plus-circle"))
        add_button.setFont(QFont("Segoe UI", 11))
        add_button.setMinimumHeight(40)
        add_button.setCursor(Qt.CursorShape.PointingHandCursor)
        add_button.setStyleSheet(
            """
            QPushButton {
                padding: 10px 20px;
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
        """
        )
        add_button.clicked.connect(self.add_schedule_dialog)
        actions_layout.addWidget(add_button)

        self.run_now_button = QPushButton("  Run Now")
        self.run_now_button.setIcon(self.get_icon("activity"))
        self.run_now_button.setFont(QFont("Segoe UI", 11))
        self.run_now_button.setMinimumHeight(40)
        self.run_now_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.run_now_button.setStyleSheet(
            """
            QPushButton {
                padding: 10px 20px;
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
        self.run_now_button.clicked.connect(self.run_selected_now)
        actions_layout.addWidget(self.run_now_button)

        self.toggle_button = QPushButton("  Toggle")
        self.toggle_button.setIcon(self.get_icon("clock"))
        self.toggle_button.setFont(QFont("Segoe UI", 11))
        self.toggle_button.setMinimumHeight(40)
        self.toggle_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_button.setStyleSheet(
            """
            QPushButton {
                padding: 10px 20px;
                background-color: #856404;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #a57a05;
            }
            QPushButton:pressed {
                background-color: #6d5203;
            }
        """
        )
        self.toggle_button.clicked.connect(self.toggle_selected)
        actions_layout.addWidget(self.toggle_button)

        self.delete_button = QPushButton("  Delete")
        self.delete_button.setIcon(self.get_icon("x"))
        self.delete_button.setFont(QFont("Segoe UI", 11))
        self.delete_button.setMinimumHeight(40)
        self.delete_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_button.setStyleSheet(
            """
            QPushButton {
                padding: 10px 20px;
                background-color: #a82828;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #c93636;
            }
            QPushButton:pressed {
                background-color: #8e2020;
            }
        """
        )
        self.delete_button.clicked.connect(self.delete_selected)
        actions_layout.addWidget(self.delete_button)

        actions_layout.addStretch()

        content_layout.addLayout(actions_layout)

        # Scheduled tasks section
        tasks_label = QLabel("Scheduled Tasks")
        tasks_label.setFont(QFont("Segoe UI", 14, QFont.Weight.DemiBold))
        tasks_label.setStyleSheet("color: #ffffff; margin-top: 8px;")
        content_layout.addWidget(tasks_label)

        # Tasks table
        self.schedules_table = QTableWidget()
        self.schedules_table.setColumnCount(6)
        self.schedules_table.setHorizontalHeaderLabels(
            ["Name", "Automation", "Type", "Status", "Next Run", "Runs"]
        )
        self.schedules_table.setFont(QFont("Segoe UI", 10))
        self.schedules_table.setAlternatingRowColors(True)
        self.schedules_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.schedules_table.setStyleSheet(
            """
            QTableWidget {
                border: 1px solid #3e3e42;
                border-radius: 6px;
                background-color: #1e1e1e;
                gridline-color: #2d2d30;
            }
            QTableWidget::item {
                padding: 8px;
                color: #e0e0e0;
            }
            QTableWidget::item:selected {
                background-color: #0e639c;
                color: #ffffff;
            }
            QTableWidget::item:alternate {
                background-color: #252526;
            }
            QHeaderView::section {
                background-color: #2d2d30;
                color: #ffffff;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #3e3e42;
                font-weight: 600;
            }
        """
        )
        self.schedules_table.setMinimumHeight(300)
        self.schedules_table.horizontalHeader().setStretchLastSection(True)
        content_layout.addWidget(self.schedules_table)

        # Add stretch to push content to top
        content_layout.addStretch()

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        self.setLayout(main_layout)
        self.setStyleSheet("QWidget { background-color: #252526; }")

    def add_schedule_dialog(self):
        dialog = ScheduleDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            schedule = dialog.get_schedule()
            self.add_schedule(schedule)

    def add_schedule(self, schedule):
        self.schedules.append(schedule)
        self.update_next_run(schedule)
        self.update_table()
        self.save_schedules()

    def update_table(self):
        """Optimized table update with professional styling"""
        self.schedules_table.setRowCount(len(self.schedules))

        for i, schedule in enumerate(self.schedules):
            # Name
            name_item = QTableWidgetItem(schedule.name)
            name_item.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
            self.schedules_table.setItem(i, 0, name_item)

            # Automation
            self.schedules_table.setItem(
                i, 1, QTableWidgetItem(schedule.automation_name)
            )

            # Type
            type_item = QTableWidgetItem(schedule.schedule_type.capitalize())
            self.schedules_table.setItem(i, 2, type_item)

            # Status
            status_text = "🟢 Enabled" if schedule.enabled else "🔴 Disabled"
            status_item = QTableWidgetItem(status_text)
            self.schedules_table.setItem(i, 3, status_item)

            # Next Run
            next_run_text = (
                schedule.next_run.strftime("%Y-%m-%d %H:%M")
                if schedule.next_run
                else "Not scheduled"
            )
            self.schedules_table.setItem(i, 4, QTableWidgetItem(next_run_text))

            # Run Count
            self.schedules_table.setItem(
                i, 5, QTableWidgetItem(str(schedule.run_count))
            )

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
        self.save_schedules()

    def update_next_run(self, schedule):
        """Update the next run time for a schedule"""
        now = datetime.now()

        if schedule.schedule_type == "interval":
            # Schedule for next interval
            interval_minutes = int(schedule.schedule_value)
            schedule.next_run = now + timedelta(minutes=interval_minutes)
        elif schedule.schedule_type == "daily":
            # Schedule for next day at same time
            schedule.next_run = now + timedelta(days=1)
        elif schedule.schedule_type == "once":
            # One-time schedule, disable after run
            schedule.enabled = False
            schedule.next_run = None

    def toggle_selected(self):
        """Toggle enabled status of selected schedule"""
        current_row = self.schedules_table.currentRow()
        if current_row >= 0:
            self.schedules[current_row].enabled = not self.schedules[
                current_row
            ].enabled
            if self.schedules[current_row].enabled:
                self.update_next_run(self.schedules[current_row])
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
            self.schedules[current_row].last_run = datetime.now()
            self.schedules[current_row].run_count += 1
            self.update_table()
            self.save_schedules()

    def save_schedules(self):
        """Optimized save to file"""
        os.makedirs("data", exist_ok=True)

        schedules_data = [
            {
                "name": s.name,
                "automation_name": s.automation_name,
                "schedule_type": s.schedule_type,
                "schedule_value": s.schedule_value,
                "enabled": s.enabled,
                "last_run": s.last_run.isoformat() if s.last_run else None,
                "next_run": s.next_run.isoformat() if s.next_run else None,
                "run_count": s.run_count,
            }
            for s in self.schedules
        ]

        with open(self._schedules_file, "w") as f:
            json.dump(schedules_data, f, separators=(",", ":"))

    def load_schedules(self):
        """Optimized load from file"""
        try:
            with open(self._schedules_file, "r") as f:
                schedules_data = json.load(f)

            self.schedules = [
                self._create_schedule_from_data(data) for data in schedules_data
            ]

            self.update_table()
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def _create_schedule_from_data(self, data):
        """Create schedule item from data dict"""
        schedule = ScheduleItem(
            data["name"],
            data["automation_name"],
            data["schedule_type"],
            data["schedule_value"],
            data["enabled"],
        )
        schedule.last_run = (
            datetime.fromisoformat(data["last_run"]) if data["last_run"] else None
        )
        schedule.next_run = (
            datetime.fromisoformat(data["next_run"]) if data["next_run"] else None
        )
        schedule.run_count = data.get("run_count", 0)
        return schedule


class ScheduleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Schedule")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Title
        title = QLabel("New Schedule")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #ffffff;")
        layout.addWidget(title)

        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # Name
        self.name_edit = QLineEdit()
        self.name_edit.setFont(QFont("Segoe UI", 11))
        self.name_edit.setMinimumHeight(36)
        self.name_edit.setStyleSheet(
            """
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #3e3e42;
                border-radius: 4px;
                background-color: #2d2d30;
                color: #e0e0e0;
            }
            QLineEdit:focus {
                border: 1px solid #007acc;
            }
        """
        )
        form_layout.addRow("Schedule Name:", self.name_edit)

        # Automation
        self.automation_edit = QLineEdit()
        self.automation_edit.setFont(QFont("Segoe UI", 11))
        self.automation_edit.setMinimumHeight(36)
        self.automation_edit.setStyleSheet(
            """
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #3e3e42;
                border-radius: 4px;
                background-color: #2d2d30;
                color: #e0e0e0;
            }
            QLineEdit:focus {
                border: 1px solid #007acc;
            }
        """
        )
        form_layout.addRow("Automation:", self.automation_edit)

        # Type
        self.type_combo = QComboBox()
        self.type_combo.addItems(["once", "interval", "daily"])
        self.type_combo.setFont(QFont("Segoe UI", 11))
        self.type_combo.setMinimumHeight(36)
        self.type_combo.setStyleSheet(
            """
            QComboBox {
                padding: 8px 12px;
                border: 1px solid #3e3e42;
                border-radius: 4px;
                background-color: #2d2d30;
                color: #e0e0e0;
            }
            QComboBox:hover {
                border: 1px solid #007acc;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d30;
                color: #e0e0e0;
                selection-background-color: #0e639c;
            }
        """
        )
        form_layout.addRow("Type:", self.type_combo)

        # Value
        self.value_edit = QLineEdit()
        self.value_edit.setFont(QFont("Segoe UI", 11))
        self.value_edit.setMinimumHeight(36)
        self.value_edit.setPlaceholderText("For interval: minutes (e.g., 30)")
        self.value_edit.setStyleSheet(
            """
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #3e3e42;
                border-radius: 4px;
                background-color: #2d2d30;
                color: #e0e0e0;
            }
            QLineEdit:focus {
                border: 1px solid #007acc;
            }
        """
        )
        form_layout.addRow("Interval:", self.value_edit)

        # Enabled
        self.enabled_check = QCheckBox("Enabled")
        self.enabled_check.setChecked(True)
        self.enabled_check.setFont(QFont("Segoe UI", 11))
        self.enabled_check.setStyleSheet("color: #e0e0e0;")
        form_layout.addRow("", self.enabled_check)

        layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        button_layout.addStretch()

        ok_button = QPushButton("Create")
        ok_button.setFont(QFont("Segoe UI", 11))
        ok_button.setMinimumHeight(36)
        ok_button.setMinimumWidth(100)
        ok_button.setCursor(Qt.CursorShape.PointingHandCursor)
        ok_button.setStyleSheet(
            """
            QPushButton {
                padding: 8px 16px;
                background-color: #0e639c;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
        """
        )
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.setFont(QFont("Segoe UI", 11))
        cancel_button.setMinimumHeight(36)
        cancel_button.setMinimumWidth(100)
        cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_button.setStyleSheet(
            """
            QPushButton {
                padding: 8px 16px;
                background-color: #3e3e42;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #4e4e52;
            }
        """
        )
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)
        self.setStyleSheet("QDialog { background-color: #252526; }")

    def get_schedule(self):
        """Get the schedule from the dialog"""
        return ScheduleItem(
            self.name_edit.text(),
            self.automation_edit.text(),
            self.type_combo.currentText(),
            self.value_edit.text(),
            self.enabled_check.isChecked(),
        )
