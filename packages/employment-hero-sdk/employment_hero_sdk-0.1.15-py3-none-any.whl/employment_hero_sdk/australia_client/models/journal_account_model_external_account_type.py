from enum import Enum


class JournalAccountModelExternalAccountType(str, Enum):
    ASSET = "Asset"
    ASSETANDLIABILITY = "AssetAndLiability"
    CAPITALSANDRESERVES = "CapitalsAndReserves"
    COSTOFGOODSSOLD = "CostOfGoodsSold"
    EQUITY = "Equity"
    EXPENSE = "Expense"
    INCOME = "Income"
    LIABILITY = "Liability"
    NOTALLOWED = "NotAllowed"
    OVERHEADS = "Overheads"
    PURCHASES = "Purchases"
    SALES = "Sales"
    UNKNOWN = "Unknown"

    def __str__(self) -> str:
        return str(self.value)
