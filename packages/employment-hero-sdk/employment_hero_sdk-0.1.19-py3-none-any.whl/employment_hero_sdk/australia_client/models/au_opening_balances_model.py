from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.au_initial_deduction_model import AuInitialDeductionModel
    from ..models.au_initial_earnings_model import AuInitialEarningsModel
    from ..models.initial_employer_liability_model import InitialEmployerLiabilityModel
    from ..models.initial_leave_balance_model import InitialLeaveBalanceModel
    from ..models.opening_balances_etp_model import OpeningBalancesEtpModel


T = TypeVar("T", bound="AuOpeningBalancesModel")


@_attrs_define
class AuOpeningBalancesModel:
    """
    Attributes:
        deductions (Union[Unset, List['AuInitialDeductionModel']]):
        payg_withholding_amount (Union[Unset, float]):
        method_b2_payg_withholding_amount (Union[Unset, float]):
        sfss_amount (Union[Unset, float]):
        help_amount (Union[Unset, float]):
        super_contribution (Union[Unset, float]):
        employer_contribution (Union[Unset, float]):
        non_resc_employer_contribution (Union[Unset, float]):
        earnings_lines (Union[Unset, List['AuInitialEarningsModel']]):
        etps (Union[Unset, List['OpeningBalancesEtpModel']]):
        employee_id (Union[Unset, int]):
        total_hours (Union[Unset, float]):
        gross_earnings (Union[Unset, float]):
        leave_balances (Union[Unset, List['InitialLeaveBalanceModel']]):
        employer_liabilities (Union[Unset, List['InitialEmployerLiabilityModel']]):
        financial_year_starting_year (Union[Unset, int]):
        location_name (Union[Unset, str]):
    """

    deductions: Union[Unset, List["AuInitialDeductionModel"]] = UNSET
    payg_withholding_amount: Union[Unset, float] = UNSET
    method_b2_payg_withholding_amount: Union[Unset, float] = UNSET
    sfss_amount: Union[Unset, float] = UNSET
    help_amount: Union[Unset, float] = UNSET
    super_contribution: Union[Unset, float] = UNSET
    employer_contribution: Union[Unset, float] = UNSET
    non_resc_employer_contribution: Union[Unset, float] = UNSET
    earnings_lines: Union[Unset, List["AuInitialEarningsModel"]] = UNSET
    etps: Union[Unset, List["OpeningBalancesEtpModel"]] = UNSET
    employee_id: Union[Unset, int] = UNSET
    total_hours: Union[Unset, float] = UNSET
    gross_earnings: Union[Unset, float] = UNSET
    leave_balances: Union[Unset, List["InitialLeaveBalanceModel"]] = UNSET
    employer_liabilities: Union[Unset, List["InitialEmployerLiabilityModel"]] = UNSET
    financial_year_starting_year: Union[Unset, int] = UNSET
    location_name: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        deductions: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.deductions, Unset):
            deductions = []
            for deductions_item_data in self.deductions:
                deductions_item = deductions_item_data.to_dict()
                deductions.append(deductions_item)

        payg_withholding_amount = self.payg_withholding_amount

        method_b2_payg_withholding_amount = self.method_b2_payg_withholding_amount

        sfss_amount = self.sfss_amount

        help_amount = self.help_amount

        super_contribution = self.super_contribution

        employer_contribution = self.employer_contribution

        non_resc_employer_contribution = self.non_resc_employer_contribution

        earnings_lines: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.earnings_lines, Unset):
            earnings_lines = []
            for earnings_lines_item_data in self.earnings_lines:
                earnings_lines_item = earnings_lines_item_data.to_dict()
                earnings_lines.append(earnings_lines_item)

        etps: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.etps, Unset):
            etps = []
            for etps_item_data in self.etps:
                etps_item = etps_item_data.to_dict()
                etps.append(etps_item)

        employee_id = self.employee_id

        total_hours = self.total_hours

        gross_earnings = self.gross_earnings

        leave_balances: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.leave_balances, Unset):
            leave_balances = []
            for leave_balances_item_data in self.leave_balances:
                leave_balances_item = leave_balances_item_data.to_dict()
                leave_balances.append(leave_balances_item)

        employer_liabilities: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.employer_liabilities, Unset):
            employer_liabilities = []
            for employer_liabilities_item_data in self.employer_liabilities:
                employer_liabilities_item = employer_liabilities_item_data.to_dict()
                employer_liabilities.append(employer_liabilities_item)

        financial_year_starting_year = self.financial_year_starting_year

        location_name = self.location_name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if deductions is not UNSET:
            field_dict["deductions"] = deductions
        if payg_withholding_amount is not UNSET:
            field_dict["paygWithholdingAmount"] = payg_withholding_amount
        if method_b2_payg_withholding_amount is not UNSET:
            field_dict["methodB2PaygWithholdingAmount"] = method_b2_payg_withholding_amount
        if sfss_amount is not UNSET:
            field_dict["sfssAmount"] = sfss_amount
        if help_amount is not UNSET:
            field_dict["helpAmount"] = help_amount
        if super_contribution is not UNSET:
            field_dict["superContribution"] = super_contribution
        if employer_contribution is not UNSET:
            field_dict["employerContribution"] = employer_contribution
        if non_resc_employer_contribution is not UNSET:
            field_dict["nonRescEmployerContribution"] = non_resc_employer_contribution
        if earnings_lines is not UNSET:
            field_dict["earningsLines"] = earnings_lines
        if etps is not UNSET:
            field_dict["etps"] = etps
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if total_hours is not UNSET:
            field_dict["totalHours"] = total_hours
        if gross_earnings is not UNSET:
            field_dict["grossEarnings"] = gross_earnings
        if leave_balances is not UNSET:
            field_dict["leaveBalances"] = leave_balances
        if employer_liabilities is not UNSET:
            field_dict["employerLiabilities"] = employer_liabilities
        if financial_year_starting_year is not UNSET:
            field_dict["financialYearStartingYear"] = financial_year_starting_year
        if location_name is not UNSET:
            field_dict["locationName"] = location_name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.au_initial_deduction_model import AuInitialDeductionModel
        from ..models.au_initial_earnings_model import AuInitialEarningsModel
        from ..models.initial_employer_liability_model import InitialEmployerLiabilityModel
        from ..models.initial_leave_balance_model import InitialLeaveBalanceModel
        from ..models.opening_balances_etp_model import OpeningBalancesEtpModel

        d = src_dict.copy()
        deductions = []
        _deductions = d.pop("deductions", UNSET)
        for deductions_item_data in _deductions or []:
            deductions_item = AuInitialDeductionModel.from_dict(deductions_item_data)

            deductions.append(deductions_item)

        payg_withholding_amount = d.pop("paygWithholdingAmount", UNSET)

        method_b2_payg_withholding_amount = d.pop("methodB2PaygWithholdingAmount", UNSET)

        sfss_amount = d.pop("sfssAmount", UNSET)

        help_amount = d.pop("helpAmount", UNSET)

        super_contribution = d.pop("superContribution", UNSET)

        employer_contribution = d.pop("employerContribution", UNSET)

        non_resc_employer_contribution = d.pop("nonRescEmployerContribution", UNSET)

        earnings_lines = []
        _earnings_lines = d.pop("earningsLines", UNSET)
        for earnings_lines_item_data in _earnings_lines or []:
            earnings_lines_item = AuInitialEarningsModel.from_dict(earnings_lines_item_data)

            earnings_lines.append(earnings_lines_item)

        etps = []
        _etps = d.pop("etps", UNSET)
        for etps_item_data in _etps or []:
            etps_item = OpeningBalancesEtpModel.from_dict(etps_item_data)

            etps.append(etps_item)

        employee_id = d.pop("employeeId", UNSET)

        total_hours = d.pop("totalHours", UNSET)

        gross_earnings = d.pop("grossEarnings", UNSET)

        leave_balances = []
        _leave_balances = d.pop("leaveBalances", UNSET)
        for leave_balances_item_data in _leave_balances or []:
            leave_balances_item = InitialLeaveBalanceModel.from_dict(leave_balances_item_data)

            leave_balances.append(leave_balances_item)

        employer_liabilities = []
        _employer_liabilities = d.pop("employerLiabilities", UNSET)
        for employer_liabilities_item_data in _employer_liabilities or []:
            employer_liabilities_item = InitialEmployerLiabilityModel.from_dict(employer_liabilities_item_data)

            employer_liabilities.append(employer_liabilities_item)

        financial_year_starting_year = d.pop("financialYearStartingYear", UNSET)

        location_name = d.pop("locationName", UNSET)

        au_opening_balances_model = cls(
            deductions=deductions,
            payg_withholding_amount=payg_withholding_amount,
            method_b2_payg_withholding_amount=method_b2_payg_withholding_amount,
            sfss_amount=sfss_amount,
            help_amount=help_amount,
            super_contribution=super_contribution,
            employer_contribution=employer_contribution,
            non_resc_employer_contribution=non_resc_employer_contribution,
            earnings_lines=earnings_lines,
            etps=etps,
            employee_id=employee_id,
            total_hours=total_hours,
            gross_earnings=gross_earnings,
            leave_balances=leave_balances,
            employer_liabilities=employer_liabilities,
            financial_year_starting_year=financial_year_starting_year,
            location_name=location_name,
        )

        au_opening_balances_model.additional_properties = d
        return au_opening_balances_model

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
