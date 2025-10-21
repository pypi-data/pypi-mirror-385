from enum import Enum


class SubmitPayRunDeductionRequestIdType(str, Enum):
    EXTERNAL = "External"
    STANDARD = "Standard"

    def __str__(self) -> str:
        return str(self.value)
