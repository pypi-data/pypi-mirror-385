from enum import Enum


class AuEditBusinessPaySlipApiModelPaySlipSuperContributionProcessingFrequencyTextOption(str, Enum):
    MONTHLY = "Monthly"
    NONE = "None"
    QUARTERLY = "Quarterly"

    def __str__(self) -> str:
        return str(self.value)
