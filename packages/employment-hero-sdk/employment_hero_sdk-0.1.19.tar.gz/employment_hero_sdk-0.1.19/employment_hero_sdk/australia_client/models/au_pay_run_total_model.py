from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AuPayRunTotalModel")


@_attrs_define
class AuPayRunTotalModel:
    """
    Attributes:
        payg_withheld (Union[Unset, float]):
        sfss_withheld (Union[Unset, float]):
        help_withheld (Union[Unset, float]):
        super_contribution (Union[Unset, float]):
        employer_contribution (Union[Unset, float]):
        id (Union[Unset, int]):
        total_hours (Union[Unset, float]):
        gross_earnings (Union[Unset, float]):
        pre_tax_deductions (Union[Unset, float]):
        taxable_earnings (Union[Unset, float]):
        post_tax_deductions (Union[Unset, float]):
        net_earnings (Union[Unset, float]):
        total_employee_expenses (Union[Unset, float]):
        total_employer_liabilities (Union[Unset, float]):
        is_published (Union[Unset, bool]):
        pay_run_id (Union[Unset, int]):
        notation (Union[Unset, str]):
    """

    payg_withheld: Union[Unset, float] = UNSET
    sfss_withheld: Union[Unset, float] = UNSET
    help_withheld: Union[Unset, float] = UNSET
    super_contribution: Union[Unset, float] = UNSET
    employer_contribution: Union[Unset, float] = UNSET
    id: Union[Unset, int] = UNSET
    total_hours: Union[Unset, float] = UNSET
    gross_earnings: Union[Unset, float] = UNSET
    pre_tax_deductions: Union[Unset, float] = UNSET
    taxable_earnings: Union[Unset, float] = UNSET
    post_tax_deductions: Union[Unset, float] = UNSET
    net_earnings: Union[Unset, float] = UNSET
    total_employee_expenses: Union[Unset, float] = UNSET
    total_employer_liabilities: Union[Unset, float] = UNSET
    is_published: Union[Unset, bool] = UNSET
    pay_run_id: Union[Unset, int] = UNSET
    notation: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        payg_withheld = self.payg_withheld

        sfss_withheld = self.sfss_withheld

        help_withheld = self.help_withheld

        super_contribution = self.super_contribution

        employer_contribution = self.employer_contribution

        id = self.id

        total_hours = self.total_hours

        gross_earnings = self.gross_earnings

        pre_tax_deductions = self.pre_tax_deductions

        taxable_earnings = self.taxable_earnings

        post_tax_deductions = self.post_tax_deductions

        net_earnings = self.net_earnings

        total_employee_expenses = self.total_employee_expenses

        total_employer_liabilities = self.total_employer_liabilities

        is_published = self.is_published

        pay_run_id = self.pay_run_id

        notation = self.notation

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if payg_withheld is not UNSET:
            field_dict["paygWithheld"] = payg_withheld
        if sfss_withheld is not UNSET:
            field_dict["sfssWithheld"] = sfss_withheld
        if help_withheld is not UNSET:
            field_dict["helpWithheld"] = help_withheld
        if super_contribution is not UNSET:
            field_dict["superContribution"] = super_contribution
        if employer_contribution is not UNSET:
            field_dict["employerContribution"] = employer_contribution
        if id is not UNSET:
            field_dict["id"] = id
        if total_hours is not UNSET:
            field_dict["totalHours"] = total_hours
        if gross_earnings is not UNSET:
            field_dict["grossEarnings"] = gross_earnings
        if pre_tax_deductions is not UNSET:
            field_dict["preTaxDeductions"] = pre_tax_deductions
        if taxable_earnings is not UNSET:
            field_dict["taxableEarnings"] = taxable_earnings
        if post_tax_deductions is not UNSET:
            field_dict["postTaxDeductions"] = post_tax_deductions
        if net_earnings is not UNSET:
            field_dict["netEarnings"] = net_earnings
        if total_employee_expenses is not UNSET:
            field_dict["totalEmployeeExpenses"] = total_employee_expenses
        if total_employer_liabilities is not UNSET:
            field_dict["totalEmployerLiabilities"] = total_employer_liabilities
        if is_published is not UNSET:
            field_dict["isPublished"] = is_published
        if pay_run_id is not UNSET:
            field_dict["payRunId"] = pay_run_id
        if notation is not UNSET:
            field_dict["notation"] = notation

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        payg_withheld = d.pop("paygWithheld", UNSET)

        sfss_withheld = d.pop("sfssWithheld", UNSET)

        help_withheld = d.pop("helpWithheld", UNSET)

        super_contribution = d.pop("superContribution", UNSET)

        employer_contribution = d.pop("employerContribution", UNSET)

        id = d.pop("id", UNSET)

        total_hours = d.pop("totalHours", UNSET)

        gross_earnings = d.pop("grossEarnings", UNSET)

        pre_tax_deductions = d.pop("preTaxDeductions", UNSET)

        taxable_earnings = d.pop("taxableEarnings", UNSET)

        post_tax_deductions = d.pop("postTaxDeductions", UNSET)

        net_earnings = d.pop("netEarnings", UNSET)

        total_employee_expenses = d.pop("totalEmployeeExpenses", UNSET)

        total_employer_liabilities = d.pop("totalEmployerLiabilities", UNSET)

        is_published = d.pop("isPublished", UNSET)

        pay_run_id = d.pop("payRunId", UNSET)

        notation = d.pop("notation", UNSET)

        au_pay_run_total_model = cls(
            payg_withheld=payg_withheld,
            sfss_withheld=sfss_withheld,
            help_withheld=help_withheld,
            super_contribution=super_contribution,
            employer_contribution=employer_contribution,
            id=id,
            total_hours=total_hours,
            gross_earnings=gross_earnings,
            pre_tax_deductions=pre_tax_deductions,
            taxable_earnings=taxable_earnings,
            post_tax_deductions=post_tax_deductions,
            net_earnings=net_earnings,
            total_employee_expenses=total_employee_expenses,
            total_employer_liabilities=total_employer_liabilities,
            is_published=is_published,
            pay_run_id=pay_run_id,
            notation=notation,
        )

        au_pay_run_total_model.additional_properties = d
        return au_pay_run_total_model

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
