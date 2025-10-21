from enum import Enum


class PayRunFinaliseDefaultSettingsModelPayRunFinaliseActionTimeline(str, Enum):
    AFTER = "After"
    BEFORE = "Before"
    ON = "On"

    def __str__(self) -> str:
        return str(self.value)
