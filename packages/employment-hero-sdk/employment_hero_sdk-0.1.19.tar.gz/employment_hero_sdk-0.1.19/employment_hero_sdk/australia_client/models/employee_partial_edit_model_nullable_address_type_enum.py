from enum import Enum


class EmployeePartialEditModelNullableAddressTypeEnum(str, Enum):
    FOREIGNADDRESS = "ForeignAddress"
    LOCALADDRESS = "LocalAddress"
    LOCALCAREOFADDRESS = "LocalCareOfAddress"

    def __str__(self) -> str:
        return str(self.value)
