from enum import Enum


class AuLeaveCategoryModelAuLeaveCategoryTypeEnum(str, Enum):
    LONGSERVICELEAVE = "LongServiceLeave"
    PERSONALCARERSLEAVE = "PersonalCarersLeave"
    STANDARD = "Standard"

    def __str__(self) -> str:
        return str(self.value)
