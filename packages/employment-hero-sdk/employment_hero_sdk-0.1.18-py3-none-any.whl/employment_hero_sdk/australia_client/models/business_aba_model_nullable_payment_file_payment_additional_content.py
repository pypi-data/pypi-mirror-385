from enum import Enum


class BusinessAbaModelNullablePaymentFilePaymentAdditionalContent(str, Enum):
    EMPLOYEEID = "EmployeeId"
    NONE = "None"
    PAYMENTDATE = "PaymentDate"
    PAYRUNID = "PayRunId"
    PERIODENDINGDATE = "PeriodEndingDate"

    def __str__(self) -> str:
        return str(self.value)
