from enum import Enum


class AuReportsTimesheetGetTimesheetLineStatusType(str, Enum):
    APPROVED = "Approved"
    MISSING = "Missing"
    PROCESSED = "Processed"
    REJECTED = "Rejected"
    SUBMITTED = "Submitted"

    def __str__(self) -> str:
        return str(self.value)
