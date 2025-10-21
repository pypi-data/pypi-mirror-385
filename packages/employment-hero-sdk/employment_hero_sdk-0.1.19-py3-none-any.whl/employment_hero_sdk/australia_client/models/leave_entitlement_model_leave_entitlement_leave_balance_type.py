from enum import Enum


class LeaveEntitlementModelLeaveEntitlementLeaveBalanceType(str, Enum):
    FULL = "Full"
    NONE = "None"
    PRORATA = "ProRata"

    def __str__(self) -> str:
        return str(self.value)
