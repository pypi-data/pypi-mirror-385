from enum import Enum


class AdditionalEarningsModelExpirationTypeEnum(str, Enum):
    AMOUNTEXPIRY = "AmountExpiry"
    DATEEXPIRY = "DateExpiry"
    NONE = "None"

    def __str__(self) -> str:
        return str(self.value)
