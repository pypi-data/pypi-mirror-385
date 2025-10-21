from enum import Enum


class AuFeaturesModelESSTimesheetSetting(str, Enum):
    DISABLED = "Disabled"
    EDITKIOSK = "EditKiosk"
    EDITWORKZONECLOCKONOFF = "EditWorkZoneClockOnOff"
    READONLY = "ReadOnly"
    READWRITE = "ReadWrite"

    def __str__(self) -> str:
        return str(self.value)
