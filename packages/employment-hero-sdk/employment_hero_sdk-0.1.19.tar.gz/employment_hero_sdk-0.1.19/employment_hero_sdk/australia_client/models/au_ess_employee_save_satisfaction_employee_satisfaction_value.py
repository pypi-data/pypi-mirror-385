from enum import Enum


class AuEssEmployeeSaveSatisfactionEmployeeSatisfactionValue(str, Enum):
    HAPPY = "Happy"
    NEUTRAL = "Neutral"
    NOTSET = "NotSet"
    SAD = "Sad"

    def __str__(self) -> str:
        return str(self.value)
