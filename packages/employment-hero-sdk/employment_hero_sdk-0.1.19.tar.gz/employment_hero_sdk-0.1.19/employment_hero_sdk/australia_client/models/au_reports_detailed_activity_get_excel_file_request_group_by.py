from enum import Enum


class AuReportsDetailedActivityGetExcelFileRequestGroupBy(str, Enum):
    DEFAULTLOCATION = "DefaultLocation"
    EARNINGSLOCATION = "EarningsLocation"
    ROLLUPLOCATION = "RollUpLocation"

    def __str__(self) -> str:
        return str(self.value)
