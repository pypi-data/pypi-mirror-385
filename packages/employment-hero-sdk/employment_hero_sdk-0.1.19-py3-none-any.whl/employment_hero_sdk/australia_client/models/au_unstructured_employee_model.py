import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.au_unstructured_employee_model_employee_status_enum import AuUnstructuredEmployeeModelEmployeeStatusEnum
from ..models.au_unstructured_employee_model_nullable_closely_held_reporting_enum import (
    AuUnstructuredEmployeeModelNullableCloselyHeldReportingEnum,
)
from ..models.au_unstructured_employee_model_nullable_leave_accrual_start_date_type import (
    AuUnstructuredEmployeeModelNullableLeaveAccrualStartDateType,
)
from ..models.au_unstructured_employee_model_nullable_medicare_levy_surcharge_withholding_tier import (
    AuUnstructuredEmployeeModelNullableMedicareLevySurchargeWithholdingTier,
)
from ..models.au_unstructured_employee_model_nullable_stp_income_type_enum import (
    AuUnstructuredEmployeeModelNullableStpIncomeTypeEnum,
)
from ..models.au_unstructured_employee_model_nullable_tax_file_declaration_tax_category_combination import (
    AuUnstructuredEmployeeModelNullableTaxFileDeclarationTaxCategoryCombination,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="AuUnstructuredEmployeeModel")


