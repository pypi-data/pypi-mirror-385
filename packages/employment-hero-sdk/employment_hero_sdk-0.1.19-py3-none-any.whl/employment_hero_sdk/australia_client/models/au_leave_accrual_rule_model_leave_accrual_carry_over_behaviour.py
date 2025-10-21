from enum import Enum


class AuLeaveAccrualRuleModelLeaveAccrualCarryOverBehaviour(str, Enum):
    CARRYENTIREAMOUNT = "CarryEntireAmount"
    CARRYHOURS = "CarryHours"

    def __str__(self) -> str:
        return str(self.value)
