from enum import Enum


class PayrollTaxReportRequestModelPayrollTaxGroupByEnum(str, Enum):
    DEFAULTLOCATION = "DefaultLocation"
    EARNINGSLOCATION = "EarningsLocation"
    EARNINGSROLLUPLOCATION = "EarningsRollUpLocation"

    def __str__(self) -> str:
        return str(self.value)
