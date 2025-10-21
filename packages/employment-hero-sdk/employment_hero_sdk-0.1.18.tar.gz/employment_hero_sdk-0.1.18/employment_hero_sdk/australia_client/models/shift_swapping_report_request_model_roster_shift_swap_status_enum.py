from enum import Enum


class ShiftSwappingReportRequestModelRosterShiftSwapStatusEnum(str, Enum):
    ACCEPTED = "Accepted"
    APPROVEDBYMANAGER = "ApprovedByManager"
    AWAITINGMANAGERAPPROVAL = "AwaitingManagerApproval"
    CANCELLED = "Cancelled"
    CREATED = "Created"
    DECLINED = "Declined"
    REJECTEDBYMANAGER = "RejectedByManager"

    def __str__(self) -> str:
        return str(self.value)
