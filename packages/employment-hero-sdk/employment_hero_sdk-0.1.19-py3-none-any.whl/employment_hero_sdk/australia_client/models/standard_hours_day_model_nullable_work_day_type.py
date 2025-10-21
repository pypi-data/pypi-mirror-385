from enum import Enum


class StandardHoursDayModelNullableWorkDayType(str, Enum):
    FULL = "Full"
    HALF = "Half"
    OFF = "Off"
    REST = "Rest"

    def __str__(self) -> str:
        return str(self.value)
