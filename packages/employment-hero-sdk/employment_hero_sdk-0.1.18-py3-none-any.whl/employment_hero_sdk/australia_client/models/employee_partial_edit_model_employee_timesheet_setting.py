from enum import Enum


class EmployeePartialEditModelEmployeeTimesheetSetting(str, Enum):
    DISABLED = "Disabled"
    ENABLED = "Enabled"
    ENABLEDFOREXCEPTIONS = "EnabledForExceptions"

    def __str__(self) -> str:
        return str(self.value)
