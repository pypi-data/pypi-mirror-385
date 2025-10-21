from enum import Enum


class BusinessAccessListModelRelatedUserType(str, Enum):
    RESTRICTED = "Restricted"
    UNRESTRICTED = "Unrestricted"

    def __str__(self) -> str:
        return str(self.value)
