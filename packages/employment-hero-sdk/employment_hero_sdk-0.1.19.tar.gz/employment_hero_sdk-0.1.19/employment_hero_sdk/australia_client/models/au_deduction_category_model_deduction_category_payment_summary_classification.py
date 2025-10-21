from enum import Enum


class AuDeductionCategoryModelDeductionCategoryPaymentSummaryClassification(str, Enum):
    CHILDSUPPORTDEDUCTION = "ChildSupportDeduction"
    CHILDSUPPORTGARNISHEE = "ChildSupportGarnishee"
    DEFAULT = "Default"
    SALARYSACRIFICEOTHEREMPLOYEEBENEFITS = "SalarySacrificeOtherEmployeeBenefits"
    SALARYSACRIFICESUPERANNUATION = "SalarySacrificeSuperannuation"
    UNIONORPROFESSIONALASSOCIATIONFEES = "UnionOrProfessionalAssociationFees"
    WORKPLACEGIVING = "WorkplaceGiving"

    def __str__(self) -> str:
        return str(self.value)
