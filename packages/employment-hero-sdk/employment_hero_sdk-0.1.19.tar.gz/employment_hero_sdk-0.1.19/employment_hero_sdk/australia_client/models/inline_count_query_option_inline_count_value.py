from enum import Enum


class InlineCountQueryOptionInlineCountValue(str, Enum):
    ALLPAGES = "AllPages"
    NONE = "None"

    def __str__(self) -> str:
        return str(self.value)
