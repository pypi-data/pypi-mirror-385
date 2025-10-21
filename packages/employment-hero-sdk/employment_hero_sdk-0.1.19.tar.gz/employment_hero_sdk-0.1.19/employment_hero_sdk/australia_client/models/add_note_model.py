from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.add_note_model_time_attendance_shift_note_type import AddNoteModelTimeAttendanceShiftNoteType
from ..models.add_note_model_time_attendance_shift_note_visibility import AddNoteModelTimeAttendanceShiftNoteVisibility
from ..types import UNSET, Unset

T = TypeVar("T", bound="AddNoteModel")


@_attrs_define
class AddNoteModel:
    """
    Attributes:
        employee_id (Union[Unset, int]):
        type (Union[Unset, AddNoteModelTimeAttendanceShiftNoteType]):
        visibility (Union[Unset, AddNoteModelTimeAttendanceShiftNoteVisibility]):
        note (Union[Unset, str]):
        is_admin_initiated (Union[Unset, bool]):
    """

    employee_id: Union[Unset, int] = UNSET
    type: Union[Unset, AddNoteModelTimeAttendanceShiftNoteType] = UNSET
    visibility: Union[Unset, AddNoteModelTimeAttendanceShiftNoteVisibility] = UNSET
    note: Union[Unset, str] = UNSET
    is_admin_initiated: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        employee_id = self.employee_id

        type: Union[Unset, str] = UNSET
        if not isinstance(self.type, Unset):
            type = self.type.value

        visibility: Union[Unset, str] = UNSET
        if not isinstance(self.visibility, Unset):
            visibility = self.visibility.value

        note = self.note

        is_admin_initiated = self.is_admin_initiated

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if type is not UNSET:
            field_dict["type"] = type
        if visibility is not UNSET:
            field_dict["visibility"] = visibility
        if note is not UNSET:
            field_dict["note"] = note
        if is_admin_initiated is not UNSET:
            field_dict["isAdminInitiated"] = is_admin_initiated

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        employee_id = d.pop("employeeId", UNSET)

        _type = d.pop("type", UNSET)
        type: Union[Unset, AddNoteModelTimeAttendanceShiftNoteType]
        if isinstance(_type, Unset):
            type = UNSET
        else:
            type = AddNoteModelTimeAttendanceShiftNoteType(_type)

        _visibility = d.pop("visibility", UNSET)
        visibility: Union[Unset, AddNoteModelTimeAttendanceShiftNoteVisibility]
        if isinstance(_visibility, Unset):
            visibility = UNSET
        else:
            visibility = AddNoteModelTimeAttendanceShiftNoteVisibility(_visibility)

        note = d.pop("note", UNSET)

        is_admin_initiated = d.pop("isAdminInitiated", UNSET)

        add_note_model = cls(
            employee_id=employee_id,
            type=type,
            visibility=visibility,
            note=note,
            is_admin_initiated=is_admin_initiated,
        )

        add_note_model.additional_properties = d
        return add_note_model

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
