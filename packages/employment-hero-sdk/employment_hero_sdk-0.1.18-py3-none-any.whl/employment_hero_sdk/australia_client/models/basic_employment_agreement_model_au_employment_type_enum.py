from enum import Enum


class BasicEmploymentAgreementModelAuEmploymentTypeEnum(str, Enum):
    CASUAL = "Casual"
    FULLTIME = "FullTime"
    LABOURHIRE = "LabourHire"
    PARTTIME = "PartTime"
    SUPERANNUATIONINCOMESTREAM = "SuperannuationIncomeStream"
    UNKNOWN = "Unknown"

    def __str__(self) -> str:
        return str(self.value)
