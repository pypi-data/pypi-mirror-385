from enum import Enum


class GenericTimeAndAttendanceGetShiftNotesModelVisibility(str, Enum):
    HIDDEN = "Hidden"
    VISIBLE = "Visible"

    def __str__(self) -> str:
        return str(self.value)
