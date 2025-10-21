from enum import Enum


class ReportLeaveLiabilityRequestModelNullableLeaveReportDisplayEnum(str, Enum):
    ACCRUALLOCATION = "AccrualLocation"
    DEFAULTLOCATION = "DefaultLocation"

    def __str__(self) -> str:
        return str(self.value)
