from enum import Enum


class AuBusinessExportModelBudgetEntryMethodEnum(str, Enum):
    DIRECT = "Direct"
    PERCENTAGEOFSALES = "PercentageOfSales"

    def __str__(self) -> str:
        return str(self.value)
