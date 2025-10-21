from enum import Enum


class AuBusinessHoursLeaveRequestListLeaveRequestsFilterGroupBy(str, Enum):
    EMPLOYEE = "Employee"
    LEAVETYPE = "LeaveType"

    def __str__(self) -> str:
        return str(self.value)
