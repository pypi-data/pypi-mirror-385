from enum import Enum


class GenericManagerTimesheetGetFilterStatus(str, Enum):
    ANYEXCEPTREJECTED = "AnyExceptRejected"
    APPROVED = "Approved"
    PROCESSED = "Processed"
    REJECTED = "Rejected"
    SUBMITTED = "Submitted"

    def __str__(self) -> str:
        return str(self.value)
