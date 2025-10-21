from enum import Enum


class AuBusinessExportModelNullableNumberOfEmployeesRangeEnum(str, Enum):
    ELEVENTOFIFTY = "ElevenToFifty"
    FIFTYONETOTWOFIFTY = "FiftyOneToTwoFifty"
    ONETOTEN = "OneToTen"
    TWOFIFTYONEANDUP = "TwoFiftyOneAndUp"

    def __str__(self) -> str:
        return str(self.value)
