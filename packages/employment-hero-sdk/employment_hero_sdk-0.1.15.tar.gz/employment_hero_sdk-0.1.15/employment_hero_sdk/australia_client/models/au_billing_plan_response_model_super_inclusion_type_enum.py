from enum import Enum


class AuBillingPlanResponseModelSuperInclusionTypeEnum(str, Enum):
    MONTHLY = "Monthly"
    NONE = "None"
    QUARTERLY = "Quarterly"
    WEEKLY = "Weekly"

    def __str__(self) -> str:
        return str(self.value)
