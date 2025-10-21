from enum import Enum


class AuManagerRosterShiftModelNullableShiftAssignmentStatusEnum(str, Enum):
    ASSIGNED = "Assigned"
    BIDDING = "Bidding"
    PENDING = "Pending"
    PENDINGSHIFTSWAP = "PendingShiftSwap"
    PENDINGSHIFTSWAPAWAITINGAPPROVAL = "PendingShiftSwapAwaitingApproval"
    PROPOSEDSHIFTSWAP = "ProposedShiftSwap"
    PROPOSEDSHIFTSWAPAWAITINGAPPROVAL = "ProposedShiftSwapAwaitingApproval"

    def __str__(self) -> str:
        return str(self.value)
