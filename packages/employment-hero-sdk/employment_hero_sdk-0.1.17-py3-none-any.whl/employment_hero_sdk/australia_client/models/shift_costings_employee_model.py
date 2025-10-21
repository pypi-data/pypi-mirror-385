import datetime
from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="ShiftCostingsEmployeeModel")


@_attrs_define
class ShiftCostingsEmployeeModel:
    """
    Attributes:
        name (Union[Unset, str]):
        date_of_birth (Union[Unset, datetime.datetime]):
        anniversary_date (Union[Unset, datetime.datetime]):
        standard_hours_per_week (Union[Unset, float]):
        standard_hours_per_day (Union[Unset, float]):
        tags (Union[Unset, List[str]]):
    """

    name: Union[Unset, str] = UNSET
    date_of_birth: Union[Unset, datetime.datetime] = UNSET
    anniversary_date: Union[Unset, datetime.datetime] = UNSET
    standard_hours_per_week: Union[Unset, float] = UNSET
    standard_hours_per_day: Union[Unset, float] = UNSET
    tags: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name

        date_of_birth: Union[Unset, str] = UNSET
        if not isinstance(self.date_of_birth, Unset):
            date_of_birth = self.date_of_birth.isoformat()

        anniversary_date: Union[Unset, str] = UNSET
        if not isinstance(self.anniversary_date, Unset):
            anniversary_date = self.anniversary_date.isoformat()

        standard_hours_per_week = self.standard_hours_per_week

        standard_hours_per_day = self.standard_hours_per_day

        tags: Union[Unset, List[str]] = UNSET
        if not isinstance(self.tags, Unset):
            tags = self.tags

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if date_of_birth is not UNSET:
            field_dict["dateOfBirth"] = date_of_birth
        if anniversary_date is not UNSET:
            field_dict["anniversaryDate"] = anniversary_date
        if standard_hours_per_week is not UNSET:
            field_dict["standardHoursPerWeek"] = standard_hours_per_week
        if standard_hours_per_day is not UNSET:
            field_dict["standardHoursPerDay"] = standard_hours_per_day
        if tags is not UNSET:
            field_dict["tags"] = tags

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name", UNSET)

        _date_of_birth = d.pop("dateOfBirth", UNSET)
        date_of_birth: Union[Unset, datetime.datetime]
        if isinstance(_date_of_birth, Unset):
            date_of_birth = UNSET
        else:
            date_of_birth = isoparse(_date_of_birth)

        _anniversary_date = d.pop("anniversaryDate", UNSET)
        anniversary_date: Union[Unset, datetime.datetime]
        if isinstance(_anniversary_date, Unset):
            anniversary_date = UNSET
        else:
            anniversary_date = isoparse(_anniversary_date)

        standard_hours_per_week = d.pop("standardHoursPerWeek", UNSET)

        standard_hours_per_day = d.pop("standardHoursPerDay", UNSET)

        tags = cast(List[str], d.pop("tags", UNSET))

        shift_costings_employee_model = cls(
            name=name,
            date_of_birth=date_of_birth,
            anniversary_date=anniversary_date,
            standard_hours_per_week=standard_hours_per_week,
            standard_hours_per_day=standard_hours_per_day,
            tags=tags,
        )

        shift_costings_employee_model.additional_properties = d
        return shift_costings_employee_model

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
