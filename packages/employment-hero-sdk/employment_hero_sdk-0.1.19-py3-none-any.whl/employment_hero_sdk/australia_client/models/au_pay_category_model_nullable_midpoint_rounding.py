from enum import Enum


class AuPayCategoryModelNullableMidpointRounding(str, Enum):
    AWAYFROMZERO = "AwayFromZero"
    TOEVEN = "ToEven"

    def __str__(self) -> str:
        return str(self.value)
