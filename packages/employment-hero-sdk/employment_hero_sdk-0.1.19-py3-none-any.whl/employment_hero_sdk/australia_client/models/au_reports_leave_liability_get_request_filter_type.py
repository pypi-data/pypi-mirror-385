from enum import Enum


class AuReportsLeaveLiabilityGetRequestFilterType(str, Enum):
    DATERANGE = "DateRange"
    PAYRUN = "PayRun"
    SUPERBATCH = "SuperBatch"

    def __str__(self) -> str:
        return str(self.value)
