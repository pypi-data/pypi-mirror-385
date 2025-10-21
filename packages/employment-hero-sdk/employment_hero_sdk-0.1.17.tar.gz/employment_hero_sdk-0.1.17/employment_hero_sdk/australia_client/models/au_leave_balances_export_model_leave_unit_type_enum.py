from enum import Enum


class AuLeaveBalancesExportModelLeaveUnitTypeEnum(str, Enum):
    DAYS = "Days"
    HOURS = "Hours"
    WEEKS = "Weeks"

    def __str__(self) -> str:
        return str(self.value)
