from enum import Enum


class SaveLeaveAccrualModelSaveLeaveAccrualTypeEnum(str, Enum):
    LEAVEACCRUED = "LeaveAccrued"
    LEAVEADJUSTMENT = "LeaveAdjustment"
    LEAVETAKEN = "LeaveTaken"

    def __str__(self) -> str:
        return str(self.value)
