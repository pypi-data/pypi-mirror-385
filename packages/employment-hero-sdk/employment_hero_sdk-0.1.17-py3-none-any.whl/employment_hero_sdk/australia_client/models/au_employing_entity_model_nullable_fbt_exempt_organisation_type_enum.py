from enum import Enum


class AuEmployingEntityModelNullableFbtExemptOrganisationTypeEnum(str, Enum):
    COMMUNITYBENEFIT = "CommunityBenefit"
    EDUCATIONADVANCEMENT = "EducationAdvancement"
    HEALTHPROMOTIONCHARITY = "HealthPromotionCharity"
    POVERTYRELIEF = "PovertyRelief"
    PUBLICAMBULANCESERVICE = "PublicAmbulanceService"
    PUBLICANDNONPROFITHOSPITAL = "PublicAndNonProfitHospital"
    PUBLICBENEVOLENTINSTITUTION = "PublicBenevolentInstitution"
    RELIGIONADVANCEMENT = "ReligionAdvancement"

    def __str__(self) -> str:
        return str(self.value)
