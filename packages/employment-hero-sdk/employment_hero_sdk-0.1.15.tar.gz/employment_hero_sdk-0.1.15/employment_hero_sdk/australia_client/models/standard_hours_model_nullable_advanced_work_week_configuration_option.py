from enum import Enum


class StandardHoursModelNullableAdvancedWorkWeekConfigurationOption(str, Enum):
    HOURONLY = "HourOnly"
    STARTTIMEANDSTOPTIME = "StartTimeAndStopTime"
    WORKDAYTYPE = "WorkDayType"

    def __str__(self) -> str:
        return str(self.value)
