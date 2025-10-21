from enum import Enum


class GrossToNetReportRequestNullableDateTypeEnum(str, Enum):
    DATERANGE = "DateRange"
    PAYRUN = "PayRun"
    SUPERBATCH = "SuperBatch"

    def __str__(self) -> str:
        return str(self.value)
