from enum import Enum


class IEdmTermEdmTermKind(str, Enum):
    NONE = "None"
    TYPE = "Type"
    VALUE = "Value"

    def __str__(self) -> str:
        return str(self.value)
