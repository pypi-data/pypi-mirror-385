from enum import Enum


class LeaveEntitlementTierModelLeaveEntitlementAccrualUnitType(str, Enum):
    MONTHLY = "Monthly"
    YEARLY = "Yearly"

    def __str__(self) -> str:
        return str(self.value)
