from enum import Enum


class TimesheetRoundingRulesModelRoundingDirectionEnum(str, Enum):
    DOWN = "Down"
    NONE = "None"
    TOTHENEAREST = "ToTheNearest"
    UP = "Up"

    def __str__(self) -> str:
        return str(self.value)
