import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="BusinessAction")


@_attrs_define
class BusinessAction:
    """
    Attributes:
        date (Union[Unset, datetime.datetime]):
        title (Union[Unset, str]):
        id (Union[Unset, int]):
        high_priority (Union[Unset, bool]):
    """

    date: Union[Unset, datetime.datetime] = UNSET
    title: Union[Unset, str] = UNSET
    id: Union[Unset, int] = UNSET
    high_priority: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        date: Union[Unset, str] = UNSET
        if not isinstance(self.date, Unset):
            date = self.date.isoformat()

        title = self.title

        id = self.id

        high_priority = self.high_priority

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if date is not UNSET:
            field_dict["date"] = date
        if title is not UNSET:
            field_dict["title"] = title
        if id is not UNSET:
            field_dict["id"] = id
        if high_priority is not UNSET:
            field_dict["highPriority"] = high_priority

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _date = d.pop("date", UNSET)
        date: Union[Unset, datetime.datetime]
        if isinstance(_date, Unset):
            date = UNSET
        else:
            date = isoparse(_date)

        title = d.pop("title", UNSET)

        id = d.pop("id", UNSET)

        high_priority = d.pop("highPriority", UNSET)

        business_action = cls(
            date=date,
            title=title,
            id=id,
            high_priority=high_priority,
        )

        business_action.additional_properties = d
        return business_action

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
