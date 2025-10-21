from enum import Enum


class PayRunCreateRequestNullableTimesheetImportOption(str, Enum):
    ALLOUTSTANDING = "AllOutstanding"
    CUSTOMPERIOD = "CustomPeriod"
    NONE = "None"
    THISPAYPERIOD = "ThisPayPeriod"

    def __str__(self) -> str:
        return str(self.value)
