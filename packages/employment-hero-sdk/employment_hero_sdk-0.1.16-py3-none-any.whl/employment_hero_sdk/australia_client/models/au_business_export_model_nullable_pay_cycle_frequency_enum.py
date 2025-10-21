from enum import Enum


class AuBusinessExportModelNullablePayCycleFrequencyEnum(str, Enum):
    ANNUALLY = "Annually"
    FORTNIGHTLY = "Fortnightly"
    FOURWEEKLY = "FourWeekly"
    HALFMONTHLY = "HalfMonthly"
    MONTHLY = "Monthly"
    QUARTERLY = "Quarterly"
    WEEKLY = "Weekly"

    def __str__(self) -> str:
        return str(self.value)
