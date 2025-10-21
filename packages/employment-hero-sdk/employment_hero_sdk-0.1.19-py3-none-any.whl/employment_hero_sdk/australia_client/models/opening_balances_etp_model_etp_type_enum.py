from enum import Enum


class OpeningBalancesEtpModelEtpTypeEnum(str, Enum):
    O = "O"
    P = "P"
    R = "R"
    S = "S"

    def __str__(self) -> str:
        return str(self.value)
