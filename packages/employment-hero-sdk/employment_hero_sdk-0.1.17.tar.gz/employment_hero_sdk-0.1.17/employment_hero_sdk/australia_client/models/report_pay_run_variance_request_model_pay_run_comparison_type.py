from enum import Enum


class ReportPayRunVarianceRequestModelPayRunComparisonType(str, Enum):
    PAYPERIODS = "PayPeriods"
    PAYRUNS = "PayRuns"

    def __str__(self) -> str:
        return str(self.value)
