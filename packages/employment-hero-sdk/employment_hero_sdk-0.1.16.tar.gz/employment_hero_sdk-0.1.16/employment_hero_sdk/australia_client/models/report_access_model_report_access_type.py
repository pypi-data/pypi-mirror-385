from enum import Enum


class ReportAccessModelReportAccessType(str, Enum):
    ALLREPORTS = "AllReports"
    NONE = "None"
    REPORTPACK = "ReportPack"
    SPECIFICREPORTS = "SpecificReports"

    def __str__(self) -> str:
        return str(self.value)
