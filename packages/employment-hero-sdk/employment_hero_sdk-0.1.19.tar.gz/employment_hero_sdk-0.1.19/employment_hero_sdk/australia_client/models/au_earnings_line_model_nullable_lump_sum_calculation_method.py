from enum import Enum


class AuEarningsLineModelNullableLumpSumCalculationMethod(str, Enum):
    A = "A"
    B2 = "B2"
    NOTAPPLICABLE = "NotApplicable"

    def __str__(self) -> str:
        return str(self.value)
