from enum import Enum


class ShiftAllowanceModelShiftAllowanceOption(str, Enum):
    FIXED = "Fixed"
    PERCENTAGEOFSHIFTCOST = "PercentageOfShiftCost"
    PERDAY = "PerDay"
    PERHOURWORKED = "PerHourWorked"
    PERSHIFTUNIT = "PerShiftUnit"

    def __str__(self) -> str:
        return str(self.value)
