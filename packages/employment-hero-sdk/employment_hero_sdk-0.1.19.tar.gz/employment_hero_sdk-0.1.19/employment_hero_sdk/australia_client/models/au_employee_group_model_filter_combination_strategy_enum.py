from enum import Enum


class AuEmployeeGroupModelFilterCombinationStrategyEnum(str, Enum):
    AND = "And"
    OR = "Or"

    def __str__(self) -> str:
        return str(self.value)
