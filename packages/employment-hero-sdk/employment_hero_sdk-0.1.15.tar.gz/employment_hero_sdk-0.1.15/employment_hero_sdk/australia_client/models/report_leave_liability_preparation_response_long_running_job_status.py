from enum import Enum


class ReportLeaveLiabilityPreparationResponseLongRunningJobStatus(str, Enum):
    CANCELLED = "Cancelled"
    COMPLETE = "Complete"
    FAILED = "Failed"
    QUEUED = "Queued"
    RUNNING = "Running"

    def __str__(self) -> str:
        return str(self.value)
