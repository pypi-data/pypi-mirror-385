from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.get_shift_notes_model_nullable_time_attendance_shift_note_type import (
    GetShiftNotesModelNullableTimeAttendanceShiftNoteType,
)
from ..models.get_shift_notes_model_nullable_time_attendance_shift_note_visibility import (
    GetShiftNotesModelNullableTimeAttendanceShiftNoteVisibility,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="GetShiftNotesModel")


@_attrs_define
class GetShiftNotesModel:
    """
    Attributes:
        employee_id (Union[Unset, int]):
        is_admin_initiated (Union[Unset, bool]):
        type (Union[Unset, GetShiftNotesModelNullableTimeAttendanceShiftNoteType]):
        visibility (Union[Unset, GetShiftNotesModelNullableTimeAttendanceShiftNoteVisibility]):
    """

    employee_id: Union[Unset, int] = UNSET
    is_admin_initiated: Union[Unset, bool] = UNSET
    type: Union[Unset, GetShiftNotesModelNullableTimeAttendanceShiftNoteType] = UNSET
    visibility: Union[Unset, GetShiftNotesModelNullableTimeAttendanceShiftNoteVisibility] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        employee_id = self.employee_id

        is_admin_initiated = self.is_admin_initiated

        type: Union[Unset, str] = UNSET
        if not isinstance(self.type, Unset):
            type = self.type.value

        visibility: Union[Unset, str] = UNSET
        if not isinstance(self.visibility, Unset):
            visibility = self.visibility.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if is_admin_initiated is not UNSET:
            field_dict["isAdminInitiated"] = is_admin_initiated
        if type is not UNSET:
            field_dict["type"] = type
        if visibility is not UNSET:
            field_dict["visibility"] = visibility

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        employee_id = d.pop("employeeId", UNSET)

        is_admin_initiated = d.pop("isAdminInitiated", UNSET)

        _type = d.pop("type", UNSET)
        type: Union[Unset, GetShiftNotesModelNullableTimeAttendanceShiftNoteType]
        if isinstance(_type, Unset):
            type = UNSET
        else:
            type = GetShiftNotesModelNullableTimeAttendanceShiftNoteType(_type)

        _visibility = d.pop("visibility", UNSET)
        visibility: Union[Unset, GetShiftNotesModelNullableTimeAttendanceShiftNoteVisibility]
        if isinstance(_visibility, Unset):
            visibility = UNSET
        else:
            visibility = GetShiftNotesModelNullableTimeAttendanceShiftNoteVisibility(_visibility)

        get_shift_notes_model = cls(
            employee_id=employee_id,
            is_admin_initiated=is_admin_initiated,
            type=type,
            visibility=visibility,
        )

        get_shift_notes_model.additional_properties = d
        return get_shift_notes_model

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
