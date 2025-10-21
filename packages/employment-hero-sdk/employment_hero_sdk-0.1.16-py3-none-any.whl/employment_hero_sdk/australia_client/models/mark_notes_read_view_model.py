from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="MarkNotesReadViewModel")


@_attrs_define
class MarkNotesReadViewModel:
    """
    Attributes:
        employee_id (Union[Unset, int]):
        note_ids (Union[Unset, List[int]]):
        read (Union[Unset, bool]):
    """

    employee_id: Union[Unset, int] = UNSET
    note_ids: Union[Unset, List[int]] = UNSET
    read: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        employee_id = self.employee_id

        note_ids: Union[Unset, List[int]] = UNSET
        if not isinstance(self.note_ids, Unset):
            note_ids = self.note_ids

        read = self.read

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if note_ids is not UNSET:
            field_dict["noteIds"] = note_ids
        if read is not UNSET:
            field_dict["read"] = read

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        employee_id = d.pop("employeeId", UNSET)

        note_ids = cast(List[int], d.pop("noteIds", UNSET))

        read = d.pop("read", UNSET)

        mark_notes_read_view_model = cls(
            employee_id=employee_id,
            note_ids=note_ids,
            read=read,
        )

        mark_notes_read_view_model.additional_properties = d
        return mark_notes_read_view_model

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
