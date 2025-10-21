from enum import Enum


class AuAvailableBusinessModelBudgetEntryMethodEnum(str, Enum):
    DIRECT = "Direct"
    PERCENTAGEOFSALES = "PercentageOfSales"

    def __str__(self) -> str:
        return str(self.value)
