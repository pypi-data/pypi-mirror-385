from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.au_detailed_activity_report_export_model_object import AuDetailedActivityReportExportModelObject


T = TypeVar("T", bound="AuDetailedActivityReportExportModel")


@_attrs_define
class AuDetailedActivityReportExportModel:
    """
    Attributes:
        payg (Union[Unset, float]):
        sfss (Union[Unset, float]):
        help_ (Union[Unset, float]):
        super_ (Union[Unset, float]):
        gross_plus_super (Union[Unset, float]):
        location (Union[Unset, str]):
        employee_id (Union[Unset, int]):
        first_name (Union[Unset, str]):
        surname (Union[Unset, str]):
        external_id (Union[Unset, str]):
        hours (Union[Unset, float]):
        gross_earnings (Union[Unset, float]):
        pre_tax_deductions (Union[Unset, float]):
        post_tax_deductions (Union[Unset, AuDetailedActivityReportExportModelObject]):
        tax_exempt_earnings (Union[Unset, float]):
        taxable_earnings (Union[Unset, float]):
        net_earnings (Union[Unset, float]):
        employer_liabilities (Union[Unset, float]):
    """

    payg: Union[Unset, float] = UNSET
    sfss: Union[Unset, float] = UNSET
    help_: Union[Unset, float] = UNSET
    super_: Union[Unset, float] = UNSET
    gross_plus_super: Union[Unset, float] = UNSET
    location: Union[Unset, str] = UNSET
    employee_id: Union[Unset, int] = UNSET
    first_name: Union[Unset, str] = UNSET
    surname: Union[Unset, str] = UNSET
    external_id: Union[Unset, str] = UNSET
    hours: Union[Unset, float] = UNSET
    gross_earnings: Union[Unset, float] = UNSET
    pre_tax_deductions: Union[Unset, float] = UNSET
    post_tax_deductions: Union[Unset, "AuDetailedActivityReportExportModelObject"] = UNSET
    tax_exempt_earnings: Union[Unset, float] = UNSET
    taxable_earnings: Union[Unset, float] = UNSET
    net_earnings: Union[Unset, float] = UNSET
    employer_liabilities: Union[Unset, float] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        payg = self.payg

        sfss = self.sfss

        help_ = self.help_

        super_ = self.super_

        gross_plus_super = self.gross_plus_super

        location = self.location

        employee_id = self.employee_id

        first_name = self.first_name

        surname = self.surname

        external_id = self.external_id

        hours = self.hours

        gross_earnings = self.gross_earnings

        pre_tax_deductions = self.pre_tax_deductions

        post_tax_deductions: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.post_tax_deductions, Unset):
            post_tax_deductions = self.post_tax_deductions.to_dict()

        tax_exempt_earnings = self.tax_exempt_earnings

        taxable_earnings = self.taxable_earnings

        net_earnings = self.net_earnings

        employer_liabilities = self.employer_liabilities

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if payg is not UNSET:
            field_dict["payg"] = payg
        if sfss is not UNSET:
            field_dict["sfss"] = sfss
        if help_ is not UNSET:
            field_dict["help"] = help_
        if super_ is not UNSET:
            field_dict["super"] = super_
        if gross_plus_super is not UNSET:
            field_dict["grossPlusSuper"] = gross_plus_super
        if location is not UNSET:
            field_dict["location"] = location
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if first_name is not UNSET:
            field_dict["firstName"] = first_name
        if surname is not UNSET:
            field_dict["surname"] = surname
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if hours is not UNSET:
            field_dict["hours"] = hours
        if gross_earnings is not UNSET:
            field_dict["grossEarnings"] = gross_earnings
        if pre_tax_deductions is not UNSET:
            field_dict["preTaxDeductions"] = pre_tax_deductions
        if post_tax_deductions is not UNSET:
            field_dict["postTaxDeductions"] = post_tax_deductions
        if tax_exempt_earnings is not UNSET:
            field_dict["taxExemptEarnings"] = tax_exempt_earnings
        if taxable_earnings is not UNSET:
            field_dict["taxableEarnings"] = taxable_earnings
        if net_earnings is not UNSET:
            field_dict["netEarnings"] = net_earnings
        if employer_liabilities is not UNSET:
            field_dict["employerLiabilities"] = employer_liabilities

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.au_detailed_activity_report_export_model_object import AuDetailedActivityReportExportModelObject

        d = src_dict.copy()
        payg = d.pop("payg", UNSET)

        sfss = d.pop("sfss", UNSET)

        help_ = d.pop("help", UNSET)

        super_ = d.pop("super", UNSET)

        gross_plus_super = d.pop("grossPlusSuper", UNSET)

        location = d.pop("location", UNSET)

        employee_id = d.pop("employeeId", UNSET)

        first_name = d.pop("firstName", UNSET)

        surname = d.pop("surname", UNSET)

        external_id = d.pop("externalId", UNSET)

        hours = d.pop("hours", UNSET)

        gross_earnings = d.pop("grossEarnings", UNSET)

        pre_tax_deductions = d.pop("preTaxDeductions", UNSET)

        _post_tax_deductions = d.pop("postTaxDeductions", UNSET)
        post_tax_deductions: Union[Unset, AuDetailedActivityReportExportModelObject]
        if isinstance(_post_tax_deductions, Unset):
            post_tax_deductions = UNSET
        else:
            post_tax_deductions = AuDetailedActivityReportExportModelObject.from_dict(_post_tax_deductions)

        tax_exempt_earnings = d.pop("taxExemptEarnings", UNSET)

        taxable_earnings = d.pop("taxableEarnings", UNSET)

        net_earnings = d.pop("netEarnings", UNSET)

        employer_liabilities = d.pop("employerLiabilities", UNSET)

        au_detailed_activity_report_export_model = cls(
            payg=payg,
            sfss=sfss,
            help_=help_,
            super_=super_,
            gross_plus_super=gross_plus_super,
            location=location,
            employee_id=employee_id,
            first_name=first_name,
            surname=surname,
            external_id=external_id,
            hours=hours,
            gross_earnings=gross_earnings,
            pre_tax_deductions=pre_tax_deductions,
            post_tax_deductions=post_tax_deductions,
            tax_exempt_earnings=tax_exempt_earnings,
            taxable_earnings=taxable_earnings,
            net_earnings=net_earnings,
            employer_liabilities=employer_liabilities,
        )

        au_detailed_activity_report_export_model.additional_properties = d
        return au_detailed_activity_report_export_model

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
