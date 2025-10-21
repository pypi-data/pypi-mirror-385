from enum import Enum


class LeaveEntitlementTierModelLeaveEntitlementAccrualStartDateUnitType(str, Enum):
    MONTH = "Month"
    YEAR = "Year"

    def __str__(self) -> str:
        return str(self.value)
