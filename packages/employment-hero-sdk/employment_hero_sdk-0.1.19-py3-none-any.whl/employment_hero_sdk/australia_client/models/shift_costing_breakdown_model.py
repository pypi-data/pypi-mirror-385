import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="ShiftCostingBreakdownModel")


@_attrs_define
class ShiftCostingBreakdownModel:
    """
    Attributes:
        start_time (Union[Unset, datetime.datetime]):
        end_time (Union[Unset, datetime.datetime]):
        pay_category_id (Union[Unset, int]):
        pay_category_name (Union[Unset, str]):
        units (Union[Unset, float]):
        rate (Union[Unset, float]):
        cost (Union[Unset, float]):
        type (Union[Unset, str]):
        liability_category_id (Union[Unset, int]):
        liability_category_name (Union[Unset, str]):
        location_id (Union[Unset, int]):
        location_name (Union[Unset, str]):
    """

    start_time: Union[Unset, datetime.datetime] = UNSET
    end_time: Union[Unset, datetime.datetime] = UNSET
    pay_category_id: Union[Unset, int] = UNSET
    pay_category_name: Union[Unset, str] = UNSET
    units: Union[Unset, float] = UNSET
    rate: Union[Unset, float] = UNSET
    cost: Union[Unset, float] = UNSET
    type: Union[Unset, str] = UNSET
    liability_category_id: Union[Unset, int] = UNSET
    liability_category_name: Union[Unset, str] = UNSET
    location_id: Union[Unset, int] = UNSET
    location_name: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        start_time: Union[Unset, str] = UNSET
        if not isinstance(self.start_time, Unset):
            start_time = self.start_time.isoformat()

        end_time: Union[Unset, str] = UNSET
        if not isinstance(self.end_time, Unset):
            end_time = self.end_time.isoformat()

        pay_category_id = self.pay_category_id

        pay_category_name = self.pay_category_name

        units = self.units

        rate = self.rate

        cost = self.cost

        type = self.type

        liability_category_id = self.liability_category_id

        liability_category_name = self.liability_category_name

        location_id = self.location_id

        location_name = self.location_name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if start_time is not UNSET:
            field_dict["startTime"] = start_time
        if end_time is not UNSET:
            field_dict["endTime"] = end_time
        if pay_category_id is not UNSET:
            field_dict["payCategoryId"] = pay_category_id
        if pay_category_name is not UNSET:
            field_dict["payCategoryName"] = pay_category_name
        if units is not UNSET:
            field_dict["units"] = units
        if rate is not UNSET:
            field_dict["rate"] = rate
        if cost is not UNSET:
            field_dict["cost"] = cost
        if type is not UNSET:
            field_dict["type"] = type
        if liability_category_id is not UNSET:
            field_dict["liabilityCategoryId"] = liability_category_id
        if liability_category_name is not UNSET:
            field_dict["liabilityCategoryName"] = liability_category_name
        if location_id is not UNSET:
            field_dict["locationId"] = location_id
        if location_name is not UNSET:
            field_dict["locationName"] = location_name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _start_time = d.pop("startTime", UNSET)
        start_time: Union[Unset, datetime.datetime]
        if isinstance(_start_time, Unset):
            start_time = UNSET
        else:
            start_time = isoparse(_start_time)

        _end_time = d.pop("endTime", UNSET)
        end_time: Union[Unset, datetime.datetime]
        if isinstance(_end_time, Unset):
            end_time = UNSET
        else:
            end_time = isoparse(_end_time)

        pay_category_id = d.pop("payCategoryId", UNSET)

        pay_category_name = d.pop("payCategoryName", UNSET)

        units = d.pop("units", UNSET)

        rate = d.pop("rate", UNSET)

        cost = d.pop("cost", UNSET)

        type = d.pop("type", UNSET)

        liability_category_id = d.pop("liabilityCategoryId", UNSET)

        liability_category_name = d.pop("liabilityCategoryName", UNSET)

        location_id = d.pop("locationId", UNSET)

        location_name = d.pop("locationName", UNSET)

        shift_costing_breakdown_model = cls(
            start_time=start_time,
            end_time=end_time,
            pay_category_id=pay_category_id,
            pay_category_name=pay_category_name,
            units=units,
            rate=rate,
            cost=cost,
            type=type,
            liability_category_id=liability_category_id,
            liability_category_name=liability_category_name,
            location_id=location_id,
            location_name=location_name,
        )

        shift_costing_breakdown_model.additional_properties = d
        return shift_costing_breakdown_model

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
