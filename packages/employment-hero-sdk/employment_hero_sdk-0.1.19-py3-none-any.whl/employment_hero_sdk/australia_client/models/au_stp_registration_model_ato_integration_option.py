from enum import Enum


class AuStpRegistrationModelAtoIntegrationOption(str, Enum):
    ACCESSMANAGER = "AccessManager"
    NONE = "None"
    PHONE = "Phone"

    def __str__(self) -> str:
        return str(self.value)
