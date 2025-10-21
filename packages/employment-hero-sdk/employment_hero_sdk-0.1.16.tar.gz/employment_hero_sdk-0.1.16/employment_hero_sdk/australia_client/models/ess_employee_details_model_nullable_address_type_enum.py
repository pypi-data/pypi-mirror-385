from enum import Enum


class EssEmployeeDetailsModelNullableAddressTypeEnum(str, Enum):
    FOREIGNADDRESS = "ForeignAddress"
    LOCALADDRESS = "LocalAddress"
    LOCALCAREOFADDRESS = "LocalCareOfAddress"

    def __str__(self) -> str:
        return str(self.value)
