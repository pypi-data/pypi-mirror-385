from enum import Enum


class AuUnstructuredEmployeeModelNullableCloselyHeldReportingEnum(str, Enum):
    PERPAYRUN = "PerPayRun"
    PERQUARTER = "PerQuarter"

    def __str__(self) -> str:
        return str(self.value)
