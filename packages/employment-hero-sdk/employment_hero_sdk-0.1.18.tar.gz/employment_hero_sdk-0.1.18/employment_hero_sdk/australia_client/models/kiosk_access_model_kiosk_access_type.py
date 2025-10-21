from enum import Enum


class KioskAccessModelKioskAccessType(str, Enum):
    ALLKIOSKS = "AllKiosks"
    NONE = "None"
    SPECIFICKIOSKS = "SpecificKiosks"

    def __str__(self) -> str:
        return str(self.value)
