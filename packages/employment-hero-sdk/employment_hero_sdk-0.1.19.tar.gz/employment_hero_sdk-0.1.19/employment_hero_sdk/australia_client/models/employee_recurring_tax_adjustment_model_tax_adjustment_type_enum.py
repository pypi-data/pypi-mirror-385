from enum import Enum


class EmployeeRecurringTaxAdjustmentModelTaxAdjustmentTypeEnum(str, Enum):
    FIXED = "Fixed"
    PERCENTAGEGROSS = "PercentageGross"
    PERCENTAGETAXABLEEARNINGS = "PercentageTaxableEarnings"

    def __str__(self) -> str:
        return str(self.value)
