from enum import Enum


class AuEmployeePortalSettingsModelESSTimesheetSettingModelEnum(str, Enum):
    DISABLED = "Disabled"
    EDITKIOSK = "EditKiosk"
    EDITKIOSKORWORKZONECLOCKONOFF = "EditKioskOrWorkZoneClockOnOff"
    EDITWORKZONECLOCKONOFF = "EditWorkZoneClockOnOff"
    ENABLED = "Enabled"
    READONLY = "ReadOnly"
    READWRITE = "ReadWrite"

    def __str__(self) -> str:
        return str(self.value)
