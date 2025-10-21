from enum import Enum


class ManagerExpenseGetFilterStatus(str, Enum):
    APPROVED = "Approved"
    CANCELLED = "Cancelled"
    DECLINED = "Declined"
    PENDING = "Pending"
    PROCESSED = "Processed"

    def __str__(self) -> str:
        return str(self.value)
