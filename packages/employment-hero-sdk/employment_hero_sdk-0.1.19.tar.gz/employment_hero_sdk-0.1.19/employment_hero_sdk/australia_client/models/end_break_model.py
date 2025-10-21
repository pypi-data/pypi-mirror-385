import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.end_break_model_nullable_time_attendance_shift_note_visibility import (
    EndBreakModelNullableTimeAttendanceShiftNoteVisibility,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="EndBreakModel")


@_attrs_define
class EndBreakModel:
    """
    Attributes:
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
        note_visibility (Union[Unset, EndBreakModelNullableTimeAttendanceShiftNoteVisibility]):
    """

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
    note_visibility: Union[Unset, EndBreakModelNullableTimeAttendanceShiftNoteVisibility] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
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
        d = src_dict.copy()
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
        note_visibility: Union[Unset, EndBreakModelNullableTimeAttendanceShiftNoteVisibility]
        if isinstance(_note_visibility, Unset):
            note_visibility = UNSET
        else:
            note_visibility = EndBreakModelNullableTimeAttendanceShiftNoteVisibility(_note_visibility)

        end_break_model = cls(
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

        end_break_model.additional_properties = d
        return end_break_model

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
