from enum import Enum


class LeaveRequestFilterModelLeaveRequestGroupBy(str, Enum):
    EMPLOYEE = "Employee"
    LEAVETYPE = "LeaveType"

    def __str__(self) -> str:
        return str(self.value)
