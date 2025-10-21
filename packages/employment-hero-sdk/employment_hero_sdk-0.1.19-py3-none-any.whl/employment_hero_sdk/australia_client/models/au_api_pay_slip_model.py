from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.au_api_pay_slip_model_rate_unit_enum import AuApiPaySlipModelRateUnitEnum
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.api_employee_expense_grid_model import ApiEmployeeExpenseGridModel
    from ..models.api_pay_slip_deduction_model import ApiPaySlipDeductionModel
    from ..models.api_pay_slip_leave_model import ApiPaySlipLeaveModel
    from ..models.api_pay_slip_payg_adjustment_model import ApiPaySlipPaygAdjustmentModel
    from ..models.api_pay_slip_super_adjustment_model import ApiPaySlipSuperAdjustmentModel
    from ..models.api_pay_slip_super_payment_model import ApiPaySlipSuperPaymentModel
    from ..models.api_year_to_date_earnings_breakdown_model import ApiYearToDateEarningsBreakdownModel
    from ..models.au_api_pay_slip_bank_payment_model import AuApiPaySlipBankPaymentModel
    from ..models.au_api_pay_slip_earnings_line_model import AuApiPaySlipEarningsLineModel


T = TypeVar("T", bound="AuApiPaySlipModel")


@_attrs_define
class AuApiPaySlipModel:
    """
    Attributes:
        payg_adjustments (Union[Unset, List['ApiPaySlipPaygAdjustmentModel']]):
        super_adjustments (Union[Unset, List['ApiPaySlipSuperAdjustmentModel']]):
        super_payments (Union[Unset, List['ApiPaySlipSuperPaymentModel']]):
        bank_payments (Union[Unset, List['AuApiPaySlipBankPaymentModel']]):
        earnings_lines (Union[Unset, List['AuApiPaySlipEarningsLineModel']]):
        payg_withholding_amount (Union[Unset, float]):
        sfss_amount (Union[Unset, float]):
        help_amount (Union[Unset, float]):
        super_contribution (Union[Unset, float]):
        employee_postal_suburb_name (Union[Unset, str]):
        employee_postal_suburb_postcode (Union[Unset, str]):
        employee_postal_suburb_state (Union[Unset, str]):
        super_ytd (Union[Unset, float]):
        sfss_ytd (Union[Unset, float]):
        help_ytd (Union[Unset, float]):
        payg_ytd (Union[Unset, float]):
        abn (Union[Unset, str]):
        total_accrued_leave (Union[Unset, List['ApiPaySlipLeaveModel']]):
        accrued_leave (Union[Unset, List['ApiPaySlipLeaveModel']]):
        leave_taken (Union[Unset, List['ApiPaySlipLeaveModel']]):
        deductions (Union[Unset, List['ApiPaySlipDeductionModel']]):
        gross_ytd_details (Union[Unset, List['ApiYearToDateEarningsBreakdownModel']]):
        employee_expenses (Union[Unset, List['ApiEmployeeExpenseGridModel']]):
        total_hours (Union[Unset, float]):
        gross_earnings (Union[Unset, float]):
        net_earnings (Union[Unset, float]):
        taxable_earnings (Union[Unset, float]):
        post_tax_deduction_amount (Union[Unset, float]):
        pre_tax_deduction_amount (Union[Unset, float]):
        id (Union[Unset, int]):
        business_name (Union[Unset, str]):
        business_address (Union[Unset, str]):
        contact_name (Union[Unset, str]):
        pay_period_starting (Union[Unset, str]):
        pay_period_ending (Union[Unset, str]):
        message (Union[Unset, str]):
        employee_id (Union[Unset, int]):
        employee_external_id (Union[Unset, str]):
        employee_name (Union[Unset, str]):
        employee_first_name (Union[Unset, str]):
        employee_surname (Union[Unset, str]):
        employee_postal_street_address (Union[Unset, str]):
        employee_postal_address_line_2 (Union[Unset, str]):
        employee_postal_address_country (Union[Unset, str]):
        notation (Union[Unset, str]):
        is_published (Union[Unset, bool]):
        gross_ytd (Union[Unset, float]):
        net_ytd (Union[Unset, float]):
        withholding_ytd (Union[Unset, float]):
        base_pay_rate (Union[Unset, str]):
        base_rate (Union[Unset, str]):
        hourly_rate (Union[Unset, float]):
        pre_tax_deductions_ytd (Union[Unset, float]):
        post_tax_deductions_ytd (Union[Unset, float]):
        employee_base_rate (Union[Unset, float]):
        employee_base_rate_unit (Union[Unset, AuApiPaySlipModelRateUnitEnum]):
    """

    payg_adjustments: Union[Unset, List["ApiPaySlipPaygAdjustmentModel"]] = UNSET
    super_adjustments: Union[Unset, List["ApiPaySlipSuperAdjustmentModel"]] = UNSET
    super_payments: Union[Unset, List["ApiPaySlipSuperPaymentModel"]] = UNSET
    bank_payments: Union[Unset, List["AuApiPaySlipBankPaymentModel"]] = UNSET
    earnings_lines: Union[Unset, List["AuApiPaySlipEarningsLineModel"]] = UNSET
    payg_withholding_amount: Union[Unset, float] = UNSET
    sfss_amount: Union[Unset, float] = UNSET
    help_amount: Union[Unset, float] = UNSET
    super_contribution: Union[Unset, float] = UNSET
    employee_postal_suburb_name: Union[Unset, str] = UNSET
    employee_postal_suburb_postcode: Union[Unset, str] = UNSET
    employee_postal_suburb_state: Union[Unset, str] = UNSET
    super_ytd: Union[Unset, float] = UNSET
    sfss_ytd: Union[Unset, float] = UNSET
    help_ytd: Union[Unset, float] = UNSET
    payg_ytd: Union[Unset, float] = UNSET
    abn: Union[Unset, str] = UNSET
    total_accrued_leave: Union[Unset, List["ApiPaySlipLeaveModel"]] = UNSET
    accrued_leave: Union[Unset, List["ApiPaySlipLeaveModel"]] = UNSET
    leave_taken: Union[Unset, List["ApiPaySlipLeaveModel"]] = UNSET
    deductions: Union[Unset, List["ApiPaySlipDeductionModel"]] = UNSET
    gross_ytd_details: Union[Unset, List["ApiYearToDateEarningsBreakdownModel"]] = UNSET
    employee_expenses: Union[Unset, List["ApiEmployeeExpenseGridModel"]] = UNSET
    total_hours: Union[Unset, float] = UNSET
    gross_earnings: Union[Unset, float] = UNSET
    net_earnings: Union[Unset, float] = UNSET
    taxable_earnings: Union[Unset, float] = UNSET
    post_tax_deduction_amount: Union[Unset, float] = UNSET
    pre_tax_deduction_amount: Union[Unset, float] = UNSET
    id: Union[Unset, int] = UNSET
    business_name: Union[Unset, str] = UNSET
    business_address: Union[Unset, str] = UNSET
    contact_name: Union[Unset, str] = UNSET
    pay_period_starting: Union[Unset, str] = UNSET
    pay_period_ending: Union[Unset, str] = UNSET
    message: Union[Unset, str] = UNSET
    employee_id: Union[Unset, int] = UNSET
    employee_external_id: Union[Unset, str] = UNSET
    employee_name: Union[Unset, str] = UNSET
    employee_first_name: Union[Unset, str] = UNSET
    employee_surname: Union[Unset, str] = UNSET
    employee_postal_street_address: Union[Unset, str] = UNSET
    employee_postal_address_line_2: Union[Unset, str] = UNSET
    employee_postal_address_country: Union[Unset, str] = UNSET
    notation: Union[Unset, str] = UNSET
    is_published: Union[Unset, bool] = UNSET
    gross_ytd: Union[Unset, float] = UNSET
    net_ytd: Union[Unset, float] = UNSET
    withholding_ytd: Union[Unset, float] = UNSET
    base_pay_rate: Union[Unset, str] = UNSET
    base_rate: Union[Unset, str] = UNSET
    hourly_rate: Union[Unset, float] = UNSET
    pre_tax_deductions_ytd: Union[Unset, float] = UNSET
    post_tax_deductions_ytd: Union[Unset, float] = UNSET
    employee_base_rate: Union[Unset, float] = UNSET
    employee_base_rate_unit: Union[Unset, AuApiPaySlipModelRateUnitEnum] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        payg_adjustments: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.payg_adjustments, Unset):
            payg_adjustments = []
            for payg_adjustments_item_data in self.payg_adjustments:
                payg_adjustments_item = payg_adjustments_item_data.to_dict()
                payg_adjustments.append(payg_adjustments_item)

        super_adjustments: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.super_adjustments, Unset):
            super_adjustments = []
            for super_adjustments_item_data in self.super_adjustments:
                super_adjustments_item = super_adjustments_item_data.to_dict()
                super_adjustments.append(super_adjustments_item)

        super_payments: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.super_payments, Unset):
            super_payments = []
            for super_payments_item_data in self.super_payments:
                super_payments_item = super_payments_item_data.to_dict()
                super_payments.append(super_payments_item)

        bank_payments: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.bank_payments, Unset):
            bank_payments = []
            for bank_payments_item_data in self.bank_payments:
                bank_payments_item = bank_payments_item_data.to_dict()
                bank_payments.append(bank_payments_item)

        earnings_lines: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.earnings_lines, Unset):
            earnings_lines = []
            for earnings_lines_item_data in self.earnings_lines:
                earnings_lines_item = earnings_lines_item_data.to_dict()
                earnings_lines.append(earnings_lines_item)

        payg_withholding_amount = self.payg_withholding_amount

        sfss_amount = self.sfss_amount

        help_amount = self.help_amount

        super_contribution = self.super_contribution

        employee_postal_suburb_name = self.employee_postal_suburb_name

        employee_postal_suburb_postcode = self.employee_postal_suburb_postcode

        employee_postal_suburb_state = self.employee_postal_suburb_state

        super_ytd = self.super_ytd

        sfss_ytd = self.sfss_ytd

        help_ytd = self.help_ytd

        payg_ytd = self.payg_ytd

        abn = self.abn

        total_accrued_leave: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.total_accrued_leave, Unset):
            total_accrued_leave = []
            for total_accrued_leave_item_data in self.total_accrued_leave:
                total_accrued_leave_item = total_accrued_leave_item_data.to_dict()
                total_accrued_leave.append(total_accrued_leave_item)

        accrued_leave: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.accrued_leave, Unset):
            accrued_leave = []
            for accrued_leave_item_data in self.accrued_leave:
                accrued_leave_item = accrued_leave_item_data.to_dict()
                accrued_leave.append(accrued_leave_item)

        leave_taken: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.leave_taken, Unset):
            leave_taken = []
            for leave_taken_item_data in self.leave_taken:
                leave_taken_item = leave_taken_item_data.to_dict()
                leave_taken.append(leave_taken_item)

        deductions: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.deductions, Unset):
            deductions = []
            for deductions_item_data in self.deductions:
                deductions_item = deductions_item_data.to_dict()
                deductions.append(deductions_item)

        gross_ytd_details: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.gross_ytd_details, Unset):
            gross_ytd_details = []
            for gross_ytd_details_item_data in self.gross_ytd_details:
                gross_ytd_details_item = gross_ytd_details_item_data.to_dict()
                gross_ytd_details.append(gross_ytd_details_item)

        employee_expenses: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.employee_expenses, Unset):
            employee_expenses = []
            for employee_expenses_item_data in self.employee_expenses:
                employee_expenses_item = employee_expenses_item_data.to_dict()
                employee_expenses.append(employee_expenses_item)

        total_hours = self.total_hours

        gross_earnings = self.gross_earnings

        net_earnings = self.net_earnings

        taxable_earnings = self.taxable_earnings

        post_tax_deduction_amount = self.post_tax_deduction_amount

        pre_tax_deduction_amount = self.pre_tax_deduction_amount

        id = self.id

        business_name = self.business_name

        business_address = self.business_address

        contact_name = self.contact_name

        pay_period_starting = self.pay_period_starting

        pay_period_ending = self.pay_period_ending

        message = self.message

        employee_id = self.employee_id

        employee_external_id = self.employee_external_id

        employee_name = self.employee_name

        employee_first_name = self.employee_first_name

        employee_surname = self.employee_surname

        employee_postal_street_address = self.employee_postal_street_address

        employee_postal_address_line_2 = self.employee_postal_address_line_2

        employee_postal_address_country = self.employee_postal_address_country

        notation = self.notation

        is_published = self.is_published

        gross_ytd = self.gross_ytd

        net_ytd = self.net_ytd

        withholding_ytd = self.withholding_ytd

        base_pay_rate = self.base_pay_rate

        base_rate = self.base_rate

        hourly_rate = self.hourly_rate

        pre_tax_deductions_ytd = self.pre_tax_deductions_ytd

        post_tax_deductions_ytd = self.post_tax_deductions_ytd

        employee_base_rate = self.employee_base_rate

        employee_base_rate_unit: Union[Unset, str] = UNSET
        if not isinstance(self.employee_base_rate_unit, Unset):
            employee_base_rate_unit = self.employee_base_rate_unit.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if payg_adjustments is not UNSET:
            field_dict["paygAdjustments"] = payg_adjustments
        if super_adjustments is not UNSET:
            field_dict["superAdjustments"] = super_adjustments
        if super_payments is not UNSET:
            field_dict["superPayments"] = super_payments
        if bank_payments is not UNSET:
            field_dict["bankPayments"] = bank_payments
        if earnings_lines is not UNSET:
            field_dict["earningsLines"] = earnings_lines
        if payg_withholding_amount is not UNSET:
            field_dict["paygWithholdingAmount"] = payg_withholding_amount
        if sfss_amount is not UNSET:
            field_dict["sfssAmount"] = sfss_amount
        if help_amount is not UNSET:
            field_dict["helpAmount"] = help_amount
        if super_contribution is not UNSET:
            field_dict["superContribution"] = super_contribution
        if employee_postal_suburb_name is not UNSET:
            field_dict["employeePostalSuburbName"] = employee_postal_suburb_name
        if employee_postal_suburb_postcode is not UNSET:
            field_dict["employeePostalSuburbPostcode"] = employee_postal_suburb_postcode
        if employee_postal_suburb_state is not UNSET:
            field_dict["employeePostalSuburbState"] = employee_postal_suburb_state
        if super_ytd is not UNSET:
            field_dict["superYTD"] = super_ytd
        if sfss_ytd is not UNSET:
            field_dict["sfssYTD"] = sfss_ytd
        if help_ytd is not UNSET:
            field_dict["helpYTD"] = help_ytd
        if payg_ytd is not UNSET:
            field_dict["paygYTD"] = payg_ytd
        if abn is not UNSET:
            field_dict["abn"] = abn
        if total_accrued_leave is not UNSET:
            field_dict["totalAccruedLeave"] = total_accrued_leave
        if accrued_leave is not UNSET:
            field_dict["accruedLeave"] = accrued_leave
        if leave_taken is not UNSET:
            field_dict["leaveTaken"] = leave_taken
        if deductions is not UNSET:
            field_dict["deductions"] = deductions
        if gross_ytd_details is not UNSET:
            field_dict["grossYTDDetails"] = gross_ytd_details
        if employee_expenses is not UNSET:
            field_dict["employeeExpenses"] = employee_expenses
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
        if id is not UNSET:
            field_dict["id"] = id
        if business_name is not UNSET:
            field_dict["businessName"] = business_name
        if business_address is not UNSET:
            field_dict["businessAddress"] = business_address
        if contact_name is not UNSET:
            field_dict["contactName"] = contact_name
        if pay_period_starting is not UNSET:
            field_dict["payPeriodStarting"] = pay_period_starting
        if pay_period_ending is not UNSET:
            field_dict["payPeriodEnding"] = pay_period_ending
        if message is not UNSET:
            field_dict["message"] = message
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if employee_external_id is not UNSET:
            field_dict["employeeExternalId"] = employee_external_id
        if employee_name is not UNSET:
            field_dict["employeeName"] = employee_name
        if employee_first_name is not UNSET:
            field_dict["employeeFirstName"] = employee_first_name
        if employee_surname is not UNSET:
            field_dict["employeeSurname"] = employee_surname
        if employee_postal_street_address is not UNSET:
            field_dict["employeePostalStreetAddress"] = employee_postal_street_address
        if employee_postal_address_line_2 is not UNSET:
            field_dict["employeePostalAddressLine2"] = employee_postal_address_line_2
        if employee_postal_address_country is not UNSET:
            field_dict["employeePostalAddressCountry"] = employee_postal_address_country
        if notation is not UNSET:
            field_dict["notation"] = notation
        if is_published is not UNSET:
            field_dict["isPublished"] = is_published
        if gross_ytd is not UNSET:
            field_dict["grossYTD"] = gross_ytd
        if net_ytd is not UNSET:
            field_dict["netYTD"] = net_ytd
        if withholding_ytd is not UNSET:
            field_dict["withholdingYTD"] = withholding_ytd
        if base_pay_rate is not UNSET:
            field_dict["basePayRate"] = base_pay_rate
        if base_rate is not UNSET:
            field_dict["baseRate"] = base_rate
        if hourly_rate is not UNSET:
            field_dict["hourlyRate"] = hourly_rate
        if pre_tax_deductions_ytd is not UNSET:
            field_dict["preTaxDeductionsYTD"] = pre_tax_deductions_ytd
        if post_tax_deductions_ytd is not UNSET:
            field_dict["postTaxDeductionsYTD"] = post_tax_deductions_ytd
        if employee_base_rate is not UNSET:
            field_dict["employeeBaseRate"] = employee_base_rate
        if employee_base_rate_unit is not UNSET:
            field_dict["employeeBaseRateUnit"] = employee_base_rate_unit

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.api_employee_expense_grid_model import ApiEmployeeExpenseGridModel
        from ..models.api_pay_slip_deduction_model import ApiPaySlipDeductionModel
        from ..models.api_pay_slip_leave_model import ApiPaySlipLeaveModel
        from ..models.api_pay_slip_payg_adjustment_model import ApiPaySlipPaygAdjustmentModel
        from ..models.api_pay_slip_super_adjustment_model import ApiPaySlipSuperAdjustmentModel
        from ..models.api_pay_slip_super_payment_model import ApiPaySlipSuperPaymentModel
        from ..models.api_year_to_date_earnings_breakdown_model import ApiYearToDateEarningsBreakdownModel
        from ..models.au_api_pay_slip_bank_payment_model import AuApiPaySlipBankPaymentModel
        from ..models.au_api_pay_slip_earnings_line_model import AuApiPaySlipEarningsLineModel

        d = src_dict.copy()
        payg_adjustments = []
        _payg_adjustments = d.pop("paygAdjustments", UNSET)
        for payg_adjustments_item_data in _payg_adjustments or []:
            payg_adjustments_item = ApiPaySlipPaygAdjustmentModel.from_dict(payg_adjustments_item_data)

            payg_adjustments.append(payg_adjustments_item)

        super_adjustments = []
        _super_adjustments = d.pop("superAdjustments", UNSET)
        for super_adjustments_item_data in _super_adjustments or []:
            super_adjustments_item = ApiPaySlipSuperAdjustmentModel.from_dict(super_adjustments_item_data)

            super_adjustments.append(super_adjustments_item)

        super_payments = []
        _super_payments = d.pop("superPayments", UNSET)
        for super_payments_item_data in _super_payments or []:
            super_payments_item = ApiPaySlipSuperPaymentModel.from_dict(super_payments_item_data)

            super_payments.append(super_payments_item)

        bank_payments = []
        _bank_payments = d.pop("bankPayments", UNSET)
        for bank_payments_item_data in _bank_payments or []:
            bank_payments_item = AuApiPaySlipBankPaymentModel.from_dict(bank_payments_item_data)

            bank_payments.append(bank_payments_item)

        earnings_lines = []
        _earnings_lines = d.pop("earningsLines", UNSET)
        for earnings_lines_item_data in _earnings_lines or []:
            earnings_lines_item = AuApiPaySlipEarningsLineModel.from_dict(earnings_lines_item_data)

            earnings_lines.append(earnings_lines_item)

        payg_withholding_amount = d.pop("paygWithholdingAmount", UNSET)

        sfss_amount = d.pop("sfssAmount", UNSET)

        help_amount = d.pop("helpAmount", UNSET)

        super_contribution = d.pop("superContribution", UNSET)

        employee_postal_suburb_name = d.pop("employeePostalSuburbName", UNSET)

        employee_postal_suburb_postcode = d.pop("employeePostalSuburbPostcode", UNSET)

        employee_postal_suburb_state = d.pop("employeePostalSuburbState", UNSET)

        super_ytd = d.pop("superYTD", UNSET)

        sfss_ytd = d.pop("sfssYTD", UNSET)

        help_ytd = d.pop("helpYTD", UNSET)

        payg_ytd = d.pop("paygYTD", UNSET)

        abn = d.pop("abn", UNSET)

        total_accrued_leave = []
        _total_accrued_leave = d.pop("totalAccruedLeave", UNSET)
        for total_accrued_leave_item_data in _total_accrued_leave or []:
            total_accrued_leave_item = ApiPaySlipLeaveModel.from_dict(total_accrued_leave_item_data)

            total_accrued_leave.append(total_accrued_leave_item)

        accrued_leave = []
        _accrued_leave = d.pop("accruedLeave", UNSET)
        for accrued_leave_item_data in _accrued_leave or []:
            accrued_leave_item = ApiPaySlipLeaveModel.from_dict(accrued_leave_item_data)

            accrued_leave.append(accrued_leave_item)

        leave_taken = []
        _leave_taken = d.pop("leaveTaken", UNSET)
        for leave_taken_item_data in _leave_taken or []:
            leave_taken_item = ApiPaySlipLeaveModel.from_dict(leave_taken_item_data)

            leave_taken.append(leave_taken_item)

        deductions = []
        _deductions = d.pop("deductions", UNSET)
        for deductions_item_data in _deductions or []:
            deductions_item = ApiPaySlipDeductionModel.from_dict(deductions_item_data)

            deductions.append(deductions_item)

        gross_ytd_details = []
        _gross_ytd_details = d.pop("grossYTDDetails", UNSET)
        for gross_ytd_details_item_data in _gross_ytd_details or []:
            gross_ytd_details_item = ApiYearToDateEarningsBreakdownModel.from_dict(gross_ytd_details_item_data)

            gross_ytd_details.append(gross_ytd_details_item)

        employee_expenses = []
        _employee_expenses = d.pop("employeeExpenses", UNSET)
        for employee_expenses_item_data in _employee_expenses or []:
            employee_expenses_item = ApiEmployeeExpenseGridModel.from_dict(employee_expenses_item_data)

            employee_expenses.append(employee_expenses_item)

        total_hours = d.pop("totalHours", UNSET)

        gross_earnings = d.pop("grossEarnings", UNSET)

        net_earnings = d.pop("netEarnings", UNSET)

        taxable_earnings = d.pop("taxableEarnings", UNSET)

        post_tax_deduction_amount = d.pop("postTaxDeductionAmount", UNSET)

        pre_tax_deduction_amount = d.pop("preTaxDeductionAmount", UNSET)

        id = d.pop("id", UNSET)

        business_name = d.pop("businessName", UNSET)

        business_address = d.pop("businessAddress", UNSET)

        contact_name = d.pop("contactName", UNSET)

        pay_period_starting = d.pop("payPeriodStarting", UNSET)

        pay_period_ending = d.pop("payPeriodEnding", UNSET)

        message = d.pop("message", UNSET)

        employee_id = d.pop("employeeId", UNSET)

        employee_external_id = d.pop("employeeExternalId", UNSET)

        employee_name = d.pop("employeeName", UNSET)

        employee_first_name = d.pop("employeeFirstName", UNSET)

        employee_surname = d.pop("employeeSurname", UNSET)

        employee_postal_street_address = d.pop("employeePostalStreetAddress", UNSET)

        employee_postal_address_line_2 = d.pop("employeePostalAddressLine2", UNSET)

        employee_postal_address_country = d.pop("employeePostalAddressCountry", UNSET)

        notation = d.pop("notation", UNSET)

        is_published = d.pop("isPublished", UNSET)

        gross_ytd = d.pop("grossYTD", UNSET)

        net_ytd = d.pop("netYTD", UNSET)

        withholding_ytd = d.pop("withholdingYTD", UNSET)

        base_pay_rate = d.pop("basePayRate", UNSET)

        base_rate = d.pop("baseRate", UNSET)

        hourly_rate = d.pop("hourlyRate", UNSET)

        pre_tax_deductions_ytd = d.pop("preTaxDeductionsYTD", UNSET)

        post_tax_deductions_ytd = d.pop("postTaxDeductionsYTD", UNSET)

        employee_base_rate = d.pop("employeeBaseRate", UNSET)

        _employee_base_rate_unit = d.pop("employeeBaseRateUnit", UNSET)
        employee_base_rate_unit: Union[Unset, AuApiPaySlipModelRateUnitEnum]
        if isinstance(_employee_base_rate_unit, Unset):
            employee_base_rate_unit = UNSET
        else:
            employee_base_rate_unit = AuApiPaySlipModelRateUnitEnum(_employee_base_rate_unit)

        au_api_pay_slip_model = cls(
            payg_adjustments=payg_adjustments,
            super_adjustments=super_adjustments,
            super_payments=super_payments,
            bank_payments=bank_payments,
            earnings_lines=earnings_lines,
            payg_withholding_amount=payg_withholding_amount,
            sfss_amount=sfss_amount,
            help_amount=help_amount,
            super_contribution=super_contribution,
            employee_postal_suburb_name=employee_postal_suburb_name,
            employee_postal_suburb_postcode=employee_postal_suburb_postcode,
            employee_postal_suburb_state=employee_postal_suburb_state,
            super_ytd=super_ytd,
            sfss_ytd=sfss_ytd,
            help_ytd=help_ytd,
            payg_ytd=payg_ytd,
            abn=abn,
            total_accrued_leave=total_accrued_leave,
            accrued_leave=accrued_leave,
            leave_taken=leave_taken,
            deductions=deductions,
            gross_ytd_details=gross_ytd_details,
            employee_expenses=employee_expenses,
            total_hours=total_hours,
            gross_earnings=gross_earnings,
            net_earnings=net_earnings,
            taxable_earnings=taxable_earnings,
            post_tax_deduction_amount=post_tax_deduction_amount,
            pre_tax_deduction_amount=pre_tax_deduction_amount,
            id=id,
            business_name=business_name,
            business_address=business_address,
            contact_name=contact_name,
            pay_period_starting=pay_period_starting,
            pay_period_ending=pay_period_ending,
            message=message,
            employee_id=employee_id,
            employee_external_id=employee_external_id,
            employee_name=employee_name,
            employee_first_name=employee_first_name,
            employee_surname=employee_surname,
            employee_postal_street_address=employee_postal_street_address,
            employee_postal_address_line_2=employee_postal_address_line_2,
            employee_postal_address_country=employee_postal_address_country,
            notation=notation,
            is_published=is_published,
            gross_ytd=gross_ytd,
            net_ytd=net_ytd,
            withholding_ytd=withholding_ytd,
            base_pay_rate=base_pay_rate,
            base_rate=base_rate,
            hourly_rate=hourly_rate,
            pre_tax_deductions_ytd=pre_tax_deductions_ytd,
            post_tax_deductions_ytd=post_tax_deductions_ytd,
            employee_base_rate=employee_base_rate,
            employee_base_rate_unit=employee_base_rate_unit,
        )

        au_api_pay_slip_model.additional_properties = d
        return au_api_pay_slip_model

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
