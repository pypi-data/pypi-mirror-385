from enum import Enum


class AuReportsSuperContributionsGetExcelReportRequestGroupBy(str, Enum):
    EMPLOYEE = "Employee"
    SUPERFUND = "SuperFund"

    def __str__(self) -> str:
        return str(self.value)
