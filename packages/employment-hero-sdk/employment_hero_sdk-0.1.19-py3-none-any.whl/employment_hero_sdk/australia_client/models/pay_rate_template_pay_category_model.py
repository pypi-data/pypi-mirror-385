from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PayRateTemplatePayCategoryModel")


@_attrs_define
class PayRateTemplatePayCategoryModel:
    """
    Attributes:
        pay_category_id (Union[Unset, int]):
        pay_category_name (Union[Unset, str]):
        user_supplied_rate (Union[Unset, float]):
        calculated_rate (Union[Unset, float]):
        standard_weekly_hours (Union[Unset, float]):
        super_rate (Union[Unset, float]):
    """

    pay_category_id: Union[Unset, int] = UNSET
    pay_category_name: Union[Unset, str] = UNSET
    user_supplied_rate: Union[Unset, float] = UNSET
    calculated_rate: Union[Unset, float] = UNSET
    standard_weekly_hours: Union[Unset, float] = UNSET
    super_rate: Union[Unset, float] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        pay_category_id = self.pay_category_id

        pay_category_name = self.pay_category_name

        user_supplied_rate = self.user_supplied_rate

        calculated_rate = self.calculated_rate

        standard_weekly_hours = self.standard_weekly_hours

        super_rate = self.super_rate

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if pay_category_id is not UNSET:
            field_dict["payCategoryId"] = pay_category_id
        if pay_category_name is not UNSET:
            field_dict["payCategoryName"] = pay_category_name
        if user_supplied_rate is not UNSET:
            field_dict["userSuppliedRate"] = user_supplied_rate
        if calculated_rate is not UNSET:
            field_dict["calculatedRate"] = calculated_rate
        if standard_weekly_hours is not UNSET:
            field_dict["standardWeeklyHours"] = standard_weekly_hours
        if super_rate is not UNSET:
            field_dict["superRate"] = super_rate

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        pay_category_id = d.pop("payCategoryId", UNSET)

        pay_category_name = d.pop("payCategoryName", UNSET)

        user_supplied_rate = d.pop("userSuppliedRate", UNSET)

        calculated_rate = d.pop("calculatedRate", UNSET)

        standard_weekly_hours = d.pop("standardWeeklyHours", UNSET)

        super_rate = d.pop("superRate", UNSET)

        pay_rate_template_pay_category_model = cls(
            pay_category_id=pay_category_id,
            pay_category_name=pay_category_name,
            user_supplied_rate=user_supplied_rate,
            calculated_rate=calculated_rate,
            standard_weekly_hours=standard_weekly_hours,
            super_rate=super_rate,
        )

        pay_rate_template_pay_category_model.additional_properties = d
        return pay_rate_template_pay_category_model

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
