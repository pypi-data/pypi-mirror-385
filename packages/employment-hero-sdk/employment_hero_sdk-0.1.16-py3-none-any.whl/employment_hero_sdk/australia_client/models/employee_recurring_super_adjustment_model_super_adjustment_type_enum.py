from enum import Enum


class EmployeeRecurringSuperAdjustmentModelSuperAdjustmentTypeEnum(str, Enum):
    FIXED = "Fixed"
    PERCENTAGEGROSS = "PercentageGross"
    PERCENTAGEOTE = "PercentageOTE"
    PERCENTAGETAXABLEEARNINGS = "PercentageTaxableEarnings"

    def __str__(self) -> str:
        return str(self.value)
