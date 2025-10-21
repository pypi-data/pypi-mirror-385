from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ApiYearToDateEarningsBreakdownModel")


@_attrs_define
class ApiYearToDateEarningsBreakdownModel:
    """
    Attributes:
        pay_category_name (Union[Unset, str]):
        gross_earnings (Union[Unset, float]):
    """

    pay_category_name: Union[Unset, str] = UNSET
    gross_earnings: Union[Unset, float] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        pay_category_name = self.pay_category_name

        gross_earnings = self.gross_earnings

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if pay_category_name is not UNSET:
            field_dict["payCategoryName"] = pay_category_name
        if gross_earnings is not UNSET:
            field_dict["grossEarnings"] = gross_earnings

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        pay_category_name = d.pop("payCategoryName", UNSET)

        gross_earnings = d.pop("grossEarnings", UNSET)

        api_year_to_date_earnings_breakdown_model = cls(
            pay_category_name=pay_category_name,
            gross_earnings=gross_earnings,
        )

        api_year_to_date_earnings_breakdown_model.additional_properties = d
        return api_year_to_date_earnings_breakdown_model

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
