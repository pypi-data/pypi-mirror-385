import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="TasksReportNoteModel")


@_attrs_define
class TasksReportNoteModel:
    """
    Attributes:
        username (Union[Unset, str]):
        date_created (Union[Unset, datetime.datetime]):
        note (Union[Unset, str]):
        is_visible_to_manager (Union[Unset, bool]):
    """

    username: Union[Unset, str] = UNSET
    date_created: Union[Unset, datetime.datetime] = UNSET
    note: Union[Unset, str] = UNSET
    is_visible_to_manager: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        username = self.username

        date_created: Union[Unset, str] = UNSET
        if not isinstance(self.date_created, Unset):
            date_created = self.date_created.isoformat()

        note = self.note

        is_visible_to_manager = self.is_visible_to_manager

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if username is not UNSET:
            field_dict["username"] = username
        if date_created is not UNSET:
            field_dict["dateCreated"] = date_created
        if note is not UNSET:
            field_dict["note"] = note
        if is_visible_to_manager is not UNSET:
            field_dict["isVisibleToManager"] = is_visible_to_manager

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        username = d.pop("username", UNSET)

        _date_created = d.pop("dateCreated", UNSET)
        date_created: Union[Unset, datetime.datetime]
        if isinstance(_date_created, Unset):
            date_created = UNSET
        else:
            date_created = isoparse(_date_created)

        note = d.pop("note", UNSET)

        is_visible_to_manager = d.pop("isVisibleToManager", UNSET)

        tasks_report_note_model = cls(
            username=username,
            date_created=date_created,
            note=note,
            is_visible_to_manager=is_visible_to_manager,
        )

        tasks_report_note_model.additional_properties = d
        return tasks_report_note_model

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
