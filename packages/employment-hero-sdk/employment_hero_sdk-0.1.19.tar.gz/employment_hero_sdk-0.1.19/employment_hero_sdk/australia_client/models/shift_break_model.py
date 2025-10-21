import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.shift_break_model_nullable_time_attendance_shift_note_visibility import (
    ShiftBreakModelNullableTimeAttendanceShiftNoteVisibility,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.end_break_model import EndBreakModel
    from ..models.start_break_model import StartBreakModel


T = TypeVar("T", bound="ShiftBreakModel")


@_attrs_define
class ShiftBreakModel:
    """
    Attributes:
        start (Union[Unset, StartBreakModel]):
        end (Union[Unset, EndBreakModel]):
        is_paid_break (Union[Unset, bool]):
        employee_id (Union[Unset, int]):
        latitude (Union[Unset, float]):
        longitude (Union[Unset, float]):
        kiosk_id (Union[Unset, int]):
        ip_address (Union[Unset, str]):
        image (Union[Unset, str]):
        is_admin_initiated (Union[Unset, bool]):
        recorded_time_utc (Union[Unset, datetime.datetime]):
        utc_offset (Union[Unset, str]):
        note_visibility (Union[Unset, ShiftBreakModelNullableTimeAttendanceShiftNoteVisibility]):
    """

    start: Union[Unset, "StartBreakModel"] = UNSET
    end: Union[Unset, "EndBreakModel"] = UNSET
    is_paid_break: Union[Unset, bool] = UNSET
    employee_id: Union[Unset, int] = UNSET
    latitude: Union[Unset, float] = UNSET
    longitude: Union[Unset, float] = UNSET
    kiosk_id: Union[Unset, int] = UNSET
    ip_address: Union[Unset, str] = UNSET
    image: Union[Unset, str] = UNSET
    is_admin_initiated: Union[Unset, bool] = UNSET
    recorded_time_utc: Union[Unset, datetime.datetime] = UNSET
    utc_offset: Union[Unset, str] = UNSET
    note_visibility: Union[Unset, ShiftBreakModelNullableTimeAttendanceShiftNoteVisibility] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        start: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.start, Unset):
            start = self.start.to_dict()

        end: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.end, Unset):
            end = self.end.to_dict()

        is_paid_break = self.is_paid_break

        employee_id = self.employee_id

        latitude = self.latitude

        longitude = self.longitude

        kiosk_id = self.kiosk_id

        ip_address = self.ip_address

        image = self.image

        is_admin_initiated = self.is_admin_initiated

        recorded_time_utc: Union[Unset, str] = UNSET
        if not isinstance(self.recorded_time_utc, Unset):
            recorded_time_utc = self.recorded_time_utc.isoformat()

        utc_offset = self.utc_offset

        note_visibility: Union[Unset, str] = UNSET
        if not isinstance(self.note_visibility, Unset):
            note_visibility = self.note_visibility.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if start is not UNSET:
            field_dict["start"] = start
        if end is not UNSET:
            field_dict["end"] = end
        if is_paid_break is not UNSET:
            field_dict["isPaidBreak"] = is_paid_break
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if latitude is not UNSET:
            field_dict["latitude"] = latitude
        if longitude is not UNSET:
            field_dict["longitude"] = longitude
        if kiosk_id is not UNSET:
            field_dict["kioskId"] = kiosk_id
        if ip_address is not UNSET:
            field_dict["ipAddress"] = ip_address
        if image is not UNSET:
            field_dict["image"] = image
        if is_admin_initiated is not UNSET:
            field_dict["isAdminInitiated"] = is_admin_initiated
        if recorded_time_utc is not UNSET:
            field_dict["recordedTimeUtc"] = recorded_time_utc
        if utc_offset is not UNSET:
            field_dict["utcOffset"] = utc_offset
        if note_visibility is not UNSET:
            field_dict["noteVisibility"] = note_visibility

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.end_break_model import EndBreakModel
        from ..models.start_break_model import StartBreakModel

        d = src_dict.copy()
        _start = d.pop("start", UNSET)
        start: Union[Unset, StartBreakModel]
        if isinstance(_start, Unset):
            start = UNSET
        else:
            start = StartBreakModel.from_dict(_start)

        _end = d.pop("end", UNSET)
        end: Union[Unset, EndBreakModel]
        if isinstance(_end, Unset):
            end = UNSET
        else:
            end = EndBreakModel.from_dict(_end)

        is_paid_break = d.pop("isPaidBreak", UNSET)

        employee_id = d.pop("employeeId", UNSET)

        latitude = d.pop("latitude", UNSET)

        longitude = d.pop("longitude", UNSET)

        kiosk_id = d.pop("kioskId", UNSET)

        ip_address = d.pop("ipAddress", UNSET)

        image = d.pop("image", UNSET)

        is_admin_initiated = d.pop("isAdminInitiated", UNSET)

        _recorded_time_utc = d.pop("recordedTimeUtc", UNSET)
        recorded_time_utc: Union[Unset, datetime.datetime]
        if isinstance(_recorded_time_utc, Unset):
            recorded_time_utc = UNSET
        else:
            recorded_time_utc = isoparse(_recorded_time_utc)

        utc_offset = d.pop("utcOffset", UNSET)

        _note_visibility = d.pop("noteVisibility", UNSET)
        note_visibility: Union[Unset, ShiftBreakModelNullableTimeAttendanceShiftNoteVisibility]
        if isinstance(_note_visibility, Unset):
            note_visibility = UNSET
        else:
            note_visibility = ShiftBreakModelNullableTimeAttendanceShiftNoteVisibility(_note_visibility)

        shift_break_model = cls(
            start=start,
            end=end,
            is_paid_break=is_paid_break,
            employee_id=employee_id,
            latitude=latitude,
            longitude=longitude,
            kiosk_id=kiosk_id,
            ip_address=ip_address,
            image=image,
            is_admin_initiated=is_admin_initiated,
            recorded_time_utc=recorded_time_utc,
            utc_offset=utc_offset,
            note_visibility=note_visibility,
        )

        shift_break_model.additional_properties = d
        return shift_break_model

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
