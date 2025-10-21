from enum import Enum


class AuLeaveAllowanceTemplateLeaveCategoryApiModelLeaveAccrualType(str, Enum):
    BASEDONLENGTHOFSERVICE = "BasedOnLengthOfService"
    ONGOING = "Ongoing"
    YEARLY = "Yearly"

    def __str__(self) -> str:
        return str(self.value)
