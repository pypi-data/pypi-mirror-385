from enum import Enum


class PayRunInclusionsReportRequestModelPayRunInclusionsStatus(str, Enum):
    ACTIVE = "Active"
    ALL = "All"
    EXPIRED = "Expired"

    def __str__(self) -> str:
        return str(self.value)
