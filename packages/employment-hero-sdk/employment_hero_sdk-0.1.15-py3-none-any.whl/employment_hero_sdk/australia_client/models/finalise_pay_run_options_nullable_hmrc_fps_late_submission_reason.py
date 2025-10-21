from enum import Enum


class FinalisePayRunOptionsNullableHmrcFpsLateSubmissionReason(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"
    G = "G"
    H = "H"

    def __str__(self) -> str:
        return str(self.value)
