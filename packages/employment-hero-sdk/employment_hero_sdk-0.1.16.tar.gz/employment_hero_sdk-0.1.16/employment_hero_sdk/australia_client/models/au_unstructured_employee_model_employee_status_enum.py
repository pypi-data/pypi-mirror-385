from enum import Enum


class AuUnstructuredEmployeeModelEmployeeStatusEnum(str, Enum):
    ACTIVE = "Active"
    INCOMPLETE = "Incomplete"
    TERMINATED = "Terminated"

    def __str__(self) -> str:
        return str(self.value)
