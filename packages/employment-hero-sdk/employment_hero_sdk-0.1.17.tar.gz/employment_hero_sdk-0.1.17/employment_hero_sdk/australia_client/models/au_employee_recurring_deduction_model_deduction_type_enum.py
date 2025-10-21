from enum import Enum


class AuEmployeeRecurringDeductionModelDeductionTypeEnum(str, Enum):
    CUSTOM = "Custom"
    FIXED = "Fixed"
    NOTSET = "NotSet"
    PERCENTAGEGROSS = "PercentageGross"
    PERCENTAGENET = "PercentageNet"
    PERCENTAGEOTE = "PercentageOTE"
    PERCENTAGESTUDENTLOAN = "PercentageStudentLoan"
    PERCENTAGESUPERANNUATION = "PercentageSuperannuation"
    TIERED = "Tiered"

    def __str__(self) -> str:
        return str(self.value)
