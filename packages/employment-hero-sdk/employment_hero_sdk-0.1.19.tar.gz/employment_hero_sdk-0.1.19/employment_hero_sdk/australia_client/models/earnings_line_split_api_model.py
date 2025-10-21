from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="EarningsLineSplitApiModel")


@_attrs_define
class EarningsLineSplitApiModel:
    """
    Attributes:
        location_id (Union[Unset, int]):
        location_name (Union[Unset, str]):
        allocated_percentage (Union[Unset, float]):
        allocate_balance (Union[Unset, bool]):
    """

    location_id: Union[Unset, int] = UNSET
    location_name: Union[Unset, str] = UNSET
    allocated_percentage: Union[Unset, float] = UNSET
    allocate_balance: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        location_id = self.location_id

        location_name = self.location_name

        allocated_percentage = self.allocated_percentage

        allocate_balance = self.allocate_balance

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if location_id is not UNSET:
            field_dict["locationId"] = location_id
        if location_name is not UNSET:
            field_dict["locationName"] = location_name
        if allocated_percentage is not UNSET:
            field_dict["allocatedPercentage"] = allocated_percentage
        if allocate_balance is not UNSET:
            field_dict["allocateBalance"] = allocate_balance

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        location_id = d.pop("locationId", UNSET)

        location_name = d.pop("locationName", UNSET)

        allocated_percentage = d.pop("allocatedPercentage", UNSET)

        allocate_balance = d.pop("allocateBalance", UNSET)

        earnings_line_split_api_model = cls(
            location_id=location_id,
            location_name=location_name,
            allocated_percentage=allocated_percentage,
            allocate_balance=allocate_balance,
        )

        earnings_line_split_api_model.additional_properties = d
        return earnings_line_split_api_model

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
