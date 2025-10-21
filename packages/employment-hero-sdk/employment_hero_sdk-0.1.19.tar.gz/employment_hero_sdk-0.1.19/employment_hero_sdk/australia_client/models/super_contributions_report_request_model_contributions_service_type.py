from enum import Enum


class SuperContributionsReportRequestModelContributionsServiceType(str, Enum):
    EMPLOYEE = "Employee"
    SUPERFUND = "SuperFund"

    def __str__(self) -> str:
        return str(self.value)
