import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="AuPayRunTotalDetailModel")


@_attrs_define
class AuPayRunTotalDetailModel:
    """
    Attributes:
        payg_withholding_amount (Union[Unset, float]):
        payg_withholding_percent (Union[Unset, float]):
        sfss_amount (Union[Unset, float]):
        help_amount (Union[Unset, float]):
        super_contribution (Union[Unset, float]):
        employer_contribution (Union[Unset, float]):
        super_contribution_minus_super_adjustments (Union[Unset, float]):
        all_super_contributions_total (Union[Unset, float]):
        gross_plus_super (Union[Unset, float]):
        super_adjustments_amount (Union[Unset, float]):
        salary_sacrifice_super_amount (Union[Unset, float]):
        member_voluntary_super_amount (Union[Unset, float]):
        non_super_deduction_total (Union[Unset, float]):
        super_payments_total (Union[Unset, float]):
        is_employee_under_18 (Union[Unset, bool]):
        employer_contribution_adjustments_amount (Union[Unset, float]):
        payg_adjustments_amount (Union[Unset, float]):
        super_contributions_cap_applied (Union[Unset, bool]):
        payg_payment_total (Union[Unset, float]):
        id (Union[Unset, int]):
        employee_name (Union[Unset, str]):
        total_hours (Union[Unset, float]):
        gross_earnings (Union[Unset, float]):
        net_earnings (Union[Unset, float]):
        taxable_earnings (Union[Unset, float]):
        post_tax_deduction_amount (Union[Unset, float]):
        pre_tax_deduction_amount (Union[Unset, float]):
        pay_condition_rule_set_name (Union[Unset, str]):
        employee_id (Union[Unset, int]):
        is_termination (Union[Unset, bool]):
        notation (Union[Unset, str]):
        employee_start_date (Union[Unset, datetime.datetime]):
        employee_external_reference_id (Union[Unset, str]):
        is_excluded (Union[Unset, bool]):
        employee_external_id (Union[Unset, str]):
        bank_payments_total (Union[Unset, float]):
        termination_date (Union[Unset, datetime.datetime]):
        earliest_termination_date (Union[Unset, datetime.datetime]):
        previous_termination_date (Union[Unset, datetime.datetime]):
        employee_expenses_total (Union[Unset, float]):
        employer_liabilities_total (Union[Unset, float]):
        is_complete (Union[Unset, bool]):
    """

    payg_withholding_amount: Union[Unset, float] = UNSET
    payg_withholding_percent: Union[Unset, float] = UNSET
    sfss_amount: Union[Unset, float] = UNSET
    help_amount: Union[Unset, float] = UNSET
    super_contribution: Union[Unset, float] = UNSET
    employer_contribution: Union[Unset, float] = UNSET
    super_contribution_minus_super_adjustments: Union[Unset, float] = UNSET
    all_super_contributions_total: Union[Unset, float] = UNSET
    gross_plus_super: Union[Unset, float] = UNSET
    super_adjustments_amount: Union[Unset, float] = UNSET
    salary_sacrifice_super_amount: Union[Unset, float] = UNSET
    member_voluntary_super_amount: Union[Unset, float] = UNSET
    non_super_deduction_total: Union[Unset, float] = UNSET
    super_payments_total: Union[Unset, float] = UNSET
    is_employee_under_18: Union[Unset, bool] = UNSET
    employer_contribution_adjustments_amount: Union[Unset, float] = UNSET
    payg_adjustments_amount: Union[Unset, float] = UNSET
    super_contributions_cap_applied: Union[Unset, bool] = UNSET
    payg_payment_total: Union[Unset, float] = UNSET
    id: Union[Unset, int] = UNSET
    employee_name: Union[Unset, str] = UNSET
    total_hours: Union[Unset, float] = UNSET
    gross_earnings: Union[Unset, float] = UNSET
    net_earnings: Union[Unset, float] = UNSET
    taxable_earnings: Union[Unset, float] = UNSET
    post_tax_deduction_amount: Union[Unset, float] = UNSET
    pre_tax_deduction_amount: Union[Unset, float] = UNSET
    pay_condition_rule_set_name: Union[Unset, str] = UNSET
    employee_id: Union[Unset, int] = UNSET
    is_termination: Union[Unset, bool] = UNSET
    notation: Union[Unset, str] = UNSET
    employee_start_date: Union[Unset, datetime.datetime] = UNSET
    employee_external_reference_id: Union[Unset, str] = UNSET
    is_excluded: Union[Unset, bool] = UNSET
    employee_external_id: Union[Unset, str] = UNSET
    bank_payments_total: Union[Unset, float] = UNSET
    termination_date: Union[Unset, datetime.datetime] = UNSET
    earliest_termination_date: Union[Unset, datetime.datetime] = UNSET
    previous_termination_date: Union[Unset, datetime.datetime] = UNSET
    employee_expenses_total: Union[Unset, float] = UNSET
    employer_liabilities_total: Union[Unset, float] = UNSET
    is_complete: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        payg_withholding_amount = self.payg_withholding_amount

        payg_withholding_percent = self.payg_withholding_percent

        sfss_amount = self.sfss_amount

        help_amount = self.help_amount

        super_contribution = self.super_contribution

        employer_contribution = self.employer_contribution

        super_contribution_minus_super_adjustments = self.super_contribution_minus_super_adjustments

        all_super_contributions_total = self.all_super_contributions_total

        gross_plus_super = self.gross_plus_super

        super_adjustments_amount = self.super_adjustments_amount

        salary_sacrifice_super_amount = self.salary_sacrifice_super_amount

        member_voluntary_super_amount = self.member_voluntary_super_amount

        non_super_deduction_total = self.non_super_deduction_total

        super_payments_total = self.super_payments_total

        is_employee_under_18 = self.is_employee_under_18

        employer_contribution_adjustments_amount = self.employer_contribution_adjustments_amount

        payg_adjustments_amount = self.payg_adjustments_amount

        super_contributions_cap_applied = self.super_contributions_cap_applied

        payg_payment_total = self.payg_payment_total

        id = self.id

        employee_name = self.employee_name

        total_hours = self.total_hours

        gross_earnings = self.gross_earnings

        net_earnings = self.net_earnings

        taxable_earnings = self.taxable_earnings

        post_tax_deduction_amount = self.post_tax_deduction_amount

        pre_tax_deduction_amount = self.pre_tax_deduction_amount

        pay_condition_rule_set_name = self.pay_condition_rule_set_name

        employee_id = self.employee_id

        is_termination = self.is_termination

        notation = self.notation

        employee_start_date: Union[Unset, str] = UNSET
        if not isinstance(self.employee_start_date, Unset):
            employee_start_date = self.employee_start_date.isoformat()

        employee_external_reference_id = self.employee_external_reference_id

        is_excluded = self.is_excluded

        employee_external_id = self.employee_external_id

        bank_payments_total = self.bank_payments_total

        termination_date: Union[Unset, str] = UNSET
        if not isinstance(self.termination_date, Unset):
            termination_date = self.termination_date.isoformat()

        earliest_termination_date: Union[Unset, str] = UNSET
        if not isinstance(self.earliest_termination_date, Unset):
            earliest_termination_date = self.earliest_termination_date.isoformat()

        previous_termination_date: Union[Unset, str] = UNSET
        if not isinstance(self.previous_termination_date, Unset):
            previous_termination_date = self.previous_termination_date.isoformat()

        employee_expenses_total = self.employee_expenses_total

        employer_liabilities_total = self.employer_liabilities_total

        is_complete = self.is_complete

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if payg_withholding_amount is not UNSET:
            field_dict["paygWithholdingAmount"] = payg_withholding_amount
        if payg_withholding_percent is not UNSET:
            field_dict["paygWithholdingPercent"] = payg_withholding_percent
        if sfss_amount is not UNSET:
            field_dict["sfssAmount"] = sfss_amount
        if help_amount is not UNSET:
            field_dict["helpAmount"] = help_amount
        if super_contribution is not UNSET:
            field_dict["superContribution"] = super_contribution
        if employer_contribution is not UNSET:
            field_dict["employerContribution"] = employer_contribution
        if super_contribution_minus_super_adjustments is not UNSET:
            field_dict["superContributionMinusSuperAdjustments"] = super_contribution_minus_super_adjustments
        if all_super_contributions_total is not UNSET:
            field_dict["allSuperContributionsTotal"] = all_super_contributions_total
        if gross_plus_super is not UNSET:
            field_dict["grossPlusSuper"] = gross_plus_super
        if super_adjustments_amount is not UNSET:
            field_dict["superAdjustmentsAmount"] = super_adjustments_amount
        if salary_sacrifice_super_amount is not UNSET:
            field_dict["salarySacrificeSuperAmount"] = salary_sacrifice_super_amount
        if member_voluntary_super_amount is not UNSET:
            field_dict["memberVoluntarySuperAmount"] = member_voluntary_super_amount
        if non_super_deduction_total is not UNSET:
            field_dict["nonSuperDeductionTotal"] = non_super_deduction_total
        if super_payments_total is not UNSET:
            field_dict["superPaymentsTotal"] = super_payments_total
        if is_employee_under_18 is not UNSET:
            field_dict["isEmployeeUnder18"] = is_employee_under_18
        if employer_contribution_adjustments_amount is not UNSET:
            field_dict["employerContributionAdjustmentsAmount"] = employer_contribution_adjustments_amount
        if payg_adjustments_amount is not UNSET:
            field_dict["paygAdjustmentsAmount"] = payg_adjustments_amount
        if super_contributions_cap_applied is not UNSET:
            field_dict["superContributionsCapApplied"] = super_contributions_cap_applied
        if payg_payment_total is not UNSET:
            field_dict["paygPaymentTotal"] = payg_payment_total
        if id is not UNSET:
            field_dict["id"] = id
        if employee_name is not UNSET:
            field_dict["employeeName"] = employee_name
        if total_hours is not UNSET:
            field_dict["totalHours"] = total_hours
        if gross_earnings is not UNSET:
            field_dict["grossEarnings"] = gross_earnings
        if net_earnings is not UNSET:
            field_dict["netEarnings"] = net_earnings
        if taxable_earnings is not UNSET:
            field_dict["taxableEarnings"] = taxable_earnings
        if post_tax_deduction_amount is not UNSET:
            field_dict["postTaxDeductionAmount"] = post_tax_deduction_amount
        if pre_tax_deduction_amount is not UNSET:
            field_dict["preTaxDeductionAmount"] = pre_tax_deduction_amount
        if pay_condition_rule_set_name is not UNSET:
            field_dict["payConditionRuleSetName"] = pay_condition_rule_set_name
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if is_termination is not UNSET:
            field_dict["isTermination"] = is_termination
        if notation is not UNSET:
            field_dict["notation"] = notation
        if employee_start_date is not UNSET:
            field_dict["employeeStartDate"] = employee_start_date
        if employee_external_reference_id is not UNSET:
            field_dict["employeeExternalReferenceId"] = employee_external_reference_id
        if is_excluded is not UNSET:
            field_dict["isExcluded"] = is_excluded
        if employee_external_id is not UNSET:
            field_dict["employeeExternalId"] = employee_external_id
        if bank_payments_total is not UNSET:
            field_dict["bankPaymentsTotal"] = bank_payments_total
        if termination_date is not UNSET:
            field_dict["terminationDate"] = termination_date
        if earliest_termination_date is not UNSET:
            field_dict["earliestTerminationDate"] = earliest_termination_date
        if previous_termination_date is not UNSET:
            field_dict["previousTerminationDate"] = previous_termination_date
        if employee_expenses_total is not UNSET:
            field_dict["employeeExpensesTotal"] = employee_expenses_total
        if employer_liabilities_total is not UNSET:
            field_dict["employerLiabilitiesTotal"] = employer_liabilities_total
        if is_complete is not UNSET:
            field_dict["isComplete"] = is_complete

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        payg_withholding_amount = d.pop("paygWithholdingAmount", UNSET)

        payg_withholding_percent = d.pop("paygWithholdingPercent", UNSET)

        sfss_amount = d.pop("sfssAmount", UNSET)

        help_amount = d.pop("helpAmount", UNSET)

        super_contribution = d.pop("superContribution", UNSET)

        employer_contribution = d.pop("employerContribution", UNSET)

        super_contribution_minus_super_adjustments = d.pop("superContributionMinusSuperAdjustments", UNSET)

        all_super_contributions_total = d.pop("allSuperContributionsTotal", UNSET)

        gross_plus_super = d.pop("grossPlusSuper", UNSET)

        super_adjustments_amount = d.pop("superAdjustmentsAmount", UNSET)

        salary_sacrifice_super_amount = d.pop("salarySacrificeSuperAmount", UNSET)

        member_voluntary_super_amount = d.pop("memberVoluntarySuperAmount", UNSET)

        non_super_deduction_total = d.pop("nonSuperDeductionTotal", UNSET)

        super_payments_total = d.pop("superPaymentsTotal", UNSET)

        is_employee_under_18 = d.pop("isEmployeeUnder18", UNSET)

        employer_contribution_adjustments_amount = d.pop("employerContributionAdjustmentsAmount", UNSET)

        payg_adjustments_amount = d.pop("paygAdjustmentsAmount", UNSET)

        super_contributions_cap_applied = d.pop("superContributionsCapApplied", UNSET)

        payg_payment_total = d.pop("paygPaymentTotal", UNSET)

        id = d.pop("id", UNSET)

        employee_name = d.pop("employeeName", UNSET)

        total_hours = d.pop("totalHours", UNSET)

        gross_earnings = d.pop("grossEarnings", UNSET)

        net_earnings = d.pop("netEarnings", UNSET)

        taxable_earnings = d.pop("taxableEarnings", UNSET)

        post_tax_deduction_amount = d.pop("postTaxDeductionAmount", UNSET)

        pre_tax_deduction_amount = d.pop("preTaxDeductionAmount", UNSET)

        pay_condition_rule_set_name = d.pop("payConditionRuleSetName", UNSET)

        employee_id = d.pop("employeeId", UNSET)

        is_termination = d.pop("isTermination", UNSET)

        notation = d.pop("notation", UNSET)

        _employee_start_date = d.pop("employeeStartDate", UNSET)
        employee_start_date: Union[Unset, datetime.datetime]
        if isinstance(_employee_start_date, Unset):
            employee_start_date = UNSET
        else:
            employee_start_date = isoparse(_employee_start_date)

        employee_external_reference_id = d.pop("employeeExternalReferenceId", UNSET)

        is_excluded = d.pop("isExcluded", UNSET)

        employee_external_id = d.pop("employeeExternalId", UNSET)

        bank_payments_total = d.pop("bankPaymentsTotal", UNSET)

        _termination_date = d.pop("terminationDate", UNSET)
        termination_date: Union[Unset, datetime.datetime]
        if isinstance(_termination_date, Unset):
            termination_date = UNSET
        else:
            termination_date = isoparse(_termination_date)

        _earliest_termination_date = d.pop("earliestTerminationDate", UNSET)
        earliest_termination_date: Union[Unset, datetime.datetime]
        if isinstance(_earliest_termination_date, Unset):
            earliest_termination_date = UNSET
        else:
            earliest_termination_date = isoparse(_earliest_termination_date)

        _previous_termination_date = d.pop("previousTerminationDate", UNSET)
        previous_termination_date: Union[Unset, datetime.datetime]
        if isinstance(_previous_termination_date, Unset):
            previous_termination_date = UNSET
        else:
            previous_termination_date = isoparse(_previous_termination_date)

        employee_expenses_total = d.pop("employeeExpensesTotal", UNSET)

        employer_liabilities_total = d.pop("employerLiabilitiesTotal", UNSET)

        is_complete = d.pop("isComplete", UNSET)

        au_pay_run_total_detail_model = cls(
            payg_withholding_amount=payg_withholding_amount,
            payg_withholding_percent=payg_withholding_percent,
            sfss_amount=sfss_amount,
            help_amount=help_amount,
            super_contribution=super_contribution,
            employer_contribution=employer_contribution,
            super_contribution_minus_super_adjustments=super_contribution_minus_super_adjustments,
            all_super_contributions_total=all_super_contributions_total,
            gross_plus_super=gross_plus_super,
            super_adjustments_amount=super_adjustments_amount,
            salary_sacrifice_super_amount=salary_sacrifice_super_amount,
            member_voluntary_super_amount=member_voluntary_super_amount,
            non_super_deduction_total=non_super_deduction_total,
            super_payments_total=super_payments_total,
            is_employee_under_18=is_employee_under_18,
            employer_contribution_adjustments_amount=employer_contribution_adjustments_amount,
            payg_adjustments_amount=payg_adjustments_amount,
            super_contributions_cap_applied=super_contributions_cap_applied,
            payg_payment_total=payg_payment_total,
            id=id,
            employee_name=employee_name,
            total_hours=total_hours,
            gross_earnings=gross_earnings,
            net_earnings=net_earnings,
            taxable_earnings=taxable_earnings,
            post_tax_deduction_amount=post_tax_deduction_amount,
            pre_tax_deduction_amount=pre_tax_deduction_amount,
            pay_condition_rule_set_name=pay_condition_rule_set_name,
            employee_id=employee_id,
            is_termination=is_termination,
            notation=notation,
            employee_start_date=employee_start_date,
            employee_external_reference_id=employee_external_reference_id,
            is_excluded=is_excluded,
            employee_external_id=employee_external_id,
            bank_payments_total=bank_payments_total,
            termination_date=termination_date,
            earliest_termination_date=earliest_termination_date,
            previous_termination_date=previous_termination_date,
            employee_expenses_total=employee_expenses_total,
            employer_liabilities_total=employer_liabilities_total,
            is_complete=is_complete,
        )

        au_pay_run_total_detail_model.additional_properties = d
        return au_pay_run_total_detail_model

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
