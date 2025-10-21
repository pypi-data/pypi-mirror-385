from enum import Enum


class AuUnstructuredEmployeeModelNullableMedicareLevySurchargeWithholdingTier(str, Enum):
    TIER1 = "Tier1"
    TIER2 = "Tier2"
    TIER3 = "Tier3"

    def __str__(self) -> str:
        return str(self.value)
