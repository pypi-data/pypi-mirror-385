from enum import Enum


class BasicKioskEmployeeModelTimeAttendanceStatus(str, Enum):
    CLOCKEDOFF = "ClockedOff"
    CLOCKEDON = "ClockedOn"
    NOTCLOCKEDON = "NotClockedOn"
    ONBREAK = "OnBreak"

    def __str__(self) -> str:
        return str(self.value)
