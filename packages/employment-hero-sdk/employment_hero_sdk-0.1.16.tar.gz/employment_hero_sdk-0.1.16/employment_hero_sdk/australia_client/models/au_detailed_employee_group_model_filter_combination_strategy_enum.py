from enum import Enum


class AuDetailedEmployeeGroupModelFilterCombinationStrategyEnum(str, Enum):
    AND = "And"
    OR = "Or"

    def __str__(self) -> str:
        return str(self.value)
