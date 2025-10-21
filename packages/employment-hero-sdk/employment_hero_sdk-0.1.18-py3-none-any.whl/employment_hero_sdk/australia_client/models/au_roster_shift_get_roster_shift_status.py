from enum import Enum


class AuRosterShiftGetRosterShiftStatus(str, Enum):
    ACCEPTED = "Accepted"
    ALL = "All"
    PUBLISHED = "Published"
    UNPUBLISHED = "Unpublished"

    def __str__(self) -> str:
        return str(self.value)
