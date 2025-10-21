from enum import Enum


class AuEmployeeFilterModelFilterOperatorEnum(str, Enum):
    IN = "In"
    NOTIN = "NotIn"

    def __str__(self) -> str:
        return str(self.value)
