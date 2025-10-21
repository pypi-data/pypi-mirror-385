from enum import Enum


class AuPayScheduleModelNullablePayRunEmployeeSelectionStrategy(str, Enum):
    ACTIVESUBCONTRACTORS = "ActiveSubcontractors"
    EMPLOYINGENTITY = "EmployingEntity"
    NONE = "None"
    PAYRUNDEFAULT = "PayRunDefault"
    PAYRUNDEFAULTWITHTIMESHEETS = "PayRunDefaultWithTimesheets"
    TIMESHEETLOCATIONS = "TimesheetLocations"

    def __str__(self) -> str:
        return str(self.value)
