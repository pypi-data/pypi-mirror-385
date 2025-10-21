from enum import Enum


class FinalisePayRunOptionsNullablePayRunFinaliseActionPreference(str, Enum):
    IMMEDIATE = "Immediate"
    MANUAL = "Manual"
    SCHEDULED = "Scheduled"

    def __str__(self) -> str:
        return str(self.value)
