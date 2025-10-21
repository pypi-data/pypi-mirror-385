from enum import Enum


class AuReportsLeaveBalancesGetRequestGroupBy(str, Enum):
    ACCRUALLOCATION = "AccrualLocation"
    DEFAULTLOCATION = "DefaultLocation"

    def __str__(self) -> str:
        return str(self.value)
