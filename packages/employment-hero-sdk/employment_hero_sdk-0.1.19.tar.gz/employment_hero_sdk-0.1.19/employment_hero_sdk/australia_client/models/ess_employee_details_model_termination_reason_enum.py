from enum import Enum


class EssEmployeeDetailsModelTerminationReasonEnum(str, Enum):
    CONTRACTCESSATION = "ContractCessation"
    DECEASED = "Deceased"
    DISMISSAL = "Dismissal"
    ILLHEALTH = "IllHealth"
    OTHER = "Other"
    REDUNDANCY = "Redundancy"
    TRANSFER = "Transfer"
    VOLUNTARYCESSATION = "VoluntaryCessation"

    def __str__(self) -> str:
        return str(self.value)
