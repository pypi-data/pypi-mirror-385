from enum import Enum


class ShiftAllowanceModelShiftAllowanceType(str, Enum):
    ALLPURPOSE = "AllPurpose"
    STANDARD = "Standard"

    def __str__(self) -> str:
        return str(self.value)
