from enum import Enum


class AuPayScheduleModelAuPayCycleFrequencyEnum(str, Enum):
    FORTNIGHTLY = "Fortnightly"
    MONTHLY = "Monthly"
    WEEKLY = "Weekly"

    def __str__(self) -> str:
        return str(self.value)