@_attrs_define
class AuUnstructuredEmployeeModel:
    """
    Attributes:
        tax_file_number (Union[Unset, str]):
        residential_suburb (Union[Unset, str]):
        residential_state (Union[Unset, str]):
        postal_suburb (Union[Unset, str]):
        postal_state (Union[Unset, str]):
        employing_entity_abn (Union[Unset, str]):
        employing_entity_id (Union[Unset, str]):
        previous_surname (Union[Unset, str]):
        australian_resident (Union[Unset, bool]):
        claim_tax_free_threshold (Union[Unset, bool]):
        seniors_tax_offset (Union[Unset, bool]):
        other_tax_offset (Union[Unset, bool]):
        stsl_debt (Union[Unset, bool]):
        is_exempt_from_flood_levy (Union[Unset, bool]):
        has_approved_working_holiday_visa (Union[Unset, bool]):
        working_holiday_visa_country (Union[Unset, str]):
        working_holiday_visa_start_date (Union[Unset, datetime.datetime]):
        is_seasonal_worker (Union[Unset, bool]):
        has_withholding_variation (Union[Unset, bool]):
        tax_variation (Union[Unset, float]):
        date_tax_file_declaration_signed (Union[Unset, datetime.datetime]):
        date_tax_file_declaration_reported (Union[Unset, datetime.datetime]):
        business_award_package (Union[Unset, str]):
        employment_agreement (Union[Unset, str]):
        is_exempt_from_payroll_tax (Union[Unset, bool]):
        bank_account_1_bsb (Union[Unset, str]):
        bank_account_2_bsb (Union[Unset, str]):
        bank_account_3_bsb (Union[Unset, str]):
        super_fund_1_product_code (Union[Unset, str]): Nullable</p><p>Must be "SMSF" for a self managed super fund
        super_fund_1_fund_name (Union[Unset, str]):
        super_fund_1_member_number (Union[Unset, str]):
        super_fund_1_allocated_percentage (Union[Unset, float]):
        super_fund_1_fixed_amount (Union[Unset, float]):
        super_fund_1_employer_nominated_fund (Union[Unset, bool]):
        super_fund_2_product_code (Union[Unset, str]): Nullable</p><p>Must be "SMSF" for a self managed super fund
        super_fund_2_fund_name (Union[Unset, str]):
        super_fund_2_member_number (Union[Unset, str]):
        super_fund_2_allocated_percentage (Union[Unset, float]):
        super_fund_2_fixed_amount (Union[Unset, float]):
        super_fund_2_employer_nominated_fund (Union[Unset, bool]):
        super_fund_3_product_code (Union[Unset, str]): Nullable</p><p>Must be "SMSF" for a self managed super fund
        super_fund_3_fund_name (Union[Unset, str]):
        super_fund_3_member_number (Union[Unset, str]):
        super_fund_3_allocated_percentage (Union[Unset, float]):
        super_fund_3_fixed_amount (Union[Unset, float]):
        super_fund_3_employer_nominated_fund (Union[Unset, bool]):
        super_threshold_amount (Union[Unset, float]):
        maximum_quarterly_super_contributions_base (Union[Unset, float]):
        medicare_levy_exemption (Union[Unset, str]):
        closely_held_employee (Union[Unset, bool]): Nullable</p><p><i>Note:</i>A non-null value here will overwrite the
            <i>SingleTouchPayroll</i> value. Set this to null if <i>SingleTouchPayroll</i> value should be used.
        closely_held_reporting (Union[Unset, AuUnstructuredEmployeeModelNullableCloselyHeldReportingEnum]):
            Nullable</p><p><i>Note:</i>During a transition period, a null value will default to <i>PayPerQuarter</i> if
            CloselyHeldEmployee is "true".</p><p>A null value with CloselyHeldEmployee = "true" will not be valid in the
            future.
        single_touch_payroll (Union[Unset, AuUnstructuredEmployeeModelNullableStpIncomeTypeEnum]):
        hours_per_day (Union[Unset, float]): Nullable</p><p>A null value will default to the business setting for
            <i>Standard hours per day</i>
        postal_address_is_overseas (Union[Unset, bool]):
        residential_address_is_overseas (Union[Unset, bool]):
        employment_type (Union[Unset, str]):
        contractor_abn (Union[Unset, str]):
        termination_reason (Union[Unset, str]):
        tax_category (Union[Unset, AuUnstructuredEmployeeModelNullableTaxFileDeclarationTaxCategoryCombination]):
        medicare_levy_surcharge_withholding_tier (Union[Unset,
            AuUnstructuredEmployeeModelNullableMedicareLevySurchargeWithholdingTier]):
        claim_medicare_levy_reduction (Union[Unset, bool]):
        medicare_levy_reduction_spouse (Union[Unset, bool]):
        medicare_levy_reduction_dependent_count (Union[Unset, int]):
        dvl_pay_slip_description (Union[Unset, str]): String</p><p>Possible values are:</p><ul class="list-
            bullet"><li><code>EmployeePrimaryPayCategory</code></li><li>The name of any other pay category</li></ul><p>
        portable_long_service_leave_id (Union[Unset, str]):
        include_in_portable_long_service_leave_report (Union[Unset, bool]):
        automatically_apply_public_holiday_not_worked_earnings_lines (Union[Unset, bool]):
        award_id (Union[Unset, int]):
        employment_agreement_id (Union[Unset, int]):
        disable_auto_progression (Union[Unset, bool]):
        id (Union[Unset, int]):
        title (Union[Unset, str]):
        preferred_name (Union[Unset, str]):
        first_name (Union[Unset, str]):
        middle_name (Union[Unset, str]):
        surname (Union[Unset, str]):
        date_of_birth (Union[Unset, datetime.datetime]):
        gender (Union[Unset, str]):
        external_id (Union[Unset, str]):
        residential_street_address (Union[Unset, str]):
        residential_address_line_2 (Union[Unset, str]):
        residential_post_code (Union[Unset, str]):
        residential_country (Union[Unset, str]):
        postal_street_address (Union[Unset, str]):
        postal_address_line_2 (Union[Unset, str]):
        postal_post_code (Union[Unset, str]):
        postal_country (Union[Unset, str]):
        email_address (Union[Unset, str]):
        home_phone (Union[Unset, str]):
        work_phone (Union[Unset, str]):
        mobile_phone (Union[Unset, str]):
        start_date (Union[Unset, datetime.datetime]):
        end_date (Union[Unset, datetime.datetime]):
        anniversary_date (Union[Unset, datetime.datetime]):
        tags (Union[Unset, str]):
        job_title (Union[Unset, str]):
        pay_schedule (Union[Unset, str]):
        primary_pay_category (Union[Unset, str]):
        primary_location (Union[Unset, str]):
        pay_slip_notification_type (Union[Unset, str]):
        rate (Union[Unset, float]):
        override_template_rate (Union[Unset, str]):
        rate_unit (Union[Unset, str]):
        hours_per_week (Union[Unset, float]):
        automatically_pay_employee (Union[Unset, str]):
        leave_template (Union[Unset, str]):
        pay_rate_template (Union[Unset, str]):
        pay_condition_rule_set (Union[Unset, str]):
        is_enabled_for_timesheets (Union[Unset, str]):
        locations (Union[Unset, str]):
        work_types (Union[Unset, str]):
        emergency_contact_1_name (Union[Unset, str]):
        emergency_contact_1_relationship (Union[Unset, str]):
        emergency_contact_1_address (Union[Unset, str]):
        emergency_contact_1_contact_number (Union[Unset, str]):
        emergency_contact_1_alternate_contact_number (Union[Unset, str]):
        emergency_contact_2_name (Union[Unset, str]):
        emergency_contact_2_relationship (Union[Unset, str]):
        emergency_contact_2_address (Union[Unset, str]):
        emergency_contact_2_contact_number (Union[Unset, str]):
        emergency_contact_2_alternate_contact_number (Union[Unset, str]):
        bank_account_1_account_number (Union[Unset, str]):
        bank_account_1_account_name (Union[Unset, str]):
        bank_account_1_allocated_percentage (Union[Unset, float]):
        bank_account_1_fixed_amount (Union[Unset, float]):
        bank_account_2_account_number (Union[Unset, str]):
        bank_account_2_account_name (Union[Unset, str]):
        bank_account_2_allocated_percentage (Union[Unset, float]):
        bank_account_2_fixed_amount (Union[Unset, float]):
        bank_account_3_account_number (Union[Unset, str]):
        bank_account_3_account_name (Union[Unset, str]):
        bank_account_3_allocated_percentage (Union[Unset, float]):
        bank_account_3_fixed_amount (Union[Unset, float]):
        rostering_notification_choices (Union[Unset, str]):
        leave_accrual_start_date_type (Union[Unset, AuUnstructuredEmployeeModelNullableLeaveAccrualStartDateType]):
        leave_year_start (Union[Unset, datetime.datetime]):
        status (Union[Unset, AuUnstructuredEmployeeModelEmployeeStatusEnum]):
        date_created (Union[Unset, datetime.datetime]):
        reporting_dimension_values (Union[Unset, str]):
    """

    tax_file_number: Union[Unset, str] = UNSET
    residential_suburb: Union[Unset, str] = UNSET
    residential_state: Union[Unset, str] = UNSET
    postal_suburb: Union[Unset, str] = UNSET
    postal_state: Union[Unset, str] = UNSET
    employing_entity_abn: Union[Unset, str] = UNSET
    employing_entity_id: Union[Unset, str] = UNSET
    previous_surname: Union[Unset, str] = UNSET
    australian_resident: Union[Unset, bool] = UNSET
    claim_tax_free_threshold: Union[Unset, bool] = UNSET
    seniors_tax_offset: Union[Unset, bool] = UNSET
    other_tax_offset: Union[Unset, bool] = UNSET
    stsl_debt: Union[Unset, bool] = UNSET
    is_exempt_from_flood_levy: Union[Unset, bool] = UNSET
    has_approved_working_holiday_visa: Union[Unset, bool] = UNSET
    working_holiday_visa_country: Union[Unset, str] = UNSET
    working_holiday_visa_start_date: Union[Unset, datetime.datetime] = UNSET
    is_seasonal_worker: Union[Unset, bool] = UNSET
    has_withholding_variation: Union[Unset, bool] = UNSET
    tax_variation: Union[Unset, float] = UNSET
    date_tax_file_declaration_signed: Union[Unset, datetime.datetime] = UNSET
    date_tax_file_declaration_reported: Union[Unset, datetime.datetime] = UNSET
    business_award_package: Union[Unset, str] = UNSET
    employment_agreement: Union[Unset, str] = UNSET
    is_exempt_from_payroll_tax: Union[Unset, bool] = UNSET
    bank_account_1_bsb: Union[Unset, str] = UNSET
    bank_account_2_bsb: Union[Unset, str] = UNSET
    bank_account_3_bsb: Union[Unset, str] = UNSET
    super_fund_1_product_code: Union[Unset, str] = UNSET
    super_fund_1_fund_name: Union[Unset, str] = UNSET
    super_fund_1_member_number: Union[Unset, str] = UNSET
    super_fund_1_allocated_percentage: Union[Unset, float] = UNSET
    super_fund_1_fixed_amount: Union[Unset, float] = UNSET
    super_fund_1_employer_nominated_fund: Union[Unset, bool] = UNSET
    super_fund_2_product_code: Union[Unset, str] = UNSET
    super_fund_2_fund_name: Union[Unset, str] = UNSET
    super_fund_2_member_number: Union[Unset, str] = UNSET
    super_fund_2_allocated_percentage: Union[Unset, float] = UNSET
    super_fund_2_fixed_amount: Union[Unset, float] = UNSET
    super_fund_2_employer_nominated_fund: Union[Unset, bool] = UNSET
    super_fund_3_product_code: Union[Unset, str] = UNSET
    super_fund_3_fund_name: Union[Unset, str] = UNSET
    super_fund_3_member_number: Union[Unset, str] = UNSET
    super_fund_3_allocated_percentage: Union[Unset, float] = UNSET
    super_fund_3_fixed_amount: Union[Unset, float] = UNSET
    super_fund_3_employer_nominated_fund: Union[Unset, bool] = UNSET
    super_threshold_amount: Union[Unset, float] = UNSET
    maximum_quarterly_super_contributions_base: Union[Unset, float] = UNSET
    medicare_levy_exemption: Union[Unset, str] = UNSET
    closely_held_employee: Union[Unset, bool] = UNSET
    closely_held_reporting: Union[Unset, AuUnstructuredEmployeeModelNullableCloselyHeldReportingEnum] = UNSET
    single_touch_payroll: Union[Unset, AuUnstructuredEmployeeModelNullableStpIncomeTypeEnum] = UNSET
    hours_per_day: Union[Unset, float] = UNSET
    postal_address_is_overseas: Union[Unset, bool] = UNSET
    residential_address_is_overseas: Union[Unset, bool] = UNSET
    employment_type: Union[Unset, str] = UNSET
    contractor_abn: Union[Unset, str] = UNSET
    termination_reason: Union[Unset, str] = UNSET
    tax_category: Union[Unset, AuUnstructuredEmployeeModelNullableTaxFileDeclarationTaxCategoryCombination] = UNSET
    medicare_levy_surcharge_withholding_tier: Union[
        Unset, AuUnstructuredEmployeeModelNullableMedicareLevySurchargeWithholdingTier
    ] = UNSET
    claim_medicare_levy_reduction: Union[Unset, bool] = UNSET
    medicare_levy_reduction_spouse: Union[Unset, bool] = UNSET
    medicare_levy_reduction_dependent_count: Union[Unset, int] = UNSET
    dvl_pay_slip_description: Union[Unset, str] = UNSET
    portable_long_service_leave_id: Union[Unset, str] = UNSET
    include_in_portable_long_service_leave_report: Union[Unset, bool] = UNSET
    automatically_apply_public_holiday_not_worked_earnings_lines: Union[Unset, bool] = UNSET
    award_id: Union[Unset, int] = UNSET
    employment_agreement_id: Union[Unset, int] = UNSET
    disable_auto_progression: Union[Unset, bool] = UNSET
    id: Union[Unset, int] = UNSET
    title: Union[Unset, str] = UNSET
    preferred_name: Union[Unset, str] = UNSET
    first_name: Union[Unset, str] = UNSET
    middle_name: Union[Unset, str] = UNSET
    surname: Union[Unset, str] = UNSET
    date_of_birth: Union[Unset, datetime.datetime] = UNSET
    gender: Union[Unset, str] = UNSET
    external_id: Union[Unset, str] = UNSET
    residential_street_address: Union[Unset, str] = UNSET
    residential_address_line_2: Union[Unset, str] = UNSET
    residential_post_code: Union[Unset, str] = UNSET
    residential_country: Union[Unset, str] = UNSET
    postal_street_address: Union[Unset, str] = UNSET
    postal_address_line_2: Union[Unset, str] = UNSET
    postal_post_code: Union[Unset, str] = UNSET
    postal_country: Union[Unset, str] = UNSET
    email_address: Union[Unset, str] = UNSET
    home_phone: Union[Unset, str] = UNSET
    work_phone: Union[Unset, str] = UNSET
    mobile_phone: Union[Unset, str] = UNSET
    start_date: Union[Unset, datetime.datetime] = UNSET
    end_date: Union[Unset, datetime.datetime] = UNSET
    anniversary_date: Union[Unset, datetime.datetime] = UNSET
    tags: Union[Unset, str] = UNSET
    job_title: Union[Unset, str] = UNSET
    pay_schedule: Union[Unset, str] = UNSET
    primary_pay_category: Union[Unset, str] = UNSET
    primary_location: Union[Unset, str] = UNSET
    pay_slip_notification_type: Union[Unset, str] = UNSET
    rate: Union[Unset, float] = UNSET
    override_template_rate: Union[Unset, str] = UNSET
    rate_unit: Union[Unset, str] = UNSET
    hours_per_week: Union[Unset, float] = UNSET
    automatically_pay_employee: Union[Unset, str] = UNSET
    leave_template: Union[Unset, str] = UNSET
    pay_rate_template: Union[Unset, str] = UNSET
    pay_condition_rule_set: Union[Unset, str] = UNSET
    is_enabled_for_timesheets: Union[Unset, str] = UNSET
    locations: Union[Unset, str] = UNSET
    work_types: Union[Unset, str] = UNSET
    emergency_contact_1_name: Union[Unset, str] = UNSET
    emergency_contact_1_relationship: Union[Unset, str] = UNSET
    emergency_contact_1_address: Union[Unset, str] = UNSET
    emergency_contact_1_contact_number: Union[Unset, str] = UNSET
    emergency_contact_1_alternate_contact_number: Union[Unset, str] = UNSET
    emergency_contact_2_name: Union[Unset, str] = UNSET
    emergency_contact_2_relationship: Union[Unset, str] = UNSET
    emergency_contact_2_address: Union[Unset, str] = UNSET
    emergency_contact_2_contact_number: Union[Unset, str] = UNSET
    emergency_contact_2_alternate_contact_number: Union[Unset, str] = UNSET
    bank_account_1_account_number: Union[Unset, str] = UNSET
    bank_account_1_account_name: Union[Unset, str] = UNSET
    bank_account_1_allocated_percentage: Union[Unset, float] = UNSET
    bank_account_1_fixed_amount: Union[Unset, float] = UNSET
    bank_account_2_account_number: Union[Unset, str] = UNSET
    bank_account_2_account_name: Union[Unset, str] = UNSET
    bank_account_2_allocated_percentage: Union[Unset, float] = UNSET
    bank_account_2_fixed_amount: Union[Unset, float] = UNSET
    bank_account_3_account_number: Union[Unset, str] = UNSET
    bank_account_3_account_name: Union[Unset, str] = UNSET
    bank_account_3_allocated_percentage: Union[Unset, float] = UNSET
    bank_account_3_fixed_amount: Union[Unset, float] = UNSET
    rostering_notification_choices: Union[Unset, str] = UNSET
    leave_accrual_start_date_type: Union[Unset, AuUnstructuredEmployeeModelNullableLeaveAccrualStartDateType] = UNSET
    leave_year_start: Union[Unset, datetime.datetime] = UNSET
    status: Union[Unset, AuUnstructuredEmployeeModelEmployeeStatusEnum] = UNSET
    date_created: Union[Unset, datetime.datetime] = UNSET
    reporting_dimension_values: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        tax_file_number = self.tax_file_number

        residential_suburb = self.residential_suburb

        residential_state = self.residential_state

        postal_suburb = self.postal_suburb

        postal_state = self.postal_state

        employing_entity_abn = self.employing_entity_abn

        employing_entity_id = self.employing_entity_id

        previous_surname = self.previous_surname

        australian_resident = self.australian_resident

        claim_tax_free_threshold = self.claim_tax_free_threshold

        seniors_tax_offset = self.seniors_tax_offset

        other_tax_offset = self.other_tax_offset

        stsl_debt = self.stsl_debt

        is_exempt_from_flood_levy = self.is_exempt_from_flood_levy

        has_approved_working_holiday_visa = self.has_approved_working_holiday_visa

        working_holiday_visa_country = self.working_holiday_visa_country

        working_holiday_visa_start_date: Union[Unset, str] = UNSET
        if not isinstance(self.working_holiday_visa_start_date, Unset):
            working_holiday_visa_start_date = self.working_holiday_visa_start_date.isoformat()

        is_seasonal_worker = self.is_seasonal_worker

        has_withholding_variation = self.has_withholding_variation

        tax_variation = self.tax_variation

        date_tax_file_declaration_signed: Union[Unset, str] = UNSET
        if not isinstance(self.date_tax_file_declaration_signed, Unset):
            date_tax_file_declaration_signed = self.date_tax_file_declaration_signed.isoformat()

        date_tax_file_declaration_reported: Union[Unset, str] = UNSET
        if not isinstance(self.date_tax_file_declaration_reported, Unset):
            date_tax_file_declaration_reported = self.date_tax_file_declaration_reported.isoformat()

        business_award_package = self.business_award_package

        employment_agreement = self.employment_agreement

        is_exempt_from_payroll_tax = self.is_exempt_from_payroll_tax

        bank_account_1_bsb = self.bank_account_1_bsb

        bank_account_2_bsb = self.bank_account_2_bsb

        bank_account_3_bsb = self.bank_account_3_bsb

        super_fund_1_product_code = self.super_fund_1_product_code

        super_fund_1_fund_name = self.super_fund_1_fund_name

        super_fund_1_member_number = self.super_fund_1_member_number

        super_fund_1_allocated_percentage = self.super_fund_1_allocated_percentage

        super_fund_1_fixed_amount = self.super_fund_1_fixed_amount

        super_fund_1_employer_nominated_fund = self.super_fund_1_employer_nominated_fund

        super_fund_2_product_code = self.super_fund_2_product_code

        super_fund_2_fund_name = self.super_fund_2_fund_name

        super_fund_2_member_number = self.super_fund_2_member_number

        super_fund_2_allocated_percentage = self.super_fund_2_allocated_percentage

        super_fund_2_fixed_amount = self.super_fund_2_fixed_amount

        super_fund_2_employer_nominated_fund = self.super_fund_2_employer_nominated_fund

        super_fund_3_product_code = self.super_fund_3_product_code

        super_fund_3_fund_name = self.super_fund_3_fund_name

        super_fund_3_member_number = self.super_fund_3_member_number

        super_fund_3_allocated_percentage = self.super_fund_3_allocated_percentage

        super_fund_3_fixed_amount = self.super_fund_3_fixed_amount

        super_fund_3_employer_nominated_fund = self.super_fund_3_employer_nominated_fund

        super_threshold_amount = self.super_threshold_amount

        maximum_quarterly_super_contributions_base = self.maximum_quarterly_super_contributions_base

        medicare_levy_exemption = self.medicare_levy_exemption

        closely_held_employee = self.closely_held_employee

        closely_held_reporting: Union[Unset, str] = UNSET
        if not isinstance(self.closely_held_reporting, Unset):
            closely_held_reporting = self.closely_held_reporting.value

        single_touch_payroll: Union[Unset, str] = UNSET
        if not isinstance(self.single_touch_payroll, Unset):
            single_touch_payroll = self.single_touch_payroll.value

        hours_per_day = self.hours_per_day

        postal_address_is_overseas = self.postal_address_is_overseas

        residential_address_is_overseas = self.residential_address_is_overseas

        employment_type = self.employment_type

        contractor_abn = self.contractor_abn

        termination_reason = self.termination_reason

        tax_category: Union[Unset, str] = UNSET
        if not isinstance(self.tax_category, Unset):
            tax_category = self.tax_category.value

        medicare_levy_surcharge_withholding_tier: Union[Unset, str] = UNSET
        if not isinstance(self.medicare_levy_surcharge_withholding_tier, Unset):
            medicare_levy_surcharge_withholding_tier = self.medicare_levy_surcharge_withholding_tier.value

        claim_medicare_levy_reduction = self.claim_medicare_levy_reduction

        medicare_levy_reduction_spouse = self.medicare_levy_reduction_spouse

        medicare_levy_reduction_dependent_count = self.medicare_levy_reduction_dependent_count

        dvl_pay_slip_description = self.dvl_pay_slip_description

        portable_long_service_leave_id = self.portable_long_service_leave_id

        include_in_portable_long_service_leave_report = self.include_in_portable_long_service_leave_report

        automatically_apply_public_holiday_not_worked_earnings_lines = (
            self.automatically_apply_public_holiday_not_worked_earnings_lines
        )

        award_id = self.award_id

        employment_agreement_id = self.employment_agreement_id

        disable_auto_progression = self.disable_auto_progression

        id = self.id

        title = self.title

        preferred_name = self.preferred_name

        first_name = self.first_name

        middle_name = self.middle_name

        surname = self.surname

        date_of_birth: Union[Unset, str] = UNSET
        if not isinstance(self.date_of_birth, Unset):
            date_of_birth = self.date_of_birth.isoformat()

        gender = self.gender

        external_id = self.external_id

        residential_street_address = self.residential_street_address

        residential_address_line_2 = self.residential_address_line_2

        residential_post_code = self.residential_post_code

        residential_country = self.residential_country

        postal_street_address = self.postal_street_address

        postal_address_line_2 = self.postal_address_line_2

        postal_post_code = self.postal_post_code

        postal_country = self.postal_country

        email_address = self.email_address

        home_phone = self.home_phone

        work_phone = self.work_phone

        mobile_phone = self.mobile_phone

        start_date: Union[Unset, str] = UNSET
        if not isinstance(self.start_date, Unset):
            start_date = self.start_date.isoformat()

        end_date: Union[Unset, str] = UNSET
        if not isinstance(self.end_date, Unset):
            end_date = self.end_date.isoformat()

        anniversary_date: Union[Unset, str] = UNSET
        if not isinstance(self.anniversary_date, Unset):
            anniversary_date = self.anniversary_date.isoformat()

        tags = self.tags

        job_title = self.job_title

        pay_schedule = self.pay_schedule

        primary_pay_category = self.primary_pay_category

        primary_location = self.primary_location

        pay_slip_notification_type = self.pay_slip_notification_type

        rate = self.rate

        override_template_rate = self.override_template_rate

        rate_unit = self.rate_unit

        hours_per_week = self.hours_per_week

        automatically_pay_employee = self.automatically_pay_employee

        leave_template = self.leave_template

        pay_rate_template = self.pay_rate_template

        pay_condition_rule_set = self.pay_condition_rule_set

        is_enabled_for_timesheets = self.is_enabled_for_timesheets

        locations = self.locations

        work_types = self.work_types

        emergency_contact_1_name = self.emergency_contact_1_name

        emergency_contact_1_relationship = self.emergency_contact_1_relationship

        emergency_contact_1_address = self.emergency_contact_1_address

        emergency_contact_1_contact_number = self.emergency_contact_1_contact_number

        emergency_contact_1_alternate_contact_number = self.emergency_contact_1_alternate_contact_number

        emergency_contact_2_name = self.emergency_contact_2_name

        emergency_contact_2_relationship = self.emergency_contact_2_relationship

        emergency_contact_2_address = self.emergency_contact_2_address

        emergency_contact_2_contact_number = self.emergency_contact_2_contact_number

        emergency_contact_2_alternate_contact_number = self.emergency_contact_2_alternate_contact_number

        bank_account_1_account_number = self.bank_account_1_account_number

        bank_account_1_account_name = self.bank_account_1_account_name

        bank_account_1_allocated_percentage = self.bank_account_1_allocated_percentage

        bank_account_1_fixed_amount = self.bank_account_1_fixed_amount

        bank_account_2_account_number = self.bank_account_2_account_number

        bank_account_2_account_name = self.bank_account_2_account_name

        bank_account_2_allocated_percentage = self.bank_account_2_allocated_percentage

        bank_account_2_fixed_amount = self.bank_account_2_fixed_amount

        bank_account_3_account_number = self.bank_account_3_account_number

        bank_account_3_account_name = self.bank_account_3_account_name

        bank_account_3_allocated_percentage = self.bank_account_3_allocated_percentage

        bank_account_3_fixed_amount = self.bank_account_3_fixed_amount

        rostering_notification_choices = self.rostering_notification_choices

        leave_accrual_start_date_type: Union[Unset, str] = UNSET
        if not isinstance(self.leave_accrual_start_date_type, Unset):
            leave_accrual_start_date_type = self.leave_accrual_start_date_type.value

        leave_year_start: Union[Unset, str] = UNSET
        if not isinstance(self.leave_year_start, Unset):
            leave_year_start = self.leave_year_start.isoformat()

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        date_created: Union[Unset, str] = UNSET
        if not isinstance(self.date_created, Unset):
            date_created = self.date_created.isoformat()

        reporting_dimension_values = self.reporting_dimension_values

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if tax_file_number is not UNSET:
            field_dict["taxFileNumber"] = tax_file_number
        if residential_suburb is not UNSET:
            field_dict["residentialSuburb"] = residential_suburb
        if residential_state is not UNSET:
            field_dict["residentialState"] = residential_state
        if postal_suburb is not UNSET:
            field_dict["postalSuburb"] = postal_suburb
        if postal_state is not UNSET:
            field_dict["postalState"] = postal_state
        if employing_entity_abn is not UNSET:
            field_dict["employingEntityABN"] = employing_entity_abn
        if employing_entity_id is not UNSET:
            field_dict["employingEntityId"] = employing_entity_id
        if previous_surname is not UNSET:
            field_dict["previousSurname"] = previous_surname
        if australian_resident is not UNSET:
            field_dict["australianResident"] = australian_resident
        if claim_tax_free_threshold is not UNSET:
            field_dict["claimTaxFreeThreshold"] = claim_tax_free_threshold
        if seniors_tax_offset is not UNSET:
            field_dict["seniorsTaxOffset"] = seniors_tax_offset
        if other_tax_offset is not UNSET:
            field_dict["otherTaxOffset"] = other_tax_offset
        if stsl_debt is not UNSET:
            field_dict["stslDebt"] = stsl_debt
        if is_exempt_from_flood_levy is not UNSET:
            field_dict["isExemptFromFloodLevy"] = is_exempt_from_flood_levy
        if has_approved_working_holiday_visa is not UNSET:
            field_dict["hasApprovedWorkingHolidayVisa"] = has_approved_working_holiday_visa
        if working_holiday_visa_country is not UNSET:
            field_dict["workingHolidayVisaCountry"] = working_holiday_visa_country
        if working_holiday_visa_start_date is not UNSET:
            field_dict["workingHolidayVisaStartDate"] = working_holiday_visa_start_date
        if is_seasonal_worker is not UNSET:
            field_dict["isSeasonalWorker"] = is_seasonal_worker
        if has_withholding_variation is not UNSET:
            field_dict["hasWithholdingVariation"] = has_withholding_variation
        if tax_variation is not UNSET:
            field_dict["taxVariation"] = tax_variation
        if date_tax_file_declaration_signed is not UNSET:
            field_dict["dateTaxFileDeclarationSigned"] = date_tax_file_declaration_signed
        if date_tax_file_declaration_reported is not UNSET:
            field_dict["dateTaxFileDeclarationReported"] = date_tax_file_declaration_reported
        if business_award_package is not UNSET:
            field_dict["businessAwardPackage"] = business_award_package
        if employment_agreement is not UNSET:
            field_dict["employmentAgreement"] = employment_agreement
        if is_exempt_from_payroll_tax is not UNSET:
            field_dict["isExemptFromPayrollTax"] = is_exempt_from_payroll_tax
        if bank_account_1_bsb is not UNSET:
            field_dict["bankAccount1_BSB"] = bank_account_1_bsb
        if bank_account_2_bsb is not UNSET:
            field_dict["bankAccount2_BSB"] = bank_account_2_bsb
        if bank_account_3_bsb is not UNSET:
            field_dict["bankAccount3_BSB"] = bank_account_3_bsb
        if super_fund_1_product_code is not UNSET:
            field_dict["superFund1_ProductCode"] = super_fund_1_product_code
        if super_fund_1_fund_name is not UNSET:
            field_dict["superFund1_FundName"] = super_fund_1_fund_name
        if super_fund_1_member_number is not UNSET:
            field_dict["superFund1_MemberNumber"] = super_fund_1_member_number
        if super_fund_1_allocated_percentage is not UNSET:
            field_dict["superFund1_AllocatedPercentage"] = super_fund_1_allocated_percentage
        if super_fund_1_fixed_amount is not UNSET:
            field_dict["superFund1_FixedAmount"] = super_fund_1_fixed_amount
        if super_fund_1_employer_nominated_fund is not UNSET:
            field_dict["superFund1_EmployerNominatedFund"] = super_fund_1_employer_nominated_fund
        if super_fund_2_product_code is not UNSET:
            field_dict["superFund2_ProductCode"] = super_fund_2_product_code
        if super_fund_2_fund_name is not UNSET:
            field_dict["superFund2_FundName"] = super_fund_2_fund_name
        if super_fund_2_member_number is not UNSET:
            field_dict["superFund2_MemberNumber"] = super_fund_2_member_number
        if super_fund_2_allocated_percentage is not UNSET:
            field_dict["superFund2_AllocatedPercentage"] = super_fund_2_allocated_percentage
        if super_fund_2_fixed_amount is not UNSET:
            field_dict["superFund2_FixedAmount"] = super_fund_2_fixed_amount
        if super_fund_2_employer_nominated_fund is not UNSET:
            field_dict["superFund2_EmployerNominatedFund"] = super_fund_2_employer_nominated_fund
        if super_fund_3_product_code is not UNSET:
            field_dict["superFund3_ProductCode"] = super_fund_3_product_code
        if super_fund_3_fund_name is not UNSET:
            field_dict["superFund3_FundName"] = super_fund_3_fund_name
        if super_fund_3_member_number is not UNSET:
            field_dict["superFund3_MemberNumber"] = super_fund_3_member_number
        if super_fund_3_allocated_percentage is not UNSET:
            field_dict["superFund3_AllocatedPercentage"] = super_fund_3_allocated_percentage
        if super_fund_3_fixed_amount is not UNSET:
            field_dict["superFund3_FixedAmount"] = super_fund_3_fixed_amount
        if super_fund_3_employer_nominated_fund is not UNSET:
            field_dict["superFund3_EmployerNominatedFund"] = super_fund_3_employer_nominated_fund
        if super_threshold_amount is not UNSET:
            field_dict["superThresholdAmount"] = super_threshold_amount
        if maximum_quarterly_super_contributions_base is not UNSET:
            field_dict["maximumQuarterlySuperContributionsBase"] = maximum_quarterly_super_contributions_base
        if medicare_levy_exemption is not UNSET:
            field_dict["medicareLevyExemption"] = medicare_levy_exemption
        if closely_held_employee is not UNSET:
            field_dict["closelyHeldEmployee"] = closely_held_employee
        if closely_held_reporting is not UNSET:
            field_dict["closelyHeldReporting"] = closely_held_reporting
        if single_touch_payroll is not UNSET:
            field_dict["singleTouchPayroll"] = single_touch_payroll
        if hours_per_day is not UNSET:
            field_dict["hoursPerDay"] = hours_per_day
        if postal_address_is_overseas is not UNSET:
            field_dict["postalAddressIsOverseas"] = postal_address_is_overseas
        if residential_address_is_overseas is not UNSET:
            field_dict["residentialAddressIsOverseas"] = residential_address_is_overseas
        if employment_type is not UNSET:
            field_dict["employmentType"] = employment_type
        if contractor_abn is not UNSET:
            field_dict["contractorABN"] = contractor_abn
        if termination_reason is not UNSET:
            field_dict["terminationReason"] = termination_reason
        if tax_category is not UNSET:
            field_dict["taxCategory"] = tax_category
        if medicare_levy_surcharge_withholding_tier is not UNSET:
            field_dict["medicareLevySurchargeWithholdingTier"] = medicare_levy_surcharge_withholding_tier
        if claim_medicare_levy_reduction is not UNSET:
            field_dict["claimMedicareLevyReduction"] = claim_medicare_levy_reduction
        if medicare_levy_reduction_spouse is not UNSET:
            field_dict["medicareLevyReductionSpouse"] = medicare_levy_reduction_spouse
        if medicare_levy_reduction_dependent_count is not UNSET:
            field_dict["medicareLevyReductionDependentCount"] = medicare_levy_reduction_dependent_count
        if dvl_pay_slip_description is not UNSET:
            field_dict["dvlPaySlipDescription"] = dvl_pay_slip_description
        if portable_long_service_leave_id is not UNSET:
            field_dict["portableLongServiceLeaveId"] = portable_long_service_leave_id
        if include_in_portable_long_service_leave_report is not UNSET:
            field_dict["includeInPortableLongServiceLeaveReport"] = include_in_portable_long_service_leave_report
        if automatically_apply_public_holiday_not_worked_earnings_lines is not UNSET:
            field_dict["automaticallyApplyPublicHolidayNotWorkedEarningsLines"] = (
                automatically_apply_public_holiday_not_worked_earnings_lines
            )
        if award_id is not UNSET:
            field_dict["awardId"] = award_id
        if employment_agreement_id is not UNSET:
            field_dict["employmentAgreementId"] = employment_agreement_id
        if disable_auto_progression is not UNSET:
            field_dict["disableAutoProgression"] = disable_auto_progression
        if id is not UNSET:
            field_dict["id"] = id
        if title is not UNSET:
            field_dict["title"] = title
        if preferred_name is not UNSET:
            field_dict["preferredName"] = preferred_name
        if first_name is not UNSET:
            field_dict["firstName"] = first_name
        if middle_name is not UNSET:
            field_dict["middleName"] = middle_name
        if surname is not UNSET:
            field_dict["surname"] = surname
        if date_of_birth is not UNSET:
            field_dict["dateOfBirth"] = date_of_birth
        if gender is not UNSET:
            field_dict["gender"] = gender
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if residential_street_address is not UNSET:
            field_dict["residentialStreetAddress"] = residential_street_address
        if residential_address_line_2 is not UNSET:
            field_dict["residentialAddressLine2"] = residential_address_line_2
        if residential_post_code is not UNSET:
            field_dict["residentialPostCode"] = residential_post_code
        if residential_country is not UNSET:
            field_dict["residentialCountry"] = residential_country
        if postal_street_address is not UNSET:
            field_dict["postalStreetAddress"] = postal_street_address
        if postal_address_line_2 is not UNSET:
            field_dict["postalAddressLine2"] = postal_address_line_2
        if postal_post_code is not UNSET:
            field_dict["postalPostCode"] = postal_post_code
        if postal_country is not UNSET:
            field_dict["postalCountry"] = postal_country
        if email_address is not UNSET:
            field_dict["emailAddress"] = email_address
        if home_phone is not UNSET:
            field_dict["homePhone"] = home_phone
        if work_phone is not UNSET:
            field_dict["workPhone"] = work_phone
        if mobile_phone is not UNSET:
            field_dict["mobilePhone"] = mobile_phone
        if start_date is not UNSET:
            field_dict["startDate"] = start_date
        if end_date is not UNSET:
            field_dict["endDate"] = end_date
        if anniversary_date is not UNSET:
            field_dict["anniversaryDate"] = anniversary_date
        if tags is not UNSET:
            field_dict["tags"] = tags
        if job_title is not UNSET:
            field_dict["jobTitle"] = job_title
        if pay_schedule is not UNSET:
            field_dict["paySchedule"] = pay_schedule
        if primary_pay_category is not UNSET:
            field_dict["primaryPayCategory"] = primary_pay_category
        if primary_location is not UNSET:
            field_dict["primaryLocation"] = primary_location
        if pay_slip_notification_type is not UNSET:
            field_dict["paySlipNotificationType"] = pay_slip_notification_type
        if rate is not UNSET:
            field_dict["rate"] = rate
        if override_template_rate is not UNSET:
            field_dict["overrideTemplateRate"] = override_template_rate
        if rate_unit is not UNSET:
            field_dict["rateUnit"] = rate_unit
        if hours_per_week is not UNSET:
            field_dict["hoursPerWeek"] = hours_per_week
        if automatically_pay_employee is not UNSET:
            field_dict["automaticallyPayEmployee"] = automatically_pay_employee
        if leave_template is not UNSET:
            field_dict["leaveTemplate"] = leave_template
        if pay_rate_template is not UNSET:
            field_dict["payRateTemplate"] = pay_rate_template
        if pay_condition_rule_set is not UNSET:
            field_dict["payConditionRuleSet"] = pay_condition_rule_set
        if is_enabled_for_timesheets is not UNSET:
            field_dict["isEnabledForTimesheets"] = is_enabled_for_timesheets
        if locations is not UNSET:
            field_dict["locations"] = locations
        if work_types is not UNSET:
            field_dict["workTypes"] = work_types
        if emergency_contact_1_name is not UNSET:
            field_dict["emergencyContact1_Name"] = emergency_contact_1_name
        if emergency_contact_1_relationship is not UNSET:
            field_dict["emergencyContact1_Relationship"] = emergency_contact_1_relationship
        if emergency_contact_1_address is not UNSET:
            field_dict["emergencyContact1_Address"] = emergency_contact_1_address
        if emergency_contact_1_contact_number is not UNSET:
            field_dict["emergencyContact1_ContactNumber"] = emergency_contact_1_contact_number
        if emergency_contact_1_alternate_contact_number is not UNSET:
            field_dict["emergencyContact1_AlternateContactNumber"] = emergency_contact_1_alternate_contact_number
        if emergency_contact_2_name is not UNSET:
            field_dict["emergencyContact2_Name"] = emergency_contact_2_name
        if emergency_contact_2_relationship is not UNSET:
            field_dict["emergencyContact2_Relationship"] = emergency_contact_2_relationship
        if emergency_contact_2_address is not UNSET:
            field_dict["emergencyContact2_Address"] = emergency_contact_2_address
        if emergency_contact_2_contact_number is not UNSET:
            field_dict["emergencyContact2_ContactNumber"] = emergency_contact_2_contact_number
        if emergency_contact_2_alternate_contact_number is not UNSET:
            field_dict["emergencyContact2_AlternateContactNumber"] = emergency_contact_2_alternate_contact_number
        if bank_account_1_account_number is not UNSET:
            field_dict["bankAccount1_AccountNumber"] = bank_account_1_account_number
        if bank_account_1_account_name is not UNSET:
            field_dict["bankAccount1_AccountName"] = bank_account_1_account_name
        if bank_account_1_allocated_percentage is not UNSET:
            field_dict["bankAccount1_AllocatedPercentage"] = bank_account_1_allocated_percentage
        if bank_account_1_fixed_amount is not UNSET:
            field_dict["bankAccount1_FixedAmount"] = bank_account_1_fixed_amount
        if bank_account_2_account_number is not UNSET:
            field_dict["bankAccount2_AccountNumber"] = bank_account_2_account_number
        if bank_account_2_account_name is not UNSET:
            field_dict["bankAccount2_AccountName"] = bank_account_2_account_name
        if bank_account_2_allocated_percentage is not UNSET:
            field_dict["bankAccount2_AllocatedPercentage"] = bank_account_2_allocated_percentage
        if bank_account_2_fixed_amount is not UNSET:
            field_dict["bankAccount2_FixedAmount"] = bank_account_2_fixed_amount
        if bank_account_3_account_number is not UNSET:
            field_dict["bankAccount3_AccountNumber"] = bank_account_3_account_number
        if bank_account_3_account_name is not UNSET:
            field_dict["bankAccount3_AccountName"] = bank_account_3_account_name
        if bank_account_3_allocated_percentage is not UNSET:
            field_dict["bankAccount3_AllocatedPercentage"] = bank_account_3_allocated_percentage
        if bank_account_3_fixed_amount is not UNSET:
            field_dict["bankAccount3_FixedAmount"] = bank_account_3_fixed_amount
        if rostering_notification_choices is not UNSET:
            field_dict["rosteringNotificationChoices"] = rostering_notification_choices
        if leave_accrual_start_date_type is not UNSET:
            field_dict["leaveAccrualStartDateType"] = leave_accrual_start_date_type
        if leave_year_start is not UNSET:
            field_dict["leaveYearStart"] = leave_year_start
        if status is not UNSET:
            field_dict["status"] = status
        if date_created is not UNSET:
            field_dict["dateCreated"] = date_created
        if reporting_dimension_values is not UNSET:
            field_dict["reportingDimensionValues"] = reporting_dimension_values

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        tax_file_number = d.pop("taxFileNumber", UNSET)

        residential_suburb = d.pop("residentialSuburb", UNSET)

        residential_state = d.pop("residentialState", UNSET)

        postal_suburb = d.pop("postalSuburb", UNSET)

        postal_state = d.pop("postalState", UNSET)

        employing_entity_abn = d.pop("employingEntityABN", UNSET)

        employing_entity_id = d.pop("employingEntityId", UNSET)

        previous_surname = d.pop("previousSurname", UNSET)

        australian_resident = d.pop("australianResident", UNSET)

        claim_tax_free_threshold = d.pop("claimTaxFreeThreshold", UNSET)

        seniors_tax_offset = d.pop("seniorsTaxOffset", UNSET)

        other_tax_offset = d.pop("otherTaxOffset", UNSET)

        stsl_debt = d.pop("stslDebt", UNSET)

        is_exempt_from_flood_levy = d.pop("isExemptFromFloodLevy", UNSET)

        has_approved_working_holiday_visa = d.pop("hasApprovedWorkingHolidayVisa", UNSET)

        working_holiday_visa_country = d.pop("workingHolidayVisaCountry", UNSET)

        _working_holiday_visa_start_date = d.pop("workingHolidayVisaStartDate", UNSET)
        working_holiday_visa_start_date: Union[Unset, datetime.datetime]
        if isinstance(_working_holiday_visa_start_date, Unset):
            working_holiday_visa_start_date = UNSET
        else:
            working_holiday_visa_start_date = isoparse(_working_holiday_visa_start_date)

        is_seasonal_worker = d.pop("isSeasonalWorker", UNSET)

        has_withholding_variation = d.pop("hasWithholdingVariation", UNSET)

        tax_variation = d.pop("taxVariation", UNSET)

        _date_tax_file_declaration_signed = d.pop("dateTaxFileDeclarationSigned", UNSET)
        date_tax_file_declaration_signed: Union[Unset, datetime.datetime]
        if isinstance(_date_tax_file_declaration_signed, Unset):
            date_tax_file_declaration_signed = UNSET
        else:
            date_tax_file_declaration_signed = isoparse(_date_tax_file_declaration_signed)

        _date_tax_file_declaration_reported = d.pop("dateTaxFileDeclarationReported", UNSET)
        date_tax_file_declaration_reported: Union[Unset, datetime.datetime]
        if isinstance(_date_tax_file_declaration_reported, Unset):
            date_tax_file_declaration_reported = UNSET
        else:
            date_tax_file_declaration_reported = isoparse(_date_tax_file_declaration_reported)

        business_award_package = d.pop("businessAwardPackage", UNSET)

        employment_agreement = d.pop("employmentAgreement", UNSET)

        is_exempt_from_payroll_tax = d.pop("isExemptFromPayrollTax", UNSET)

        bank_account_1_bsb = d.pop("bankAccount1_BSB", UNSET)

        bank_account_2_bsb = d.pop("bankAccount2_BSB", UNSET)

        bank_account_3_bsb = d.pop("bankAccount3_BSB", UNSET)

        super_fund_1_product_code = d.pop("superFund1_ProductCode", UNSET)

        super_fund_1_fund_name = d.pop("superFund1_FundName", UNSET)

        super_fund_1_member_number = d.pop("superFund1_MemberNumber", UNSET)

        super_fund_1_allocated_percentage = d.pop("superFund1_AllocatedPercentage", UNSET)

        super_fund_1_fixed_amount = d.pop("superFund1_FixedAmount", UNSET)

        super_fund_1_employer_nominated_fund = d.pop("superFund1_EmployerNominatedFund", UNSET)

        super_fund_2_product_code = d.pop("superFund2_ProductCode", UNSET)

        super_fund_2_fund_name = d.pop("superFund2_FundName", UNSET)

        super_fund_2_member_number = d.pop("superFund2_MemberNumber", UNSET)

        super_fund_2_allocated_percentage = d.pop("superFund2_AllocatedPercentage", UNSET)

        super_fund_2_fixed_amount = d.pop("superFund2_FixedAmount", UNSET)

        super_fund_2_employer_nominated_fund = d.pop("superFund2_EmployerNominatedFund", UNSET)

        super_fund_3_product_code = d.pop("superFund3_ProductCode", UNSET)

        super_fund_3_fund_name = d.pop("superFund3_FundName", UNSET)

        super_fund_3_member_number = d.pop("superFund3_MemberNumber", UNSET)

        super_fund_3_allocated_percentage = d.pop("superFund3_AllocatedPercentage", UNSET)

        super_fund_3_fixed_amount = d.pop("superFund3_FixedAmount", UNSET)

        super_fund_3_employer_nominated_fund = d.pop("superFund3_EmployerNominatedFund", UNSET)

        super_threshold_amount = d.pop("superThresholdAmount", UNSET)

        maximum_quarterly_super_contributions_base = d.pop("maximumQuarterlySuperContributionsBase", UNSET)

        medicare_levy_exemption = d.pop("medicareLevyExemption", UNSET)

        closely_held_employee = d.pop("closelyHeldEmployee", UNSET)

        _closely_held_reporting = d.pop("closelyHeldReporting", UNSET)
        closely_held_reporting: Union[Unset, AuUnstructuredEmployeeModelNullableCloselyHeldReportingEnum]
        if isinstance(_closely_held_reporting, Unset):
            closely_held_reporting = UNSET
        else:
            closely_held_reporting = AuUnstructuredEmployeeModelNullableCloselyHeldReportingEnum(
                _closely_held_reporting
            )

        _single_touch_payroll = d.pop("singleTouchPayroll", UNSET)
        single_touch_payroll: Union[Unset, AuUnstructuredEmployeeModelNullableStpIncomeTypeEnum]
        if isinstance(_single_touch_payroll, Unset):
            single_touch_payroll = UNSET
        else:
            single_touch_payroll = AuUnstructuredEmployeeModelNullableStpIncomeTypeEnum(_single_touch_payroll)

        hours_per_day = d.pop("hoursPerDay", UNSET)

        postal_address_is_overseas = d.pop("postalAddressIsOverseas", UNSET)

        residential_address_is_overseas = d.pop("residentialAddressIsOverseas", UNSET)

        employment_type = d.pop("employmentType", UNSET)

        contractor_abn = d.pop("contractorABN", UNSET)

        termination_reason = d.pop("terminationReason", UNSET)

        _tax_category = d.pop("taxCategory", UNSET)
        tax_category: Union[Unset, AuUnstructuredEmployeeModelNullableTaxFileDeclarationTaxCategoryCombination]
        if isinstance(_tax_category, Unset):
            tax_category = UNSET
        else:
            tax_category = AuUnstructuredEmployeeModelNullableTaxFileDeclarationTaxCategoryCombination(_tax_category)

        _medicare_levy_surcharge_withholding_tier = d.pop("medicareLevySurchargeWithholdingTier", UNSET)
        medicare_levy_surcharge_withholding_tier: Union[
            Unset, AuUnstructuredEmployeeModelNullableMedicareLevySurchargeWithholdingTier
        ]
        if isinstance(_medicare_levy_surcharge_withholding_tier, Unset):
            medicare_levy_surcharge_withholding_tier = UNSET
        else:
            medicare_levy_surcharge_withholding_tier = (
                AuUnstructuredEmployeeModelNullableMedicareLevySurchargeWithholdingTier(
                    _medicare_levy_surcharge_withholding_tier
                )
            )

        claim_medicare_levy_reduction = d.pop("claimMedicareLevyReduction", UNSET)

        medicare_levy_reduction_spouse = d.pop("medicareLevyReductionSpouse", UNSET)

        medicare_levy_reduction_dependent_count = d.pop("medicareLevyReductionDependentCount", UNSET)

        dvl_pay_slip_description = d.pop("dvlPaySlipDescription", UNSET)

        portable_long_service_leave_id = d.pop("portableLongServiceLeaveId", UNSET)

        include_in_portable_long_service_leave_report = d.pop("includeInPortableLongServiceLeaveReport", UNSET)

        automatically_apply_public_holiday_not_worked_earnings_lines = d.pop(
            "automaticallyApplyPublicHolidayNotWorkedEarningsLines", UNSET
        )

        award_id = d.pop("awardId", UNSET)

        employment_agreement_id = d.pop("employmentAgreementId", UNSET)

        disable_auto_progression = d.pop("disableAutoProgression", UNSET)

        id = d.pop("id", UNSET)

        title = d.pop("title", UNSET)

        preferred_name = d.pop("preferredName", UNSET)

        first_name = d.pop("firstName", UNSET)

        middle_name = d.pop("middleName", UNSET)

        surname = d.pop("surname", UNSET)

        _date_of_birth = d.pop("dateOfBirth", UNSET)
        date_of_birth: Union[Unset, datetime.datetime]
        if isinstance(_date_of_birth, Unset):
            date_of_birth = UNSET
        else:
            date_of_birth = isoparse(_date_of_birth)

        gender = d.pop("gender", UNSET)

        external_id = d.pop("externalId", UNSET)

        residential_street_address = d.pop("residentialStreetAddress", UNSET)

        residential_address_line_2 = d.pop("residentialAddressLine2", UNSET)

        residential_post_code = d.pop("residentialPostCode", UNSET)

        residential_country = d.pop("residentialCountry", UNSET)

        postal_street_address = d.pop("postalStreetAddress", UNSET)

        postal_address_line_2 = d.pop("postalAddressLine2", UNSET)

        postal_post_code = d.pop("postalPostCode", UNSET)

        postal_country = d.pop("postalCountry", UNSET)

        email_address = d.pop("emailAddress", UNSET)

        home_phone = d.pop("homePhone", UNSET)

        work_phone = d.pop("workPhone", UNSET)

        mobile_phone = d.pop("mobilePhone", UNSET)

        _start_date = d.pop("startDate", UNSET)
        start_date: Union[Unset, datetime.datetime]
        if isinstance(_start_date, Unset):
            start_date = UNSET
        else:
            start_date = isoparse(_start_date)

        _end_date = d.pop("endDate", UNSET)
        end_date: Union[Unset, datetime.datetime]
        if isinstance(_end_date, Unset):
            end_date = UNSET
        else:
            end_date = isoparse(_end_date)

        _anniversary_date = d.pop("anniversaryDate", UNSET)
        anniversary_date: Union[Unset, datetime.datetime]
        if isinstance(_anniversary_date, Unset):
            anniversary_date = UNSET
        else:
            anniversary_date = isoparse(_anniversary_date)

        tags = d.pop("tags", UNSET)

        job_title = d.pop("jobTitle", UNSET)

        pay_schedule = d.pop("paySchedule", UNSET)

        primary_pay_category = d.pop("primaryPayCategory", UNSET)

        primary_location = d.pop("primaryLocation", UNSET)

        pay_slip_notification_type = d.pop("paySlipNotificationType", UNSET)

        rate = d.pop("rate", UNSET)

        override_template_rate = d.pop("overrideTemplateRate", UNSET)

        rate_unit = d.pop("rateUnit", UNSET)

        hours_per_week = d.pop("hoursPerWeek", UNSET)

        automatically_pay_employee = d.pop("automaticallyPayEmployee", UNSET)

        leave_template = d.pop("leaveTemplate", UNSET)

        pay_rate_template = d.pop("payRateTemplate", UNSET)

        pay_condition_rule_set = d.pop("payConditionRuleSet", UNSET)

        is_enabled_for_timesheets = d.pop("isEnabledForTimesheets", UNSET)

        locations = d.pop("locations", UNSET)

        work_types = d.pop("workTypes", UNSET)

        emergency_contact_1_name = d.pop("emergencyContact1_Name", UNSET)

        emergency_contact_1_relationship = d.pop("emergencyContact1_Relationship", UNSET)

        emergency_contact_1_address = d.pop("emergencyContact1_Address", UNSET)

        emergency_contact_1_contact_number = d.pop("emergencyContact1_ContactNumber", UNSET)

        emergency_contact_1_alternate_contact_number = d.pop("emergencyContact1_AlternateContactNumber", UNSET)

        emergency_contact_2_name = d.pop("emergencyContact2_Name", UNSET)

        emergency_contact_2_relationship = d.pop("emergencyContact2_Relationship", UNSET)

        emergency_contact_2_address = d.pop("emergencyContact2_Address", UNSET)

        emergency_contact_2_contact_number = d.pop("emergencyContact2_ContactNumber", UNSET)

        emergency_contact_2_alternate_contact_number = d.pop("emergencyContact2_AlternateContactNumber", UNSET)

        bank_account_1_account_number = d.pop("bankAccount1_AccountNumber", UNSET)

        bank_account_1_account_name = d.pop("bankAccount1_AccountName", UNSET)

        bank_account_1_allocated_percentage = d.pop("bankAccount1_AllocatedPercentage", UNSET)

        bank_account_1_fixed_amount = d.pop("bankAccount1_FixedAmount", UNSET)

        bank_account_2_account_number = d.pop("bankAccount2_AccountNumber", UNSET)

        bank_account_2_account_name = d.pop("bankAccount2_AccountName", UNSET)

        bank_account_2_allocated_percentage = d.pop("bankAccount2_AllocatedPercentage", UNSET)

        bank_account_2_fixed_amount = d.pop("bankAccount2_FixedAmount", UNSET)

        bank_account_3_account_number = d.pop("bankAccount3_AccountNumber", UNSET)

        bank_account_3_account_name = d.pop("bankAccount3_AccountName", UNSET)

        bank_account_3_allocated_percentage = d.pop("bankAccount3_AllocatedPercentage", UNSET)

        bank_account_3_fixed_amount = d.pop("bankAccount3_FixedAmount", UNSET)

        rostering_notification_choices = d.pop("rosteringNotificationChoices", UNSET)

        _leave_accrual_start_date_type = d.pop("leaveAccrualStartDateType", UNSET)
        leave_accrual_start_date_type: Union[Unset, AuUnstructuredEmployeeModelNullableLeaveAccrualStartDateType]
        if isinstance(_leave_accrual_start_date_type, Unset):
            leave_accrual_start_date_type = UNSET
        else:
            leave_accrual_start_date_type = AuUnstructuredEmployeeModelNullableLeaveAccrualStartDateType(
                _leave_accrual_start_date_type
            )

        _leave_year_start = d.pop("leaveYearStart", UNSET)
        leave_year_start: Union[Unset, datetime.datetime]
        if isinstance(_leave_year_start, Unset):
            leave_year_start = UNSET
        else:
            leave_year_start = isoparse(_leave_year_start)

        _status = d.pop("status", UNSET)
        status: Union[Unset, AuUnstructuredEmployeeModelEmployeeStatusEnum]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = AuUnstructuredEmployeeModelEmployeeStatusEnum(_status)

        _date_created = d.pop("dateCreated", UNSET)
        date_created: Union[Unset, datetime.datetime]
        if isinstance(_date_created, Unset):
            date_created = UNSET
        else:
            date_created = isoparse(_date_created)

        reporting_dimension_values = d.pop("reportingDimensionValues", UNSET)

        au_unstructured_employee_model = cls(
            tax_file_number=tax_file_number,
            residential_suburb=residential_suburb,
            residential_state=residential_state,
            postal_suburb=postal_suburb,
            postal_state=postal_state,
            employing_entity_abn=employing_entity_abn,
            employing_entity_id=employing_entity_id,
            previous_surname=previous_surname,
            australian_resident=australian_resident,
            claim_tax_free_threshold=claim_tax_free_threshold,
            seniors_tax_offset=seniors_tax_offset,
            other_tax_offset=other_tax_offset,
            stsl_debt=stsl_debt,
            is_exempt_from_flood_levy=is_exempt_from_flood_levy,
            has_approved_working_holiday_visa=has_approved_working_holiday_visa,
            working_holiday_visa_country=working_holiday_visa_country,
            working_holiday_visa_start_date=working_holiday_visa_start_date,
            is_seasonal_worker=is_seasonal_worker,
            has_withholding_variation=has_withholding_variation,
            tax_variation=tax_variation,
            date_tax_file_declaration_signed=date_tax_file_declaration_signed,
            date_tax_file_declaration_reported=date_tax_file_declaration_reported,
            business_award_package=business_award_package,
            employment_agreement=employment_agreement,
            is_exempt_from_payroll_tax=is_exempt_from_payroll_tax,
            bank_account_1_bsb=bank_account_1_bsb,
            bank_account_2_bsb=bank_account_2_bsb,
            bank_account_3_bsb=bank_account_3_bsb,
            super_fund_1_product_code=super_fund_1_product_code,
            super_fund_1_fund_name=super_fund_1_fund_name,
            super_fund_1_member_number=super_fund_1_member_number,
            super_fund_1_allocated_percentage=super_fund_1_allocated_percentage,
            super_fund_1_fixed_amount=super_fund_1_fixed_amount,
            super_fund_1_employer_nominated_fund=super_fund_1_employer_nominated_fund,
            super_fund_2_product_code=super_fund_2_product_code,
            super_fund_2_fund_name=super_fund_2_fund_name,
            super_fund_2_member_number=super_fund_2_member_number,
            super_fund_2_allocated_percentage=super_fund_2_allocated_percentage,
            super_fund_2_fixed_amount=super_fund_2_fixed_amount,
            super_fund_2_employer_nominated_fund=super_fund_2_employer_nominated_fund,
            super_fund_3_product_code=super_fund_3_product_code,
            super_fund_3_fund_name=super_fund_3_fund_name,
            super_fund_3_member_number=super_fund_3_member_number,
            super_fund_3_allocated_percentage=super_fund_3_allocated_percentage,
            super_fund_3_fixed_amount=super_fund_3_fixed_amount,
            super_fund_3_employer_nominated_fund=super_fund_3_employer_nominated_fund,
            super_threshold_amount=super_threshold_amount,
            maximum_quarterly_super_contributions_base=maximum_quarterly_super_contributions_base,
            medicare_levy_exemption=medicare_levy_exemption,
            closely_held_employee=closely_held_employee,
            closely_held_reporting=closely_held_reporting,
            single_touch_payroll=single_touch_payroll,
            hours_per_day=hours_per_day,
            postal_address_is_overseas=postal_address_is_overseas,
            residential_address_is_overseas=residential_address_is_overseas,
            employment_type=employment_type,
            contractor_abn=contractor_abn,
            termination_reason=termination_reason,
            tax_category=tax_category,
            medicare_levy_surcharge_withholding_tier=medicare_levy_surcharge_withholding_tier,
            claim_medicare_levy_reduction=claim_medicare_levy_reduction,
            medicare_levy_reduction_spouse=medicare_levy_reduction_spouse,
            medicare_levy_reduction_dependent_count=medicare_levy_reduction_dependent_count,
            dvl_pay_slip_description=dvl_pay_slip_description,
            portable_long_service_leave_id=portable_long_service_leave_id,
            include_in_portable_long_service_leave_report=include_in_portable_long_service_leave_report,
            automatically_apply_public_holiday_not_worked_earnings_lines=automatically_apply_public_holiday_not_worked_earnings_lines,
            award_id=award_id,
            employment_agreement_id=employment_agreement_id,
            disable_auto_progression=disable_auto_progression,
            id=id,
            title=title,
            preferred_name=preferred_name,
            first_name=first_name,
            middle_name=middle_name,
            surname=surname,
            date_of_birth=date_of_birth,
            gender=gender,
            external_id=external_id,
            residential_street_address=residential_street_address,
            residential_address_line_2=residential_address_line_2,
            residential_post_code=residential_post_code,
            residential_country=residential_country,
            postal_street_address=postal_street_address,
            postal_address_line_2=postal_address_line_2,
            postal_post_code=postal_post_code,
            postal_country=postal_country,
            email_address=email_address,
            home_phone=home_phone,
            work_phone=work_phone,
            mobile_phone=mobile_phone,
            start_date=start_date,
            end_date=end_date,
            anniversary_date=anniversary_date,
            tags=tags,
            job_title=job_title,
            pay_schedule=pay_schedule,
            primary_pay_category=primary_pay_category,
            primary_location=primary_location,
            pay_slip_notification_type=pay_slip_notification_type,
            rate=rate,
            override_template_rate=override_template_rate,
            rate_unit=rate_unit,
            hours_per_week=hours_per_week,
            automatically_pay_employee=automatically_pay_employee,
            leave_template=leave_template,
            pay_rate_template=pay_rate_template,
            pay_condition_rule_set=pay_condition_rule_set,
            is_enabled_for_timesheets=is_enabled_for_timesheets,
            locations=locations,
            work_types=work_types,
            emergency_contact_1_name=emergency_contact_1_name,
            emergency_contact_1_relationship=emergency_contact_1_relationship,
            emergency_contact_1_address=emergency_contact_1_address,
            emergency_contact_1_contact_number=emergency_contact_1_contact_number,
            emergency_contact_1_alternate_contact_number=emergency_contact_1_alternate_contact_number,
            emergency_contact_2_name=emergency_contact_2_name,
            emergency_contact_2_relationship=emergency_contact_2_relationship,
            emergency_contact_2_address=emergency_contact_2_address,
            emergency_contact_2_contact_number=emergency_contact_2_contact_number,
            emergency_contact_2_alternate_contact_number=emergency_contact_2_alternate_contact_number,
            bank_account_1_account_number=bank_account_1_account_number,
            bank_account_1_account_name=bank_account_1_account_name,
            bank_account_1_allocated_percentage=bank_account_1_allocated_percentage,
            bank_account_1_fixed_amount=bank_account_1_fixed_amount,
            bank_account_2_account_number=bank_account_2_account_number,
            bank_account_2_account_name=bank_account_2_account_name,
            bank_account_2_allocated_percentage=bank_account_2_allocated_percentage,
            bank_account_2_fixed_amount=bank_account_2_fixed_amount,
            bank_account_3_account_number=bank_account_3_account_number,
            bank_account_3_account_name=bank_account_3_account_name,
            bank_account_3_allocated_percentage=bank_account_3_allocated_percentage,
            bank_account_3_fixed_amount=bank_account_3_fixed_amount,
            rostering_notification_choices=rostering_notification_choices,
            leave_accrual_start_date_type=leave_accrual_start_date_type,
            leave_year_start=leave_year_start,
            status=status,
            date_created=date_created,
            reporting_dimension_values=reporting_dimension_values,
        )

        au_unstructured_employee_model.additional_properties = d
        return au_unstructured_employee_model

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
