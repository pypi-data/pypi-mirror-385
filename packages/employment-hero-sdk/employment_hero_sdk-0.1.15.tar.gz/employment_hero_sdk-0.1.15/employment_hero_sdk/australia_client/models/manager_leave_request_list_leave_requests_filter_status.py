from enum import Enum


class ManagerLeaveRequestListLeaveRequestsFilterStatus(str, Enum):
    APPROVED = "Approved"
    CANCELLED = "Cancelled"
    PENDING = "Pending"
    REJECTED = "Rejected"

    def __str__(self) -> str:
        return str(self.value)
