from enum import Enum


class SingleSignOnRequestModelNavigationDisplayEnum(str, Enum):
    FULL = "Full"
    HIDEINTERNALPAGENAV = "HideInternalPageNav"
    NONE = "None"
    PRIMARY = "Primary"
    SECONDARY = "Secondary"

    def __str__(self) -> str:
        return str(self.value)
