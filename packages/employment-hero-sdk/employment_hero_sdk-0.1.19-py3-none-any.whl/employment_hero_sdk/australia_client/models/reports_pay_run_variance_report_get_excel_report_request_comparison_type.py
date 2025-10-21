from enum import Enum


class ReportsPayRunVarianceReportGetExcelReportRequestComparisonType(str, Enum):
    PAYPERIODS = "PayPeriods"
    PAYRUNS = "PayRuns"

    def __str__(self) -> str:
        return str(self.value)
