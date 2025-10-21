import datetime
from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.clock_on_model_nullable_time_attendance_shift_note_visibility import (
    ClockOnModelNullableTimeAttendanceShiftNoteVisibility,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="ClockOnModel")


@_attrs_define
class ClockOnModel:
    """
    Attributes:
        location_id (Union[Unset, int]):
        classification_id (Union[Unset, int]):
        work_type_id (Union[Unset, int]):
        shift_condition_ids (Union[Unset, List[int]]):
        note (Union[Unset, str]):
        dimension_value_ids (Union[Unset, List[int]]):
        employee_id (Union[Unset, int]):
        latitude (Union[Unset, float]):
        longitude (Union[Unset, float]):
        kiosk_id (Union[Unset, int]):
        ip_address (Union[Unset, str]):
        image (Union[Unset, str]):
        is_admin_initiated (Union[Unset, bool]):
        recorded_time_utc (Union[Unset, datetime.datetime]):
        utc_offset (Union[Unset, str]):
        note_visibility (Union[Unset, ClockOnModelNullableTimeAttendanceShiftNoteVisibility]):
    """

    location_id: Union[Unset, int] = UNSET
    classification_id: Union[Unset, int] = UNSET
    work_type_id: Union[Unset, int] = UNSET
    shift_condition_ids: Union[Unset, List[int]] = UNSET
    note: Union[Unset, str] = UNSET
    dimension_value_ids: Union[Unset, List[int]] = UNSET
    employee_id: Union[Unset, int] = UNSET
    latitude: Union[Unset, float] = UNSET
    longitude: Union[Unset, float] = UNSET
    kiosk_id: Union[Unset, int] = UNSET
    ip_address: Union[Unset, str] = UNSET
    image: Union[Unset, str] = UNSET
    is_admin_initiated: Union[Unset, bool] = UNSET
    recorded_time_utc: Union[Unset, datetime.datetime] = UNSET
    utc_offset: Union[Unset, str] = UNSET
    note_visibility: Union[Unset, ClockOnModelNullableTimeAttendanceShiftNoteVisibility] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        location_id = self.location_id

        classification_id = self.classification_id

        work_type_id = self.work_type_id

        shift_condition_ids: Union[Unset, List[int]] = UNSET
        if not isinstance(self.shift_condition_ids, Unset):
            shift_condition_ids = self.shift_condition_ids

        note = self.note

        dimension_value_ids: Union[Unset, List[int]] = UNSET
        if not isinstance(self.dimension_value_ids, Unset):
            dimension_value_ids = self.dimension_value_ids

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
        if location_id is not UNSET:
            field_dict["locationId"] = location_id
        if classification_id is not UNSET:
            field_dict["classificationId"] = classification_id
        if work_type_id is not UNSET:
            field_dict["workTypeId"] = work_type_id
        if shift_condition_ids is not UNSET:
            field_dict["shiftConditionIds"] = shift_condition_ids
        if note is not UNSET:
            field_dict["note"] = note
        if dimension_value_ids is not UNSET:
            field_dict["dimensionValueIds"] = dimension_value_ids
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
        location_id = d.pop("locationId", UNSET)

        classification_id = d.pop("classificationId", UNSET)

        work_type_id = d.pop("workTypeId", UNSET)

        shift_condition_ids = cast(List[int], d.pop("shiftConditionIds", UNSET))

        note = d.pop("note", UNSET)

        dimension_value_ids = cast(List[int], d.pop("dimensionValueIds", UNSET))

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
        note_visibility: Union[Unset, ClockOnModelNullableTimeAttendanceShiftNoteVisibility]
        if isinstance(_note_visibility, Unset):
            note_visibility = UNSET
        else:
            note_visibility = ClockOnModelNullableTimeAttendanceShiftNoteVisibility(_note_visibility)

        clock_on_model = cls(
            location_id=location_id,
            classification_id=classification_id,
            work_type_id=work_type_id,
            shift_condition_ids=shift_condition_ids,
            note=note,
            dimension_value_ids=dimension_value_ids,
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

        clock_on_model.additional_properties = d
        return clock_on_model

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
