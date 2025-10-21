from enum import Enum


class AuBillingPlanResponseModelFunctionToggle(str, Enum):
    COMINGSOON = "ComingSoon"
    DISABLED = "Disabled"
    ENABLED = "Enabled"
    UPSELL = "Upsell"

    def __str__(self) -> str:
        return str(self.value)
