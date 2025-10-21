from enum import Enum


class AuEmployeeFilterModelAuFilterTypeEnum(str, Enum):
    EMPLOYEE = "Employee"
    EMPLOYINGENTITY = "EmployingEntity"
    EMPLOYMENTTYPE = "EmploymentType"
    LOCATION = "Location"
    LOCATIONORPARENTS = "LocationOrParents"
    PAYSCHEDULE = "PaySchedule"
    TAG = "Tag"

    def __str__(self) -> str:
        return str(self.value)
