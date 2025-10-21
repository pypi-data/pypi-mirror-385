from enum import Enum


class PayrollAccessModelNullableBusinessRestrictionTypeEnum(str, Enum):
    PAYEVENTAPPROVER = "PayEventApprover"
    PAYMENTAPPROVERALLSCHEDULES = "PaymentApproverAllSchedules"
    PAYMENTAPPROVERSELECTEDSCHEDULES = "PaymentApproverSelectedSchedules"
    PAYRUNAPPROVERALLSCHEDULES = "PayRunApproverAllSchedules"
    PAYRUNAPPROVERSELECTEDSCHEDULES = "PayRunApproverSelectedSchedules"
    PAYRUNCREATORALLSCHEDULES = "PayRunCreatorAllSchedules"
    PAYRUNCREATORSELECTEDSCHEDULES = "PayRunCreatorSelectedSchedules"

    def __str__(self) -> str:
        return str(self.value)
