from enum import Enum


class PayConditionRuleSetModelRuleSetPeriodType(str, Enum):
    CALENDARMONTH = "CalendarMonth"
    EIGHTWEEKLY = "EightWeekly"
    FORTNIGHTLY = "Fortnightly"
    FOURWEEKLY = "FourWeekly"
    MONTHLY = "Monthly"
    SIXWEEKLY = "SixWeekly"
    THREEWEEKLY = "ThreeWeekly"
    WEEKLY = "Weekly"

    def __str__(self) -> str:
        return str(self.value)
