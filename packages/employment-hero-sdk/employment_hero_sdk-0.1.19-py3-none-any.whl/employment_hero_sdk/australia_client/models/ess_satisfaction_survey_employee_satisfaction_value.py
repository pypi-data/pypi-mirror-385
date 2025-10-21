from enum import Enum


class EssSatisfactionSurveyEmployeeSatisfactionValue(str, Enum):
    HAPPY = "Happy"
    NEUTRAL = "Neutral"
    NOTSET = "NotSet"
    SAD = "Sad"

    def __str__(self) -> str:
        return str(self.value)
