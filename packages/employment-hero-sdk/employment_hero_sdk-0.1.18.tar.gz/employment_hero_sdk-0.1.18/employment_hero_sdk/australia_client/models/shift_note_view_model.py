import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.shift_note_view_model_time_attendance_shift_note_type import ShiftNoteViewModelTimeAttendanceShiftNoteType
from ..models.shift_note_view_model_time_attendance_shift_note_visibility import (
    ShiftNoteViewModelTimeAttendanceShiftNoteVisibility,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.employee_view_model import EmployeeViewModel


T = TypeVar("T", bound="ShiftNoteViewModel")


@_attrs_define
class ShiftNoteViewModel:
    """
    Attributes:
        id (Union[Unset, int]):
        employee (Union[Unset, EmployeeViewModel]):
        date (Union[Unset, datetime.datetime]):
        type (Union[Unset, ShiftNoteViewModelTimeAttendanceShiftNoteType]):
        note (Union[Unset, str]):
        note_id (Union[Unset, int]):
        visibility (Union[Unset, ShiftNoteViewModelTimeAttendanceShiftNoteVisibility]):
        read (Union[Unset, bool]):
        created_by_admin (Union[Unset, bool]):
    """

    id: Union[Unset, int] = UNSET
    employee: Union[Unset, "EmployeeViewModel"] = UNSET
    date: Union[Unset, datetime.datetime] = UNSET
    type: Union[Unset, ShiftNoteViewModelTimeAttendanceShiftNoteType] = UNSET
    note: Union[Unset, str] = UNSET
    note_id: Union[Unset, int] = UNSET
    visibility: Union[Unset, ShiftNoteViewModelTimeAttendanceShiftNoteVisibility] = UNSET
    read: Union[Unset, bool] = UNSET
    created_by_admin: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        employee: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.employee, Unset):
            employee = self.employee.to_dict()

        date: Union[Unset, str] = UNSET
        if not isinstance(self.date, Unset):
            date = self.date.isoformat()

        type: Union[Unset, str] = UNSET
        if not isinstance(self.type, Unset):
            type = self.type.value

        note = self.note

        note_id = self.note_id

        visibility: Union[Unset, str] = UNSET
        if not isinstance(self.visibility, Unset):
            visibility = self.visibility.value

        read = self.read

        created_by_admin = self.created_by_admin

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if employee is not UNSET:
            field_dict["employee"] = employee
        if date is not UNSET:
            field_dict["date"] = date
        if type is not UNSET:
            field_dict["type"] = type
        if note is not UNSET:
            field_dict["note"] = note
        if note_id is not UNSET:
            field_dict["noteId"] = note_id
        if visibility is not UNSET:
            field_dict["visibility"] = visibility
        if read is not UNSET:
            field_dict["read"] = read
        if created_by_admin is not UNSET:
            field_dict["createdByAdmin"] = created_by_admin

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.employee_view_model import EmployeeViewModel

        d = src_dict.copy()
        id = d.pop("id", UNSET)

        _employee = d.pop("employee", UNSET)
        employee: Union[Unset, EmployeeViewModel]
        if isinstance(_employee, Unset):
            employee = UNSET
        else:
            employee = EmployeeViewModel.from_dict(_employee)

        _date = d.pop("date", UNSET)
        date: Union[Unset, datetime.datetime]
        if isinstance(_date, Unset):
            date = UNSET
        else:
            date = isoparse(_date)

        _type = d.pop("type", UNSET)
        type: Union[Unset, ShiftNoteViewModelTimeAttendanceShiftNoteType]
        if isinstance(_type, Unset):
            type = UNSET
        else:
            type = ShiftNoteViewModelTimeAttendanceShiftNoteType(_type)

        note = d.pop("note", UNSET)

        note_id = d.pop("noteId", UNSET)

        _visibility = d.pop("visibility", UNSET)
        visibility: Union[Unset, ShiftNoteViewModelTimeAttendanceShiftNoteVisibility]
        if isinstance(_visibility, Unset):
            visibility = UNSET
        else:
            visibility = ShiftNoteViewModelTimeAttendanceShiftNoteVisibility(_visibility)

        read = d.pop("read", UNSET)

        created_by_admin = d.pop("createdByAdmin", UNSET)

        shift_note_view_model = cls(
            id=id,
            employee=employee,
            date=date,
            type=type,
            note=note,
            note_id=note_id,
            visibility=visibility,
            read=read,
            created_by_admin=created_by_admin,
        )

        shift_note_view_model.additional_properties = d
        return shift_note_view_model

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
