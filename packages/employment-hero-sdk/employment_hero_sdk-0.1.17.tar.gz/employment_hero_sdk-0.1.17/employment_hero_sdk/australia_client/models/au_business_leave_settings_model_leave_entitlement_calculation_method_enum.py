from enum import Enum


class AuBusinessLeaveSettingsModelLeaveEntitlementCalculationMethodEnum(str, Enum):
    FULLYEAR365 = "FullYear365"
    WORKDAYS261 = "Workdays261"

    def __str__(self) -> str:
        return str(self.value)
