from enum import Enum


class AuLeaveAccrualRuleModelLeaveAccrualType(str, Enum):
    BASEDONLENGTHOFSERVICE = "BasedOnLengthOfService"
    ONGOING = "Ongoing"
    YEARLY = "Yearly"

    def __str__(self) -> str:
        return str(self.value)
