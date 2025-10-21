from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PaygReportExportModel")


@_attrs_define
class PaygReportExportModel:
    """
    Attributes:
        location (Union[Unset, str]):
        month (Union[Unset, str]):
        gross_earnings (Union[Unset, float]):
        tax_exempt_earnings (Union[Unset, float]):
        pre_tax_deductions (Union[Unset, float]):
        taxable_earnings (Union[Unset, float]):
        payg (Union[Unset, float]):
    """

    location: Union[Unset, str] = UNSET
    month: Union[Unset, str] = UNSET
    gross_earnings: Union[Unset, float] = UNSET
    tax_exempt_earnings: Union[Unset, float] = UNSET
    pre_tax_deductions: Union[Unset, float] = UNSET
    taxable_earnings: Union[Unset, float] = UNSET
    payg: Union[Unset, float] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        location = self.location

        month = self.month

        gross_earnings = self.gross_earnings

        tax_exempt_earnings = self.tax_exempt_earnings

        pre_tax_deductions = self.pre_tax_deductions

        taxable_earnings = self.taxable_earnings

        payg = self.payg

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if location is not UNSET:
            field_dict["location"] = location
        if month is not UNSET:
            field_dict["month"] = month
        if gross_earnings is not UNSET:
            field_dict["grossEarnings"] = gross_earnings
        if tax_exempt_earnings is not UNSET:
            field_dict["taxExemptEarnings"] = tax_exempt_earnings
        if pre_tax_deductions is not UNSET:
            field_dict["preTaxDeductions"] = pre_tax_deductions
        if taxable_earnings is not UNSET:
            field_dict["taxableEarnings"] = taxable_earnings
        if payg is not UNSET:
            field_dict["payg"] = payg

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        location = d.pop("location", UNSET)

        month = d.pop("month", UNSET)

        gross_earnings = d.pop("grossEarnings", UNSET)

        tax_exempt_earnings = d.pop("taxExemptEarnings", UNSET)

        pre_tax_deductions = d.pop("preTaxDeductions", UNSET)

        taxable_earnings = d.pop("taxableEarnings", UNSET)

        payg = d.pop("payg", UNSET)

        payg_report_export_model = cls(
            location=location,
            month=month,
            gross_earnings=gross_earnings,
            tax_exempt_earnings=tax_exempt_earnings,
            pre_tax_deductions=pre_tax_deductions,
            taxable_earnings=taxable_earnings,
            payg=payg,
        )

        payg_report_export_model.additional_properties = d
        return payg_report_export_model

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
