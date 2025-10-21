from enum import Enum


class EmployeePartialEditModelEmployeeStarterTypeEnum(str, Enum):
    NEWSTARTER = "NewStarter"
    REPORTEDHMRC = "ReportedHmrc"

    def __str__(self) -> str:
        return str(self.value)
