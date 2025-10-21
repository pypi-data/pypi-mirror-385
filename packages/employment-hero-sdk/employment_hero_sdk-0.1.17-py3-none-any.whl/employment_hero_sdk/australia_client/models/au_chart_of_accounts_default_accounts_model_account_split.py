from enum import Enum


class AuChartOfAccountsDefaultAccountsModelAccountSplit(str, Enum):
    EMPLOYINGENTITY = "EmployingEntity"
    LOCATION = "Location"
    NONE = "None"

    def __str__(self) -> str:
        return str(self.value)
