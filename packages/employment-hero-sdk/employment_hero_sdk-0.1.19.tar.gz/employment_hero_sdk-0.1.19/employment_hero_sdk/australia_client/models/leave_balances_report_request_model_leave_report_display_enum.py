from enum import Enum


class LeaveBalancesReportRequestModelLeaveReportDisplayEnum(str, Enum):
    ACCRUALLOCATION = "AccrualLocation"
    DEFAULTLOCATION = "DefaultLocation"

    def __str__(self) -> str:
        return str(self.value)
