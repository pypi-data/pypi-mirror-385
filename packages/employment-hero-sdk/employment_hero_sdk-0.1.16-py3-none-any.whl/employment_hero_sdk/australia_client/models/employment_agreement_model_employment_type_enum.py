from enum import Enum


class EmploymentAgreementModelEmploymentTypeEnum(str, Enum):
    CASUAL = "Casual"
    CONTRACT = "Contract"
    FULLTIME = "FullTime"
    INDEPENDENTCONTRACTOR = "IndependentContractor"
    INTERN = "Intern"
    LABOURHIRE = "LabourHire"
    MANAGEMENT = "Management"
    NOTAPPLICABLE = "NotApplicable"
    OTHER = "Other"
    PARTTIME = "PartTime"
    SUPERANNUATIONINCOMESTREAM = "SuperannuationIncomeStream"
    UNKNOWN = "Unknown"

    def __str__(self) -> str:
        return str(self.value)
