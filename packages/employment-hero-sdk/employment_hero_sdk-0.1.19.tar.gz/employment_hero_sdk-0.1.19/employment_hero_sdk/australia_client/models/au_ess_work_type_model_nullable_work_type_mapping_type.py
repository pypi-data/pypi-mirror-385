from enum import Enum


class AuEssWorkTypeModelNullableWorkTypeMappingType(str, Enum):
    LEAVECATEGORY = "LeaveCategory"
    PAYCATEGORY = "PayCategory"
    PRIMARYPAYCATEGORY = "PrimaryPayCategory"
    SHIFTCONDITION = "ShiftCondition"

    def __str__(self) -> str:
        return str(self.value)
