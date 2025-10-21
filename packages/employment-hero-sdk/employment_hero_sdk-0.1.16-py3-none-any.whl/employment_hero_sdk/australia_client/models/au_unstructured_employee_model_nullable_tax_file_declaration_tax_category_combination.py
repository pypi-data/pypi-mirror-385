from enum import Enum


class AuUnstructuredEmployeeModelNullableTaxFileDeclarationTaxCategoryCombination(str, Enum):
    ACTOR_LIMITEDPERFORMANCEPERWEEK = "Actor_LimitedPerformancePerWeek"
    ACTOR_NOTAXFREETHRESHOLD = "Actor_NoTaxFreeThreshold"
    ACTOR_PROMOTIONAL = "Actor_Promotional"
    ACTOR_WITHTAXFREETHRESHOLD = "Actor_WithTaxFreeThreshold"
    ATODEFINED_DEATHBENEFICIARY = "ATODefined_DeathBeneficiary"
    ATODEFINED_DOWNWARDVARIATION = "ATODefined_DownwardVariation"
    ATODEFINED_NONEMPLOYEE = "ATODefined_NonEmployee"
    DAILYCASUAL = "DailyCasual"
    HORTICULTURALISTSHEARER_FOREIGNRESIDENT = "HorticulturalistShearer_ForeignResident"
    HORTICULTURALISTSHEARER_WITHTAXFREETHRESHOLD = "HorticulturalistShearer_WithTaxFreeThreshold"
    SENIORPENSIONER_MARRIED = "SeniorPensioner_Married"
    SENIORPENSIONER_SEPARATEDCOUPLEILLNESS = "SeniorPensioner_SeparatedCoupleIllness"
    SENIORPENSIONER_SINGLE = "SeniorPensioner_Single"

    def __str__(self) -> str:
        return str(self.value)
