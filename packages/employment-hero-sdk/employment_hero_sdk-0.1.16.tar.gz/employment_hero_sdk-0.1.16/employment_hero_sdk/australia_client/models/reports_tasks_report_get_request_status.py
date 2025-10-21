from enum import Enum


class ReportsTasksReportGetRequestStatus(str, Enum):
    ALL = "All"
    COMPLETED = "Completed"
    NOTCOMPLETED = "NotCompleted"

    def __str__(self) -> str:
        return str(self.value)
