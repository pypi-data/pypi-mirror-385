from enum import Enum


class AuRosterShiftGenerateTimesheetModelNullableShiftAssignmentStatusEnum(str, Enum):
    ASSIGNED = "Assigned"
    BIDDING = "Bidding"
    PENDING = "Pending"
    PENDINGSHIFTSWAP = "PendingShiftSwap"
    PENDINGSHIFTSWAPAWAITINGAPPROVAL = "PendingShiftSwapAwaitingApproval"
    PROPOSEDSHIFTSWAP = "ProposedShiftSwap"
    PROPOSEDSHIFTSWAPAWAITINGAPPROVAL = "ProposedShiftSwapAwaitingApproval"

    def __str__(self) -> str:
        return str(self.value)
