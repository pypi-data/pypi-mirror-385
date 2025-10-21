import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.au_available_business_model_budget_entry_method_enum import AuAvailableBusinessModelBudgetEntryMethodEnum
from ..models.au_available_business_model_day_of_week import AuAvailableBusinessModelDayOfWeek
from ..models.au_available_business_model_leave_accrual_start_date_type import (
    AuAvailableBusinessModelLeaveAccrualStartDateType,
)
from ..models.au_available_business_model_nullable_billing_status_enum import (
    AuAvailableBusinessModelNullableBillingStatusEnum,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.au_time_and_attendance_kiosk_model import AuTimeAndAttendanceKioskModel
    from ..models.employee_group_permission_model import EmployeeGroupPermissionModel
    from ..models.location_permission_model import LocationPermissionModel
    from ..models.white_label_branding_model import WhiteLabelBrandingModel


T = TypeVar("T", bound="AuAvailableBusinessModel")


@_attrs_define
class AuAvailableBusinessModel:
    """
    Attributes:
        management_software_id (Union[Unset, str]):
        sbr_software_provider (Union[Unset, str]):
        sbr_software_id (Union[Unset, str]):
        kiosks (Union[Unset, List['AuTimeAndAttendanceKioskModel']]):
        abn (Union[Unset, str]):
        branding (Union[Unset, WhiteLabelBrandingModel]):
        timesheet_entry_period_end (Union[Unset, datetime.datetime]):
        is_payroll_admin (Union[Unset, bool]):
        can_approve_leave_requests (Union[Unset, bool]):
        can_view_leave_requests (Union[Unset, bool]):
        can_approve_timesheets (Union[Unset, bool]):
        can_approve_expenses (Union[Unset, bool]):
        can_view_expenses (Union[Unset, bool]):
        can_view_shift_costs (Union[Unset, bool]):
        timesheets_require_work_type (Union[Unset, bool]):
        timesheets_require_location (Union[Unset, bool]):
        allow_employee_timesheets_without_start_stop_times (Union[Unset, bool]):
        can_create_timesheets (Union[Unset, bool]):
        can_create_and_approve_timesheets (Union[Unset, bool]):
        no_timesheet_permissions (Union[Unset, bool]):
        can_view_roster_shifts (Union[Unset, bool]):
        can_manage_roster_shifts (Union[Unset, bool]):
        billing_status (Union[Unset, AuAvailableBusinessModelNullableBillingStatusEnum]):
        paid_breaks_enabled (Union[Unset, bool]):
        location_permissions (Union[Unset, List['LocationPermissionModel']]):
        employee_group_permissions (Union[Unset, List['EmployeeGroupPermissionModel']]):
        timesheet_dimensions_enabled (Union[Unset, bool]):
        id (Union[Unset, int]):
        name (Union[Unset, str]):
        region (Union[Unset, str]):
        registration_number (Union[Unset, str]):
        registration_number_validation_bypassed (Union[Unset, bool]):
        legal_name (Union[Unset, str]):
        contact_name (Union[Unset, str]):
        contact_email_address (Union[Unset, str]):
        contact_phone_number (Union[Unset, str]):
        contact_fax_number (Union[Unset, str]):
        external_id (Union[Unset, str]):
        standard_hours_per_day (Union[Unset, float]):
        journal_service (Union[Unset, str]):
        end_of_week (Union[Unset, AuAvailableBusinessModelDayOfWeek]):
        initial_financial_year_start (Union[Unset, int]):
        managers_can_edit_roster_budgets (Union[Unset, bool]):
        budget_warning_percent (Union[Unset, float]):
        budget_entry_method (Union[Unset, AuAvailableBusinessModelBudgetEntryMethodEnum]):
        address_line_1 (Union[Unset, str]):
        address_line_2 (Union[Unset, str]):
        suburb (Union[Unset, str]):
        post_code (Union[Unset, str]):
        state (Union[Unset, str]):
        white_label_name (Union[Unset, str]):
        promo_code (Union[Unset, str]):
        date_created (Union[Unset, datetime.datetime]):
        leave_accrual_start_date_type (Union[Unset, AuAvailableBusinessModelLeaveAccrualStartDateType]):
        leave_year_start (Union[Unset, datetime.datetime]):
        city (Union[Unset, str]):
        auto_enrolment_staging_date (Union[Unset, datetime.datetime]):
    """

    management_software_id: Union[Unset, str] = UNSET
    sbr_software_provider: Union[Unset, str] = UNSET
    sbr_software_id: Union[Unset, str] = UNSET
    kiosks: Union[Unset, List["AuTimeAndAttendanceKioskModel"]] = UNSET
    abn: Union[Unset, str] = UNSET
    branding: Union[Unset, "WhiteLabelBrandingModel"] = UNSET
    timesheet_entry_period_end: Union[Unset, datetime.datetime] = UNSET
    is_payroll_admin: Union[Unset, bool] = UNSET
    can_approve_leave_requests: Union[Unset, bool] = UNSET
    can_view_leave_requests: Union[Unset, bool] = UNSET
    can_approve_timesheets: Union[Unset, bool] = UNSET
    can_approve_expenses: Union[Unset, bool] = UNSET
    can_view_expenses: Union[Unset, bool] = UNSET
    can_view_shift_costs: Union[Unset, bool] = UNSET
    timesheets_require_work_type: Union[Unset, bool] = UNSET
    timesheets_require_location: Union[Unset, bool] = UNSET
    allow_employee_timesheets_without_start_stop_times: Union[Unset, bool] = UNSET
    can_create_timesheets: Union[Unset, bool] = UNSET
    can_create_and_approve_timesheets: Union[Unset, bool] = UNSET
    no_timesheet_permissions: Union[Unset, bool] = UNSET
    can_view_roster_shifts: Union[Unset, bool] = UNSET
    can_manage_roster_shifts: Union[Unset, bool] = UNSET
    billing_status: Union[Unset, AuAvailableBusinessModelNullableBillingStatusEnum] = UNSET
    paid_breaks_enabled: Union[Unset, bool] = UNSET
    location_permissions: Union[Unset, List["LocationPermissionModel"]] = UNSET
    employee_group_permissions: Union[Unset, List["EmployeeGroupPermissionModel"]] = UNSET
    timesheet_dimensions_enabled: Union[Unset, bool] = UNSET
    id: Union[Unset, int] = UNSET
    name: Union[Unset, str] = UNSET
    region: Union[Unset, str] = UNSET
    registration_number: Union[Unset, str] = UNSET
    registration_number_validation_bypassed: Union[Unset, bool] = UNSET
    legal_name: Union[Unset, str] = UNSET
    contact_name: Union[Unset, str] = UNSET
    contact_email_address: Union[Unset, str] = UNSET
    contact_phone_number: Union[Unset, str] = UNSET
    contact_fax_number: Union[Unset, str] = UNSET
    external_id: Union[Unset, str] = UNSET
    standard_hours_per_day: Union[Unset, float] = UNSET
    journal_service: Union[Unset, str] = UNSET
    end_of_week: Union[Unset, AuAvailableBusinessModelDayOfWeek] = UNSET
    initial_financial_year_start: Union[Unset, int] = UNSET
    managers_can_edit_roster_budgets: Union[Unset, bool] = UNSET
    budget_warning_percent: Union[Unset, float] = UNSET
    budget_entry_method: Union[Unset, AuAvailableBusinessModelBudgetEntryMethodEnum] = UNSET
    address_line_1: Union[Unset, str] = UNSET
    address_line_2: Union[Unset, str] = UNSET
    suburb: Union[Unset, str] = UNSET
    post_code: Union[Unset, str] = UNSET
    state: Union[Unset, str] = UNSET
    white_label_name: Union[Unset, str] = UNSET
    promo_code: Union[Unset, str] = UNSET
    date_created: Union[Unset, datetime.datetime] = UNSET
    leave_accrual_start_date_type: Union[Unset, AuAvailableBusinessModelLeaveAccrualStartDateType] = UNSET
    leave_year_start: Union[Unset, datetime.datetime] = UNSET
    city: Union[Unset, str] = UNSET
    auto_enrolment_staging_date: Union[Unset, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        management_software_id = self.management_software_id

        sbr_software_provider = self.sbr_software_provider

        sbr_software_id = self.sbr_software_id

        kiosks: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.kiosks, Unset):
            kiosks = []
            for kiosks_item_data in self.kiosks:
                kiosks_item = kiosks_item_data.to_dict()
                kiosks.append(kiosks_item)

        abn = self.abn

        branding: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.branding, Unset):
            branding = self.branding.to_dict()

        timesheet_entry_period_end: Union[Unset, str] = UNSET
        if not isinstance(self.timesheet_entry_period_end, Unset):
            timesheet_entry_period_end = self.timesheet_entry_period_end.isoformat()

        is_payroll_admin = self.is_payroll_admin

        can_approve_leave_requests = self.can_approve_leave_requests

        can_view_leave_requests = self.can_view_leave_requests

        can_approve_timesheets = self.can_approve_timesheets

        can_approve_expenses = self.can_approve_expenses

        can_view_expenses = self.can_view_expenses

        can_view_shift_costs = self.can_view_shift_costs

        timesheets_require_work_type = self.timesheets_require_work_type

        timesheets_require_location = self.timesheets_require_location

        allow_employee_timesheets_without_start_stop_times = self.allow_employee_timesheets_without_start_stop_times

        can_create_timesheets = self.can_create_timesheets

        can_create_and_approve_timesheets = self.can_create_and_approve_timesheets

        no_timesheet_permissions = self.no_timesheet_permissions

        can_view_roster_shifts = self.can_view_roster_shifts

        can_manage_roster_shifts = self.can_manage_roster_shifts

        billing_status: Union[Unset, str] = UNSET
        if not isinstance(self.billing_status, Unset):
            billing_status = self.billing_status.value

        paid_breaks_enabled = self.paid_breaks_enabled

        location_permissions: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.location_permissions, Unset):
            location_permissions = []
            for location_permissions_item_data in self.location_permissions:
                location_permissions_item = location_permissions_item_data.to_dict()
                location_permissions.append(location_permissions_item)

        employee_group_permissions: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.employee_group_permissions, Unset):
            employee_group_permissions = []
            for employee_group_permissions_item_data in self.employee_group_permissions:
                employee_group_permissions_item = employee_group_permissions_item_data.to_dict()
                employee_group_permissions.append(employee_group_permissions_item)

        timesheet_dimensions_enabled = self.timesheet_dimensions_enabled

        id = self.id

        name = self.name

        region = self.region

        registration_number = self.registration_number

        registration_number_validation_bypassed = self.registration_number_validation_bypassed

        legal_name = self.legal_name

        contact_name = self.contact_name

        contact_email_address = self.contact_email_address

        contact_phone_number = self.contact_phone_number

        contact_fax_number = self.contact_fax_number

        external_id = self.external_id

        standard_hours_per_day = self.standard_hours_per_day

        journal_service = self.journal_service

        end_of_week: Union[Unset, str] = UNSET
        if not isinstance(self.end_of_week, Unset):
            end_of_week = self.end_of_week.value

        initial_financial_year_start = self.initial_financial_year_start

        managers_can_edit_roster_budgets = self.managers_can_edit_roster_budgets

        budget_warning_percent = self.budget_warning_percent

        budget_entry_method: Union[Unset, str] = UNSET
        if not isinstance(self.budget_entry_method, Unset):
            budget_entry_method = self.budget_entry_method.value

        address_line_1 = self.address_line_1

        address_line_2 = self.address_line_2

        suburb = self.suburb

        post_code = self.post_code

        state = self.state

        white_label_name = self.white_label_name

        promo_code = self.promo_code

        date_created: Union[Unset, str] = UNSET
        if not isinstance(self.date_created, Unset):
            date_created = self.date_created.isoformat()

        leave_accrual_start_date_type: Union[Unset, str] = UNSET
        if not isinstance(self.leave_accrual_start_date_type, Unset):
            leave_accrual_start_date_type = self.leave_accrual_start_date_type.value

        leave_year_start: Union[Unset, str] = UNSET
        if not isinstance(self.leave_year_start, Unset):
            leave_year_start = self.leave_year_start.isoformat()

        city = self.city

        auto_enrolment_staging_date: Union[Unset, str] = UNSET
        if not isinstance(self.auto_enrolment_staging_date, Unset):
            auto_enrolment_staging_date = self.auto_enrolment_staging_date.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if management_software_id is not UNSET:
            field_dict["managementSoftwareId"] = management_software_id
        if sbr_software_provider is not UNSET:
            field_dict["sbrSoftwareProvider"] = sbr_software_provider
        if sbr_software_id is not UNSET:
            field_dict["sbrSoftwareId"] = sbr_software_id
        if kiosks is not UNSET:
            field_dict["kiosks"] = kiosks
        if abn is not UNSET:
            field_dict["abn"] = abn
        if branding is not UNSET:
            field_dict["branding"] = branding
        if timesheet_entry_period_end is not UNSET:
            field_dict["timesheetEntryPeriodEnd"] = timesheet_entry_period_end
        if is_payroll_admin is not UNSET:
            field_dict["isPayrollAdmin"] = is_payroll_admin
        if can_approve_leave_requests is not UNSET:
            field_dict["canApproveLeaveRequests"] = can_approve_leave_requests
        if can_view_leave_requests is not UNSET:
            field_dict["canViewLeaveRequests"] = can_view_leave_requests
        if can_approve_timesheets is not UNSET:
            field_dict["canApproveTimesheets"] = can_approve_timesheets
        if can_approve_expenses is not UNSET:
            field_dict["canApproveExpenses"] = can_approve_expenses
        if can_view_expenses is not UNSET:
            field_dict["canViewExpenses"] = can_view_expenses
        if can_view_shift_costs is not UNSET:
            field_dict["canViewShiftCosts"] = can_view_shift_costs
        if timesheets_require_work_type is not UNSET:
            field_dict["timesheetsRequireWorkType"] = timesheets_require_work_type
        if timesheets_require_location is not UNSET:
            field_dict["timesheetsRequireLocation"] = timesheets_require_location
        if allow_employee_timesheets_without_start_stop_times is not UNSET:
            field_dict["allowEmployeeTimesheetsWithoutStartStopTimes"] = (
                allow_employee_timesheets_without_start_stop_times
            )
        if can_create_timesheets is not UNSET:
            field_dict["canCreateTimesheets"] = can_create_timesheets
        if can_create_and_approve_timesheets is not UNSET:
            field_dict["canCreateAndApproveTimesheets"] = can_create_and_approve_timesheets
        if no_timesheet_permissions is not UNSET:
            field_dict["noTimesheetPermissions"] = no_timesheet_permissions
        if can_view_roster_shifts is not UNSET:
            field_dict["canViewRosterShifts"] = can_view_roster_shifts
        if can_manage_roster_shifts is not UNSET:
            field_dict["canManageRosterShifts"] = can_manage_roster_shifts
        if billing_status is not UNSET:
            field_dict["billingStatus"] = billing_status
        if paid_breaks_enabled is not UNSET:
            field_dict["paidBreaksEnabled"] = paid_breaks_enabled
        if location_permissions is not UNSET:
            field_dict["locationPermissions"] = location_permissions
        if employee_group_permissions is not UNSET:
            field_dict["employeeGroupPermissions"] = employee_group_permissions
        if timesheet_dimensions_enabled is not UNSET:
            field_dict["timesheetDimensionsEnabled"] = timesheet_dimensions_enabled
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if region is not UNSET:
            field_dict["region"] = region
        if registration_number is not UNSET:
            field_dict["registrationNumber"] = registration_number
        if registration_number_validation_bypassed is not UNSET:
            field_dict["registrationNumberValidationBypassed"] = registration_number_validation_bypassed
        if legal_name is not UNSET:
            field_dict["legalName"] = legal_name
        if contact_name is not UNSET:
            field_dict["contactName"] = contact_name
        if contact_email_address is not UNSET:
            field_dict["contactEmailAddress"] = contact_email_address
        if contact_phone_number is not UNSET:
            field_dict["contactPhoneNumber"] = contact_phone_number
        if contact_fax_number is not UNSET:
            field_dict["contactFaxNumber"] = contact_fax_number
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if standard_hours_per_day is not UNSET:
            field_dict["standardHoursPerDay"] = standard_hours_per_day
        if journal_service is not UNSET:
            field_dict["journalService"] = journal_service
        if end_of_week is not UNSET:
            field_dict["endOfWeek"] = end_of_week
        if initial_financial_year_start is not UNSET:
            field_dict["initialFinancialYearStart"] = initial_financial_year_start
        if managers_can_edit_roster_budgets is not UNSET:
            field_dict["managersCanEditRosterBudgets"] = managers_can_edit_roster_budgets
        if budget_warning_percent is not UNSET:
            field_dict["budgetWarningPercent"] = budget_warning_percent
        if budget_entry_method is not UNSET:
            field_dict["budgetEntryMethod"] = budget_entry_method
        if address_line_1 is not UNSET:
            field_dict["addressLine1"] = address_line_1
        if address_line_2 is not UNSET:
            field_dict["addressLine2"] = address_line_2
        if suburb is not UNSET:
            field_dict["suburb"] = suburb
        if post_code is not UNSET:
            field_dict["postCode"] = post_code
        if state is not UNSET:
            field_dict["state"] = state
        if white_label_name is not UNSET:
            field_dict["whiteLabelName"] = white_label_name
        if promo_code is not UNSET:
            field_dict["promoCode"] = promo_code
        if date_created is not UNSET:
            field_dict["dateCreated"] = date_created
        if leave_accrual_start_date_type is not UNSET:
            field_dict["leaveAccrualStartDateType"] = leave_accrual_start_date_type
        if leave_year_start is not UNSET:
            field_dict["leaveYearStart"] = leave_year_start
        if city is not UNSET:
            field_dict["city"] = city
        if auto_enrolment_staging_date is not UNSET:
            field_dict["autoEnrolmentStagingDate"] = auto_enrolment_staging_date

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.au_time_and_attendance_kiosk_model import AuTimeAndAttendanceKioskModel
        from ..models.employee_group_permission_model import EmployeeGroupPermissionModel
        from ..models.location_permission_model import LocationPermissionModel
        from ..models.white_label_branding_model import WhiteLabelBrandingModel

        d = src_dict.copy()
        management_software_id = d.pop("managementSoftwareId", UNSET)

        sbr_software_provider = d.pop("sbrSoftwareProvider", UNSET)

        sbr_software_id = d.pop("sbrSoftwareId", UNSET)

        kiosks = []
        _kiosks = d.pop("kiosks", UNSET)
        for kiosks_item_data in _kiosks or []:
            kiosks_item = AuTimeAndAttendanceKioskModel.from_dict(kiosks_item_data)

            kiosks.append(kiosks_item)

        abn = d.pop("abn", UNSET)

        _branding = d.pop("branding", UNSET)
        branding: Union[Unset, WhiteLabelBrandingModel]
        if isinstance(_branding, Unset):
            branding = UNSET
        else:
            branding = WhiteLabelBrandingModel.from_dict(_branding)

        _timesheet_entry_period_end = d.pop("timesheetEntryPeriodEnd", UNSET)
        timesheet_entry_period_end: Union[Unset, datetime.datetime]
        if isinstance(_timesheet_entry_period_end, Unset):
            timesheet_entry_period_end = UNSET
        else:
            timesheet_entry_period_end = isoparse(_timesheet_entry_period_end)

        is_payroll_admin = d.pop("isPayrollAdmin", UNSET)

        can_approve_leave_requests = d.pop("canApproveLeaveRequests", UNSET)

        can_view_leave_requests = d.pop("canViewLeaveRequests", UNSET)

        can_approve_timesheets = d.pop("canApproveTimesheets", UNSET)

        can_approve_expenses = d.pop("canApproveExpenses", UNSET)

        can_view_expenses = d.pop("canViewExpenses", UNSET)

        can_view_shift_costs = d.pop("canViewShiftCosts", UNSET)

        timesheets_require_work_type = d.pop("timesheetsRequireWorkType", UNSET)

        timesheets_require_location = d.pop("timesheetsRequireLocation", UNSET)

        allow_employee_timesheets_without_start_stop_times = d.pop(
            "allowEmployeeTimesheetsWithoutStartStopTimes", UNSET
        )

        can_create_timesheets = d.pop("canCreateTimesheets", UNSET)

        can_create_and_approve_timesheets = d.pop("canCreateAndApproveTimesheets", UNSET)

        no_timesheet_permissions = d.pop("noTimesheetPermissions", UNSET)

        can_view_roster_shifts = d.pop("canViewRosterShifts", UNSET)

        can_manage_roster_shifts = d.pop("canManageRosterShifts", UNSET)

        _billing_status = d.pop("billingStatus", UNSET)
        billing_status: Union[Unset, AuAvailableBusinessModelNullableBillingStatusEnum]
        if isinstance(_billing_status, Unset):
            billing_status = UNSET
        else:
            billing_status = AuAvailableBusinessModelNullableBillingStatusEnum(_billing_status)

        paid_breaks_enabled = d.pop("paidBreaksEnabled", UNSET)

        location_permissions = []
        _location_permissions = d.pop("locationPermissions", UNSET)
        for location_permissions_item_data in _location_permissions or []:
            location_permissions_item = LocationPermissionModel.from_dict(location_permissions_item_data)

            location_permissions.append(location_permissions_item)

        employee_group_permissions = []
        _employee_group_permissions = d.pop("employeeGroupPermissions", UNSET)
        for employee_group_permissions_item_data in _employee_group_permissions or []:
            employee_group_permissions_item = EmployeeGroupPermissionModel.from_dict(
                employee_group_permissions_item_data
            )

            employee_group_permissions.append(employee_group_permissions_item)

        timesheet_dimensions_enabled = d.pop("timesheetDimensionsEnabled", UNSET)

        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        region = d.pop("region", UNSET)

        registration_number = d.pop("registrationNumber", UNSET)

        registration_number_validation_bypassed = d.pop("registrationNumberValidationBypassed", UNSET)

        legal_name = d.pop("legalName", UNSET)

        contact_name = d.pop("contactName", UNSET)

        contact_email_address = d.pop("contactEmailAddress", UNSET)

        contact_phone_number = d.pop("contactPhoneNumber", UNSET)

        contact_fax_number = d.pop("contactFaxNumber", UNSET)

        external_id = d.pop("externalId", UNSET)

        standard_hours_per_day = d.pop("standardHoursPerDay", UNSET)

        journal_service = d.pop("journalService", UNSET)

        _end_of_week = d.pop("endOfWeek", UNSET)
        end_of_week: Union[Unset, AuAvailableBusinessModelDayOfWeek]
        if isinstance(_end_of_week, Unset):
            end_of_week = UNSET
        else:
            end_of_week = AuAvailableBusinessModelDayOfWeek(_end_of_week)

        initial_financial_year_start = d.pop("initialFinancialYearStart", UNSET)

        managers_can_edit_roster_budgets = d.pop("managersCanEditRosterBudgets", UNSET)

        budget_warning_percent = d.pop("budgetWarningPercent", UNSET)

        _budget_entry_method = d.pop("budgetEntryMethod", UNSET)
        budget_entry_method: Union[Unset, AuAvailableBusinessModelBudgetEntryMethodEnum]
        if isinstance(_budget_entry_method, Unset):
            budget_entry_method = UNSET
        else:
            budget_entry_method = AuAvailableBusinessModelBudgetEntryMethodEnum(_budget_entry_method)

        address_line_1 = d.pop("addressLine1", UNSET)

        address_line_2 = d.pop("addressLine2", UNSET)

        suburb = d.pop("suburb", UNSET)

        post_code = d.pop("postCode", UNSET)

        state = d.pop("state", UNSET)

        white_label_name = d.pop("whiteLabelName", UNSET)

        promo_code = d.pop("promoCode", UNSET)

        _date_created = d.pop("dateCreated", UNSET)
        date_created: Union[Unset, datetime.datetime]
        if isinstance(_date_created, Unset):
            date_created = UNSET
        else:
            date_created = isoparse(_date_created)

        _leave_accrual_start_date_type = d.pop("leaveAccrualStartDateType", UNSET)
        leave_accrual_start_date_type: Union[Unset, AuAvailableBusinessModelLeaveAccrualStartDateType]
        if isinstance(_leave_accrual_start_date_type, Unset):
            leave_accrual_start_date_type = UNSET
        else:
            leave_accrual_start_date_type = AuAvailableBusinessModelLeaveAccrualStartDateType(
                _leave_accrual_start_date_type
            )

        _leave_year_start = d.pop("leaveYearStart", UNSET)
        leave_year_start: Union[Unset, datetime.datetime]
        if isinstance(_leave_year_start, Unset):
            leave_year_start = UNSET
        else:
            leave_year_start = isoparse(_leave_year_start)

        city = d.pop("city", UNSET)

        _auto_enrolment_staging_date = d.pop("autoEnrolmentStagingDate", UNSET)
        auto_enrolment_staging_date: Union[Unset, datetime.datetime]
        if isinstance(_auto_enrolment_staging_date, Unset):
            auto_enrolment_staging_date = UNSET
        else:
            auto_enrolment_staging_date = isoparse(_auto_enrolment_staging_date)

        au_available_business_model = cls(
            management_software_id=management_software_id,
            sbr_software_provider=sbr_software_provider,
            sbr_software_id=sbr_software_id,
            kiosks=kiosks,
            abn=abn,
            branding=branding,
            timesheet_entry_period_end=timesheet_entry_period_end,
            is_payroll_admin=is_payroll_admin,
            can_approve_leave_requests=can_approve_leave_requests,
            can_view_leave_requests=can_view_leave_requests,
            can_approve_timesheets=can_approve_timesheets,
            can_approve_expenses=can_approve_expenses,
            can_view_expenses=can_view_expenses,
            can_view_shift_costs=can_view_shift_costs,
            timesheets_require_work_type=timesheets_require_work_type,
            timesheets_require_location=timesheets_require_location,
            allow_employee_timesheets_without_start_stop_times=allow_employee_timesheets_without_start_stop_times,
            can_create_timesheets=can_create_timesheets,
            can_create_and_approve_timesheets=can_create_and_approve_timesheets,
            no_timesheet_permissions=no_timesheet_permissions,
            can_view_roster_shifts=can_view_roster_shifts,
            can_manage_roster_shifts=can_manage_roster_shifts,
            billing_status=billing_status,
            paid_breaks_enabled=paid_breaks_enabled,
            location_permissions=location_permissions,
            employee_group_permissions=employee_group_permissions,
            timesheet_dimensions_enabled=timesheet_dimensions_enabled,
            id=id,
            name=name,
            region=region,
            registration_number=registration_number,
            registration_number_validation_bypassed=registration_number_validation_bypassed,
            legal_name=legal_name,
            contact_name=contact_name,
            contact_email_address=contact_email_address,
            contact_phone_number=contact_phone_number,
            contact_fax_number=contact_fax_number,
            external_id=external_id,
            standard_hours_per_day=standard_hours_per_day,
            journal_service=journal_service,
            end_of_week=end_of_week,
            initial_financial_year_start=initial_financial_year_start,
            managers_can_edit_roster_budgets=managers_can_edit_roster_budgets,
            budget_warning_percent=budget_warning_percent,
            budget_entry_method=budget_entry_method,
            address_line_1=address_line_1,
            address_line_2=address_line_2,
            suburb=suburb,
            post_code=post_code,
            state=state,
            white_label_name=white_label_name,
            promo_code=promo_code,
            date_created=date_created,
            leave_accrual_start_date_type=leave_accrual_start_date_type,
            leave_year_start=leave_year_start,
            city=city,
            auto_enrolment_staging_date=auto_enrolment_staging_date,
        )

        au_available_business_model.additional_properties = d
        return au_available_business_model

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
