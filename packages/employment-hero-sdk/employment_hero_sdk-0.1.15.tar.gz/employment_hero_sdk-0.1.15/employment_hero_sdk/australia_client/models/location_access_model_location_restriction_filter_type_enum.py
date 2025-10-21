from enum import Enum


class LocationAccessModelLocationRestrictionFilterTypeEnum(str, Enum):
    LOCATION = "Location"
    LOCATIONORPARENTS = "LocationOrParents"

    def __str__(self) -> str:
        return str(self.value)
