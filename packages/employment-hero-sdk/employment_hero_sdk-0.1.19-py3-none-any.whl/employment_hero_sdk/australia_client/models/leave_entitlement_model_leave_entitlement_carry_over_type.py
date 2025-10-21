from enum import Enum


class LeaveEntitlementModelLeaveEntitlementCarryOverType(str, Enum):
    NONE = "None"
    UNLIMITED = "Unlimited"
    UPTO = "UpTo"

    def __str__(self) -> str:
        return str(self.value)
