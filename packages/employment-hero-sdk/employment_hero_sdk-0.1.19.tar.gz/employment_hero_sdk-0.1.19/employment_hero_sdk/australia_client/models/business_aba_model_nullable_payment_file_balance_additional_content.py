from enum import Enum


class BusinessAbaModelNullablePaymentFileBalanceAdditionalContent(str, Enum):
    NONE = "None"
    PAYMENTDATE = "PaymentDate"
    PAYRUNID = "PayRunId"
    PERIODENDINGDATE = "PeriodEndingDate"

    def __str__(self) -> str:
        return str(self.value)
