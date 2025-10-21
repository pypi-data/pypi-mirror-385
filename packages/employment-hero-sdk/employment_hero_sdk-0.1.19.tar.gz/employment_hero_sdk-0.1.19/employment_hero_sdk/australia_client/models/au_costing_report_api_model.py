from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.au_costing_report_api_model_i_dictionary_string_decimal import (
        AuCostingReportApiModelIDictionaryStringDecimal,
    )


T = TypeVar("T", bound="AuCostingReportApiModel")


@_attrs_define
class AuCostingReportApiModel:
    """
    Attributes:
        super_contribution (Union[Unset, float]):
        location_id (Union[Unset, int]):
        location_name (Union[Unset, str]):
        pay_categories (Union[Unset, AuCostingReportApiModelIDictionaryStringDecimal]):
    """

    super_contribution: Union[Unset, float] = UNSET
    location_id: Union[Unset, int] = UNSET
    location_name: Union[Unset, str] = UNSET
    pay_categories: Union[Unset, "AuCostingReportApiModelIDictionaryStringDecimal"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        super_contribution = self.super_contribution

        location_id = self.location_id

        location_name = self.location_name

        pay_categories: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.pay_categories, Unset):
            pay_categories = self.pay_categories.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if super_contribution is not UNSET:
            field_dict["superContribution"] = super_contribution
        if location_id is not UNSET:
            field_dict["locationId"] = location_id
        if location_name is not UNSET:
            field_dict["locationName"] = location_name
        if pay_categories is not UNSET:
            field_dict["payCategories"] = pay_categories

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.au_costing_report_api_model_i_dictionary_string_decimal import (
            AuCostingReportApiModelIDictionaryStringDecimal,
        )

        d = src_dict.copy()
        super_contribution = d.pop("superContribution", UNSET)

        location_id = d.pop("locationId", UNSET)

        location_name = d.pop("locationName", UNSET)

        _pay_categories = d.pop("payCategories", UNSET)
        pay_categories: Union[Unset, AuCostingReportApiModelIDictionaryStringDecimal]
        if isinstance(_pay_categories, Unset):
            pay_categories = UNSET
        else:
            pay_categories = AuCostingReportApiModelIDictionaryStringDecimal.from_dict(_pay_categories)

        au_costing_report_api_model = cls(
            super_contribution=super_contribution,
            location_id=location_id,
            location_name=location_name,
            pay_categories=pay_categories,
        )

        au_costing_report_api_model.additional_properties = d
        return au_costing_report_api_model

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
