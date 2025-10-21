from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="EmployeesFilter")


@_attrs_define
class EmployeesFilter:
    """
    Attributes:
        pay_schedule_id (Union[Unset, int]):
        location_id (Union[Unset, int]):
    """

    pay_schedule_id: Union[Unset, int] = UNSET
    location_id: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        pay_schedule_id = self.pay_schedule_id

        location_id = self.location_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if pay_schedule_id is not UNSET:
            field_dict["payScheduleId"] = pay_schedule_id
        if location_id is not UNSET:
            field_dict["locationId"] = location_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        pay_schedule_id = d.pop("payScheduleId", UNSET)

        location_id = d.pop("locationId", UNSET)

        employees_filter = cls(
            pay_schedule_id=pay_schedule_id,
            location_id=location_id,
        )

        employees_filter.additional_properties = d
        return employees_filter

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
