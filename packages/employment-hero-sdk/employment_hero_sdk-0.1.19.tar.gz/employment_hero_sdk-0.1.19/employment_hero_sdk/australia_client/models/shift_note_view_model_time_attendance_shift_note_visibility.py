from enum import Enum


class ShiftNoteViewModelTimeAttendanceShiftNoteVisibility(str, Enum):
    HIDDEN = "Hidden"
    VISIBLE = "Visible"

    def __str__(self) -> str:
        return str(self.value)
