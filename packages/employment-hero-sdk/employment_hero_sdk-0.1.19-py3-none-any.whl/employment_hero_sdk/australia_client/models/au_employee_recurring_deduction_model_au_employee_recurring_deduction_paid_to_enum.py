from enum import Enum


class AuEmployeeRecurringDeductionModelAuEmployeeRecurringDeductionPaidToEnum(str, Enum):
    BANKACCOUNT = "BankAccount"
    BPAY = "Bpay"
    CPFB = "CPFB"
    MANUAL = "Manual"
    PENSIONSCHEME = "PensionScheme"
    SUPERFUND = "SuperFund"
    TAXOFFICE = "TaxOffice"

    def __str__(self) -> str:
        return str(self.value)
