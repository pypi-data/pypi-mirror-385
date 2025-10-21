from enum import Enum


class AuEssTimeAndAttendanceGetShiftNotesModelType(str, Enum):
    CLOCKOFF = "ClockOff"
    CLOCKON = "ClockOn"
    SHIFT = "Shift"

    def __str__(self) -> str:
        return str(self.value)
