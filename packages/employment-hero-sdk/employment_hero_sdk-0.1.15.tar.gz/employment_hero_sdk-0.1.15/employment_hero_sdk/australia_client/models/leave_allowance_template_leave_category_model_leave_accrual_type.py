from enum import Enum


class LeaveAllowanceTemplateLeaveCategoryModelLeaveAccrualType(str, Enum):
    BASEDONLENGTHOFSERVICE = "BasedOnLengthOfService"
    ONGOING = "Ongoing"
    YEARLY = "Yearly"

    def __str__(self) -> str:
        return str(self.value)
