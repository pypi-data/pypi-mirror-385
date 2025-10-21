from enum import Enum


class ManagerLeaveRequestListLeaveRequestsFilterGroupBy(str, Enum):
    EMPLOYEE = "Employee"
    LEAVETYPE = "LeaveType"

    def __str__(self) -> str:
        return str(self.value)
