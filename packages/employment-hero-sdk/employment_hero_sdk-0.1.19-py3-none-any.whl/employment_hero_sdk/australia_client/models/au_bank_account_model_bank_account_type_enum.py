from enum import Enum


class AuBankAccountModelBankAccountTypeEnum(str, Enum):
    BPAY = "Bpay"
    CASHORCHEQUE = "CashOrCheque"
    ELECTRONIC = "Electronic"
    MANUALDEPOSIT = "ManualDeposit"

    def __str__(self) -> str:
        return str(self.value)
