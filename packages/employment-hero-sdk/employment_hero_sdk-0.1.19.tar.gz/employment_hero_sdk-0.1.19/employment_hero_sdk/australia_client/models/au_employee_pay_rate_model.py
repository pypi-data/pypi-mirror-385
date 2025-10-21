from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AuEmployeePayRateModel")


@_attrs_define
class AuEmployeePayRateModel:
    """
    Attributes:
        has_super_rate_override (Union[Unset, bool]):
        super_rate (Union[Unset, float]):
        pay_category_id (Union[Unset, int]):
        pay_category_name (Union[Unset, str]):
        is_primary_pay_category (Union[Unset, bool]):
        accrues_leave (Union[Unset, bool]):
        rate_unit (Union[Unset, str]):
        rate (Union[Unset, float]):
        calculated_rate (Union[Unset, float]):
    """

    has_super_rate_override: Union[Unset, bool] = UNSET
    super_rate: Union[Unset, float] = UNSET
    pay_category_id: Union[Unset, int] = UNSET
    pay_category_name: Union[Unset, str] = UNSET
    is_primary_pay_category: Union[Unset, bool] = UNSET
    accrues_leave: Union[Unset, bool] = UNSET
    rate_unit: Union[Unset, str] = UNSET
    rate: Union[Unset, float] = UNSET
    calculated_rate: Union[Unset, float] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        has_super_rate_override = self.has_super_rate_override

        super_rate = self.super_rate

        pay_category_id = self.pay_category_id

        pay_category_name = self.pay_category_name

        is_primary_pay_category = self.is_primary_pay_category

        accrues_leave = self.accrues_leave

        rate_unit = self.rate_unit

        rate = self.rate

        calculated_rate = self.calculated_rate

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if has_super_rate_override is not UNSET:
            field_dict["hasSuperRateOverride"] = has_super_rate_override
        if super_rate is not UNSET:
            field_dict["superRate"] = super_rate
        if pay_category_id is not UNSET:
            field_dict["payCategoryId"] = pay_category_id
        if pay_category_name is not UNSET:
            field_dict["payCategoryName"] = pay_category_name
        if is_primary_pay_category is not UNSET:
            field_dict["isPrimaryPayCategory"] = is_primary_pay_category
        if accrues_leave is not UNSET:
            field_dict["accruesLeave"] = accrues_leave
        if rate_unit is not UNSET:
            field_dict["rateUnit"] = rate_unit
        if rate is not UNSET:
            field_dict["rate"] = rate
        if calculated_rate is not UNSET:
            field_dict["calculatedRate"] = calculated_rate

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        has_super_rate_override = d.pop("hasSuperRateOverride", UNSET)

        super_rate = d.pop("superRate", UNSET)

        pay_category_id = d.pop("payCategoryId", UNSET)

        pay_category_name = d.pop("payCategoryName", UNSET)

        is_primary_pay_category = d.pop("isPrimaryPayCategory", UNSET)

        accrues_leave = d.pop("accruesLeave", UNSET)

        rate_unit = d.pop("rateUnit", UNSET)

        rate = d.pop("rate", UNSET)

        calculated_rate = d.pop("calculatedRate", UNSET)

        au_employee_pay_rate_model = cls(
            has_super_rate_override=has_super_rate_override,
            super_rate=super_rate,
            pay_category_id=pay_category_id,
            pay_category_name=pay_category_name,
            is_primary_pay_category=is_primary_pay_category,
            accrues_leave=accrues_leave,
            rate_unit=rate_unit,
            rate=rate,
            calculated_rate=calculated_rate,
        )

        au_employee_pay_rate_model.additional_properties = d
        return au_employee_pay_rate_model

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
