from enum import Enum


class AuEssBankAccountModelBankAccountTypeEnum(str, Enum):
    BPAY = "Bpay"
    CASHORCHEQUE = "CashOrCheque"
    ELECTRONIC = "Electronic"
    MANUALDEPOSIT = "ManualDeposit"

    def __str__(self) -> str:
        return str(self.value)
