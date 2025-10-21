from enum import Enum


class AuEmployeeRecurringDeductionModelDeductionAmountNotReachedEnum(str, Enum):
    DONOTPAY = "DoNotPay"
    PAYTOLIMIT = "PayToLimit"

    def __str__(self) -> str:
        return str(self.value)
