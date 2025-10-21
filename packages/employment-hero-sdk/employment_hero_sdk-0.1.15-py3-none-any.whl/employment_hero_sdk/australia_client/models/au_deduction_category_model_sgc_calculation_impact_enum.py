from enum import Enum


class AuDeductionCategoryModelSGCCalculationImpactEnum(str, Enum):
    NONE = "None"
    REDUCESOTE = "ReducesOTE"

    def __str__(self) -> str:
        return str(self.value)
