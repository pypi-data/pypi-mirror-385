from enum import Enum


class EssEmployeeDetailsModelEmployeeDetailsEditMode(str, Enum):
    BUSINESSPORTAL = "BusinessPortal"
    EMPLOYEEPORTAL = "EmployeePortal"
    EMPLOYEEPORTALREADONLY = "EmployeePortalReadOnly"

    def __str__(self) -> str:
        return str(self.value)
