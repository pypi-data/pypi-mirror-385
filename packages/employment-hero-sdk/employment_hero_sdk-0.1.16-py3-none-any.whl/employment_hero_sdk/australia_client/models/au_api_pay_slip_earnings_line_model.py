from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AuApiPaySlipEarningsLineModel")


@_attrs_define
class AuApiPaySlipEarningsLineModel:
    """
    Attributes:
        super_contribution (Union[Unset, float]):
        pay_category_name (Union[Unset, str]):
        units (Union[Unset, float]):
        is_fixed (Union[Unset, bool]):
        is_tax_exempt (Union[Unset, bool]):
        rate (Union[Unset, float]):
        notes (Union[Unset, str]):
        gross_earnings (Union[Unset, float]):
        taxable_earnings (Union[Unset, float]):
        location_name (Union[Unset, str]):
    """

    super_contribution: Union[Unset, float] = UNSET
    pay_category_name: Union[Unset, str] = UNSET
    units: Union[Unset, float] = UNSET
    is_fixed: Union[Unset, bool] = UNSET
    is_tax_exempt: Union[Unset, bool] = UNSET
    rate: Union[Unset, float] = UNSET
    notes: Union[Unset, str] = UNSET
    gross_earnings: Union[Unset, float] = UNSET
    taxable_earnings: Union[Unset, float] = UNSET
    location_name: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        super_contribution = self.super_contribution

        pay_category_name = self.pay_category_name

        units = self.units

        is_fixed = self.is_fixed

        is_tax_exempt = self.is_tax_exempt

        rate = self.rate

        notes = self.notes

        gross_earnings = self.gross_earnings

        taxable_earnings = self.taxable_earnings

        location_name = self.location_name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if super_contribution is not UNSET:
            field_dict["superContribution"] = super_contribution
        if pay_category_name is not UNSET:
            field_dict["payCategoryName"] = pay_category_name
        if units is not UNSET:
            field_dict["units"] = units
        if is_fixed is not UNSET:
            field_dict["isFixed"] = is_fixed
        if is_tax_exempt is not UNSET:
            field_dict["isTaxExempt"] = is_tax_exempt
        if rate is not UNSET:
            field_dict["rate"] = rate
        if notes is not UNSET:
            field_dict["notes"] = notes
        if gross_earnings is not UNSET:
            field_dict["grossEarnings"] = gross_earnings
        if taxable_earnings is not UNSET:
            field_dict["taxableEarnings"] = taxable_earnings
        if location_name is not UNSET:
            field_dict["locationName"] = location_name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        super_contribution = d.pop("superContribution", UNSET)

        pay_category_name = d.pop("payCategoryName", UNSET)

        units = d.pop("units", UNSET)

        is_fixed = d.pop("isFixed", UNSET)

        is_tax_exempt = d.pop("isTaxExempt", UNSET)

        rate = d.pop("rate", UNSET)

        notes = d.pop("notes", UNSET)

        gross_earnings = d.pop("grossEarnings", UNSET)

        taxable_earnings = d.pop("taxableEarnings", UNSET)

        location_name = d.pop("locationName", UNSET)

        au_api_pay_slip_earnings_line_model = cls(
            super_contribution=super_contribution,
            pay_category_name=pay_category_name,
            units=units,
            is_fixed=is_fixed,
            is_tax_exempt=is_tax_exempt,
            rate=rate,
            notes=notes,
            gross_earnings=gross_earnings,
            taxable_earnings=taxable_earnings,
            location_name=location_name,
        )

        au_api_pay_slip_earnings_line_model.additional_properties = d
        return au_api_pay_slip_earnings_line_model

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
