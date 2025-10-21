from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AuPayRunGrandTotalModel")


@_attrs_define
class AuPayRunGrandTotalModel:
    """
    Attributes:
        sfss_amount (Union[Unset, float]):
        help_amount (Union[Unset, float]):
        super_contribution (Union[Unset, float]):
        payg_withholding_amount (Union[Unset, float]):
        number_of_employees (Union[Unset, int]):
        total_hours (Union[Unset, float]):
        taxable_earnings (Union[Unset, float]):
        gross_earnings (Union[Unset, float]):
        net_earnings (Union[Unset, float]):
        pre_tax_deduction_amount (Union[Unset, float]):
        post_tax_deduction_amount (Union[Unset, float]):
        employer_contribution (Union[Unset, float]):
        employee_expenses_total (Union[Unset, float]):
        employer_liabilities_total (Union[Unset, float]):
    """

    sfss_amount: Union[Unset, float] = UNSET
    help_amount: Union[Unset, float] = UNSET
    super_contribution: Union[Unset, float] = UNSET
    payg_withholding_amount: Union[Unset, float] = UNSET
    number_of_employees: Union[Unset, int] = UNSET
    total_hours: Union[Unset, float] = UNSET
    taxable_earnings: Union[Unset, float] = UNSET
    gross_earnings: Union[Unset, float] = UNSET
    net_earnings: Union[Unset, float] = UNSET
    pre_tax_deduction_amount: Union[Unset, float] = UNSET
    post_tax_deduction_amount: Union[Unset, float] = UNSET
    employer_contribution: Union[Unset, float] = UNSET
    employee_expenses_total: Union[Unset, float] = UNSET
    employer_liabilities_total: Union[Unset, float] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        sfss_amount = self.sfss_amount

        help_amount = self.help_amount

        super_contribution = self.super_contribution

        payg_withholding_amount = self.payg_withholding_amount

        number_of_employees = self.number_of_employees

        total_hours = self.total_hours

        taxable_earnings = self.taxable_earnings

        gross_earnings = self.gross_earnings

        net_earnings = self.net_earnings

        pre_tax_deduction_amount = self.pre_tax_deduction_amount

        post_tax_deduction_amount = self.post_tax_deduction_amount

        employer_contribution = self.employer_contribution

        employee_expenses_total = self.employee_expenses_total

        employer_liabilities_total = self.employer_liabilities_total

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if sfss_amount is not UNSET:
            field_dict["sfssAmount"] = sfss_amount
        if help_amount is not UNSET:
            field_dict["helpAmount"] = help_amount
        if super_contribution is not UNSET:
            field_dict["superContribution"] = super_contribution
        if payg_withholding_amount is not UNSET:
            field_dict["paygWithholdingAmount"] = payg_withholding_amount
        if number_of_employees is not UNSET:
            field_dict["numberOfEmployees"] = number_of_employees
        if total_hours is not UNSET:
            field_dict["totalHours"] = total_hours
        if taxable_earnings is not UNSET:
            field_dict["taxableEarnings"] = taxable_earnings
        if gross_earnings is not UNSET:
            field_dict["grossEarnings"] = gross_earnings
        if net_earnings is not UNSET:
            field_dict["netEarnings"] = net_earnings
        if pre_tax_deduction_amount is not UNSET:
            field_dict["preTaxDeductionAmount"] = pre_tax_deduction_amount
        if post_tax_deduction_amount is not UNSET:
            field_dict["postTaxDeductionAmount"] = post_tax_deduction_amount
        if employer_contribution is not UNSET:
            field_dict["employerContribution"] = employer_contribution
        if employee_expenses_total is not UNSET:
            field_dict["employeeExpensesTotal"] = employee_expenses_total
        if employer_liabilities_total is not UNSET:
            field_dict["employerLiabilitiesTotal"] = employer_liabilities_total

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        sfss_amount = d.pop("sfssAmount", UNSET)

        help_amount = d.pop("helpAmount", UNSET)

        super_contribution = d.pop("superContribution", UNSET)

        payg_withholding_amount = d.pop("paygWithholdingAmount", UNSET)

        number_of_employees = d.pop("numberOfEmployees", UNSET)

        total_hours = d.pop("totalHours", UNSET)

        taxable_earnings = d.pop("taxableEarnings", UNSET)

        gross_earnings = d.pop("grossEarnings", UNSET)

        net_earnings = d.pop("netEarnings", UNSET)

        pre_tax_deduction_amount = d.pop("preTaxDeductionAmount", UNSET)

        post_tax_deduction_amount = d.pop("postTaxDeductionAmount", UNSET)

        employer_contribution = d.pop("employerContribution", UNSET)

        employee_expenses_total = d.pop("employeeExpensesTotal", UNSET)

        employer_liabilities_total = d.pop("employerLiabilitiesTotal", UNSET)

        au_pay_run_grand_total_model = cls(
            sfss_amount=sfss_amount,
            help_amount=help_amount,
            super_contribution=super_contribution,
            payg_withholding_amount=payg_withholding_amount,
            number_of_employees=number_of_employees,
            total_hours=total_hours,
            taxable_earnings=taxable_earnings,
            gross_earnings=gross_earnings,
            net_earnings=net_earnings,
            pre_tax_deduction_amount=pre_tax_deduction_amount,
            post_tax_deduction_amount=post_tax_deduction_amount,
            employer_contribution=employer_contribution,
            employee_expenses_total=employee_expenses_total,
            employer_liabilities_total=employer_liabilities_total,
        )

        au_pay_run_grand_total_model.additional_properties = d
        return au_pay_run_grand_total_model

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
