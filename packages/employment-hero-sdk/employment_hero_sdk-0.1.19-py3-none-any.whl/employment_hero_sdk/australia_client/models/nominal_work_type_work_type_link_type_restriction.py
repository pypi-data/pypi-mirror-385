from enum import Enum


class NominalWorkTypeWorkTypeLinkTypeRestriction(str, Enum):
    LEAVECATEGORY = "LeaveCategory"
    PAYCATEGORY = "PayCategory"
    SHIFTCONDITION = "ShiftCondition"

    def __str__(self) -> str:
        return str(self.value)
