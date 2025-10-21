from enum import Enum


class EmploymentAgreementModelPayRateTemplateTypeEnum(str, Enum):
    ANNIVERSARY = "Anniversary"
    ANNIVERSARYINMONTHS = "AnniversaryInMonths"
    DATEOFBIRTH = "DateOfBirth"
    DATEOFBIRTHANDANNIVERSARYINMONTHS = "DateOfBirthAndAnniversaryInMonths"

    def __str__(self) -> str:
        return str(self.value)
