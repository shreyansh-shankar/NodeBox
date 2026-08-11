import json
import os
from datetime import datetime, timedelta

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
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

from nodebox.core.paths import resource_path
from nodebox.services.scheduler import ScheduleItem


class ScheduleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Automation Schedule")
        self.setModal(True)
        self.setMinimumWidth(520)
        self.setStyleSheet("""
            QDialog { background-color: #0A0C10; color: #F0F2F8; }
        """)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("New Schedule Rule")
        title.setFont(QFont("Poppins", 15, QFont.Weight.Bold))
        title.setStyleSheet("color: #F0F2F8;")
        layout.addWidget(title)

        form_layout = QFormLayout()
        form_layout.setSpacing(14)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.name_edit = QLineEdit()
        self.name_edit.setMinimumHeight(38)
        form_layout.addRow("Schedule Name:", self.name_edit)

        self.automation_edit = QLineEdit()
        self.automation_edit.setMinimumHeight(38)
        form_layout.addRow("Automation Name:", self.automation_edit)

        self.type_combo = QComboBox()
        self.type_combo.addItems(["once", "interval", "daily"])
        self.type_combo.setMinimumHeight(38)
        form_layout.addRow("Schedule Type:", self.type_combo)

        self.value_edit = QLineEdit()
        self.value_edit.setMinimumHeight(38)
        self.value_edit.setPlaceholderText("For interval: minutes (e.g., 30)")
        form_layout.addRow("Interval / Time:", self.value_edit)

        self.enabled_check = QCheckBox("Enable Schedule Immediately")
        self.enabled_check.setChecked(True)
        self.enabled_check.setFont(QFont("Poppins", 10))
        form_layout.addRow("", self.enabled_check)

        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        button_layout.addStretch()

        ok_button = QPushButton("Create Schedule")
        ok_button.setFont(QFont("Poppins", 10, QFont.Weight.DemiBold))
        ok_button.setMinimumHeight(38)
        ok_button.setMinimumWidth(120)
        ok_button.setCursor(Qt.CursorShape.PointingHandCursor)
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #6366F1;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 4px 20px;
            }
            QPushButton:hover { background-color: #5153D6; }
        """)
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.setFont(QFont("Poppins", 10, QFont.Weight.Medium))
        cancel_button.setMinimumHeight(38)
        cancel_button.setMinimumWidth(100)
        cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_button.setStyleSheet("""
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
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def get_schedule(self):
        return ScheduleItem(
            self.name_edit.text(),
            self.automation_edit.text(),
            self.type_combo.currentText(),
            self.value_edit.text(),
            self.enabled_check.isChecked(),
        )


class WorkflowScheduler(QWidget):
    schedule_triggered = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.schedules = []
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_schedules)
        self.timer.start(30000)
        self._schedules_file = "data/schedules.json"
        self.init_ui()
        self.load_schedules()

    def get_icon(self, icon_name):
        icon_path = resource_path(f"assets/icons/{icon_name}.svg")
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        return QIcon()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(28, 28, 28, 28)
        main_layout.setSpacing(20)

        title = QLabel("Workflow Scheduler")
        title.setFont(QFont("Poppins", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #F0F2F8;")
        main_layout.addWidget(title)

        subtitle = QLabel("Automate recurring executions on custom intervals or schedules")
        subtitle.setFont(QFont("Poppins", 11))
        subtitle.setStyleSheet("color: #4A5578; margin-bottom: 4px;")
        main_layout.addWidget(subtitle)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setSpacing(20)

        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(12)

        add_button = QPushButton("Add Schedule")
        add_button.setIcon(self.get_icon("plus-circle"))
        add_button.setFont(QFont("Poppins", 10, QFont.Weight.DemiBold))
        add_button.setMinimumHeight(38)
        add_button.setCursor(Qt.CursorShape.PointingHandCursor)
        add_button.setStyleSheet("""
            QPushButton {
                padding: 6px 20px;
                background-color: #6366F1;
                color: white;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover { background-color: #5153D6; }
        """)
        add_button.clicked.connect(self.add_schedule_dialog)
        actions_layout.addWidget(add_button)

        self.run_now_button = QPushButton("  Run Now")
        self.run_now_button.setIcon(self.get_icon("activity"))
        self.run_now_button.setFont(QFont("Poppins", 11, QFont.Weight.Bold))
        self.run_now_button.setMinimumHeight(42)
        self.run_now_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.run_now_button.setStyleSheet(
            """
            QPushButton {
                padding: 10px 22px;
                background-color: #10B981;
                color: white;
                border: none;
                border-radius: 8px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """
        )
        self.run_now_button.clicked.connect(self.run_selected_now)
        actions_layout.addWidget(self.run_now_button)

        self.toggle_button = QPushButton("  Toggle Status")
        self.toggle_button.setIcon(self.get_icon("clock"))
        self.toggle_button.setFont(QFont("Poppins", 11, QFont.Weight.Bold))
        self.toggle_button.setMinimumHeight(42)
        self.toggle_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_button.setStyleSheet(
            """
            QPushButton {
                padding: 10px 22px;
                background-color: #F59E0B;
                color: white;
                border: none;
                border-radius: 8px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #D97706;
            }
        """
        )
        self.toggle_button.clicked.connect(self.toggle_selected)
        actions_layout.addWidget(self.toggle_button)

        self.delete_button = QPushButton("  Delete")
        self.delete_button.setIcon(self.get_icon("x"))
        self.delete_button.setFont(QFont("Poppins", 11, QFont.Weight.Bold))
        self.delete_button.setMinimumHeight(42)
        self.delete_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_button.setStyleSheet(
            """
            QPushButton {
                padding: 10px 22px;
                background-color: #EF4444;
                color: white;
                border: none;
                border-radius: 8px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
        """
        )
        self.delete_button.clicked.connect(self.delete_selected)
        actions_layout.addWidget(self.delete_button)

        actions_layout.addStretch()
        content_layout.addLayout(actions_layout)

        tasks_label = QLabel("Scheduled Tasks")
        tasks_label.setFont(QFont("Poppins", 14, QFont.Weight.Bold))
        tasks_label.setStyleSheet("color: #F9FAFB;")
        content_layout.addWidget(tasks_label)

        self.schedules_table = QTableWidget()
        self.schedules_table.setColumnCount(6)
        self.schedules_table.setHorizontalHeaderLabels(
            ["Name", "Automation", "Type", "Status", "Next Run", "Runs"]
        )
        self.schedules_table.setFont(QFont("Poppins", 10))
        self.schedules_table.setAlternatingRowColors(True)
        self.schedules_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.schedules_table.setMinimumHeight(300)
        self.schedules_table.horizontalHeader().setStretchLastSection(True)
        content_layout.addWidget(self.schedules_table)
        content_layout.addStretch()

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        self.setLayout(main_layout)
        self.setStyleSheet("QWidget { background-color: #121418; color: #F9FAFB; }")

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
        self.schedules_table.setRowCount(len(self.schedules))

        for i, schedule in enumerate(self.schedules):
            name_item = QTableWidgetItem(schedule.name)
            name_item.setFont(QFont("Poppins", 10, QFont.Weight.Bold))
            self.schedules_table.setItem(i, 0, name_item)

            self.schedules_table.setItem(
                i, 1, QTableWidgetItem(schedule.automation_name)
            )

            type_item = QTableWidgetItem(schedule.schedule_type.capitalize())
            self.schedules_table.setItem(i, 2, type_item)

            status_text = "Enabled" if schedule.enabled else "Disabled"
            status_item = QTableWidgetItem(status_text)
            self.schedules_table.setItem(i, 3, status_item)

            next_run_text = (
                schedule.next_run.strftime("%Y-%m-%d %H:%M")
                if schedule.next_run
                else "Not scheduled"
            )
            self.schedules_table.setItem(i, 4, QTableWidgetItem(next_run_text))

            self.schedules_table.setItem(
                i, 5, QTableWidgetItem(str(schedule.run_count))
            )

    def check_schedules(self):
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
        now = datetime.now()

        if schedule.schedule_type == "interval":
            interval_minutes = int(schedule.schedule_value)
            schedule.next_run = now + timedelta(minutes=interval_minutes)
        elif schedule.schedule_type == "daily":
            schedule.next_run = now + timedelta(days=1)
        elif schedule.schedule_type == "once":
            schedule.enabled = False
            schedule.next_run = None

    def toggle_selected(self):
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
        current_row = self.schedules_table.currentRow()
        if current_row >= 0:
            del self.schedules[current_row]
            self.update_table()
            self.save_schedules()

    def run_selected_now(self):
        current_row = self.schedules_table.currentRow()
        if current_row >= 0:
            automation_name = self.schedules[current_row].automation_name
            self.schedule_triggered.emit(automation_name)
            self.schedules[current_row].last_run = datetime.now()
            self.schedules[current_row].run_count += 1
            self.update_table()
            self.save_schedules()

    def save_schedules(self):
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


__all__ = ["ScheduleDialog", "WorkflowScheduler"]
