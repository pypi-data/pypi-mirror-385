from enum import Enum


class LeaveAllowanceTemplateLeaveCategoryModelNullableLeaveAllowanceUnitEnum(str, Enum):
    DAYPERCALENDARDAY = "DayPerCalendarDay"
    DAYPERMONTH = "DayPerMonth"
    DAYS = "Days"
    HOURSPERHOURWORKED = "HoursPerHourWorked"
    HOURSPERPAYRUN = "HoursPerPayRun"
    STANDARDDAYS = "StandardDays"
    STANDARDWEEKS = "StandardWeeks"
    WEEKS = "Weeks"

    def __str__(self) -> str:
        return str(self.value)
