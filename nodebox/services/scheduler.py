"""
Workflow Scheduling Service Data Structures.
"""


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
        self.schedule_type = schedule_type
        self.schedule_value = schedule_value
        self.enabled = enabled
        self.last_run = None
        self.next_run = None
        self.run_count = 0


__all__ = ["ScheduleItem"]
