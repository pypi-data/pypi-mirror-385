from enum import Enum


class ShiftNoteViewModelTimeAttendanceShiftNoteType(str, Enum):
    CLOCKOFF = "ClockOff"
    CLOCKON = "ClockOn"
    SHIFT = "Shift"

    def __str__(self) -> str:
        return str(self.value)
