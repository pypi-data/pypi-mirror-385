from enum import Enum


class AuRosterShiftGetFilterShiftStatus(str, Enum):
    ACCEPTED = "Accepted"
    ALL = "All"
    PUBLISHED = "Published"
    UNPUBLISHED = "Unpublished"

    def __str__(self) -> str:
        return str(self.value)
