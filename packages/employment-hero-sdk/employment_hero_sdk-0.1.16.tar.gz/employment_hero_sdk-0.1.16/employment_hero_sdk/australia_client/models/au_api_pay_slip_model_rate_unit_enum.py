from enum import Enum


class AuApiPaySlipModelRateUnitEnum(str, Enum):
    ANNUALLY = "Annually"
    DAILY = "Daily"
    FIXED = "Fixed"
    HOURLY = "Hourly"
    MONTHLY = "Monthly"

    def __str__(self) -> str:
        return str(self.value)
