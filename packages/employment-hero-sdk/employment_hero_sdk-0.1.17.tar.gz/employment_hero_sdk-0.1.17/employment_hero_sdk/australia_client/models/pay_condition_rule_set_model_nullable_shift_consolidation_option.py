from enum import Enum


class PayConditionRuleSetModelNullableShiftConsolidationOption(str, Enum):
    DURATION = "Duration"
    NONE = "None"
    SAMEDAY = "SameDay"

    def __str__(self) -> str:
        return str(self.value)
