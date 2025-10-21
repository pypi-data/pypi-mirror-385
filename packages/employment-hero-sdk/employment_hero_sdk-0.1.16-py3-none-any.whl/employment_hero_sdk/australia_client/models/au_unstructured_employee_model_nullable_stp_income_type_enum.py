from enum import Enum


class AuUnstructuredEmployeeModelNullableStpIncomeTypeEnum(str, Enum):
    CLOSELYHELD = "CloselyHeld"
    FOREIGNEMPLOYMENT = "ForeignEmployment"
    INBOUNDASSIGNEE = "InboundAssignee"
    LABOURHIRE = "LabourHire"
    OTHERSPECIFIEDPAYMENTS = "OtherSpecifiedPayments"

    def __str__(self) -> str:
        return str(self.value)
