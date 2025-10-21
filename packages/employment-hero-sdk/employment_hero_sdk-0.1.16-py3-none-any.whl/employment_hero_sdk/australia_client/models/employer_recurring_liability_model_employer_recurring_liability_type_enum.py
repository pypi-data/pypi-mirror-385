from enum import Enum


class EmployerRecurringLiabilityModelEmployerRecurringLiabilityTypeEnum(str, Enum):
    FIXED = "Fixed"
    PERCENTAGEGROSS = "PercentageGross"
    PERCENTAGEOTE = "PercentageOTE"
    PERCENTAGESUPERANNUATION = "PercentageSuperannuation"

    def __str__(self) -> str:
        return str(self.value)
