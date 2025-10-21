from enum import Enum


class AuEmployeeRecurringDeductionModelPreservedEarningsCalculationTypeEnum(str, Enum):
    AMOUNT = "Amount"
    NEVER = "Never"
    PERCENTAGE = "Percentage"

    def __str__(self) -> str:
        return str(self.value)
