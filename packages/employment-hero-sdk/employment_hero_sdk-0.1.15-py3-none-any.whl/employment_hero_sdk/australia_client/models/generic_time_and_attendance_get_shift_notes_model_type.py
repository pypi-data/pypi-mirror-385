from enum import Enum


class GenericTimeAndAttendanceGetShiftNotesModelType(str, Enum):
    CLOCKOFF = "ClockOff"
    CLOCKON = "ClockOn"
    SHIFT = "Shift"

    def __str__(self) -> str:
        return str(self.value)
