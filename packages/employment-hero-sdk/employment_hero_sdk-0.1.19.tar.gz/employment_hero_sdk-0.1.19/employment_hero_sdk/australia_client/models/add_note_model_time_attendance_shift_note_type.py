from enum import Enum


class AddNoteModelTimeAttendanceShiftNoteType(str, Enum):
    CLOCKOFF = "ClockOff"
    CLOCKON = "ClockOn"
    SHIFT = "Shift"

    def __str__(self) -> str:
        return str(self.value)
