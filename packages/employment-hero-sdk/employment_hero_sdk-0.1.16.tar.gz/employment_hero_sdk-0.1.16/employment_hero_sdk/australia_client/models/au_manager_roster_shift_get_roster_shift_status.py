from enum import Enum


class AuManagerRosterShiftGetRosterShiftStatus(str, Enum):
    ACCEPTED = "Accepted"
    ALL = "All"
    PUBLISHED = "Published"
    UNPUBLISHED = "Unpublished"

    def __str__(self) -> str:
        return str(self.value)
