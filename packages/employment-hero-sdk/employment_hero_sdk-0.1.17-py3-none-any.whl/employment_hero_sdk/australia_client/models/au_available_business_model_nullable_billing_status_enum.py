from enum import Enum


class AuAvailableBusinessModelNullableBillingStatusEnum(str, Enum):
    BILLABLE = "Billable"
    NOTBILLABLE = "NotBillable"
    TRIAL = "Trial"

    def __str__(self) -> str:
        return str(self.value)
