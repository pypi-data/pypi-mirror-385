from enum import Enum


class DeviceTokenModelMobilePlatform(str, Enum):
    ANDROID = "Android"
    IOS = "iOS"

    def __str__(self) -> str:
        return str(self.value)
