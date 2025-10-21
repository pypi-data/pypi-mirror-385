from enum import Enum


class FinalisePayRunOptionsPublishPaySlipsPreference(str, Enum):
    IMMEDIATE = "Immediate"
    MANUAL = "Manual"
    SCHEDULED = "Scheduled"

    def __str__(self) -> str:
        return str(self.value)
