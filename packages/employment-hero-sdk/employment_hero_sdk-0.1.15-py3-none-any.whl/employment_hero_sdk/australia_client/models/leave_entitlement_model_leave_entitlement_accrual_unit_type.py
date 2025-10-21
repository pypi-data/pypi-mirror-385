from enum import Enum


class LeaveEntitlementModelLeaveEntitlementAccrualUnitType(str, Enum):
    MONTHLY = "Monthly"
    YEARLY = "Yearly"

    def __str__(self) -> str:
        return str(self.value)
