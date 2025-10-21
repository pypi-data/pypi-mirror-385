from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.au_features_model_ess_timesheet_setting import AuFeaturesModelESSTimesheetSetting
from ..types import UNSET, Unset

T = TypeVar("T", bound="AuFeaturesModel")


@_attrs_define
class AuFeaturesModel:
    """
    Attributes:
        allow_employee_super_fund_self_service (Union[Unset, bool]):
        clock_on_can_specify_higher_classification (Union[Unset, bool]):
        allow_employee_leave_self_service (Union[Unset, bool]):
        allow_employee_self_editing (Union[Unset, bool]):
        allow_employee_timesheets_self_service (Union[Unset, bool]):
        allow_employee_to_set_unavailability (Union[Unset, bool]):
        allow_employee_to_decline_shifts (Union[Unset, bool]):
        allow_employee_bank_account_self_service (Union[Unset, bool]):
        allow_employee_satisfaction_survey (Union[Unset, bool]):
        allow_employees_to_view_all_approved_leave (Union[Unset, bool]):
        unavailability_cut_off (Union[Unset, int]):
        allow_employees_to_upload_profile_picture (Union[Unset, bool]):
        allow_employee_rostering_self_service (Union[Unset, bool]):
        allow_employee_expenses_self_service (Union[Unset, bool]):
        allow_employee_qualifications_self_service (Union[Unset, bool]):
        allow_employee_override_tax_codes (Union[Unset, bool]):
        allow_employees_to_edit_kiosk_timesheets (Union[Unset, bool]):
        ess_timesheet_setting (Union[Unset, AuFeaturesModelESSTimesheetSetting]):
        employee_must_accept_shifts (Union[Unset, bool]):
        allow_employee_timesheets_without_start_stop_times (Union[Unset, bool]):
        allow_employee_to_swap_shifts (Union[Unset, bool]):
        clock_on_require_photo (Union[Unset, bool]):
        clock_on_allow_employee_shift_selection (Union[Unset, bool]):
        clock_on_window_minutes (Union[Unset, int]):
        clock_off_window_minutes (Union[Unset, int]):
        timesheets_require_location (Union[Unset, bool]):
        timesheets_require_work_type (Union[Unset, bool]):
        enable_work_zone_clock_on (Union[Unset, bool]):
        shift_bidding (Union[Unset, bool]):
        allow_to_select_higher_classification (Union[Unset, bool]):
        allow_employee_work_eligibility_self_service (Union[Unset, bool]):
        paid_breaks_enabled (Union[Unset, bool]):
        timesheet_dimensions_enabled (Union[Unset, bool]):
    """

    allow_employee_super_fund_self_service: Union[Unset, bool] = UNSET
    clock_on_can_specify_higher_classification: Union[Unset, bool] = UNSET
    allow_employee_leave_self_service: Union[Unset, bool] = UNSET
    allow_employee_self_editing: Union[Unset, bool] = UNSET
    allow_employee_timesheets_self_service: Union[Unset, bool] = UNSET
    allow_employee_to_set_unavailability: Union[Unset, bool] = UNSET
    allow_employee_to_decline_shifts: Union[Unset, bool] = UNSET
    allow_employee_bank_account_self_service: Union[Unset, bool] = UNSET
    allow_employee_satisfaction_survey: Union[Unset, bool] = UNSET
    allow_employees_to_view_all_approved_leave: Union[Unset, bool] = UNSET
    unavailability_cut_off: Union[Unset, int] = UNSET
    allow_employees_to_upload_profile_picture: Union[Unset, bool] = UNSET
    allow_employee_rostering_self_service: Union[Unset, bool] = UNSET
    allow_employee_expenses_self_service: Union[Unset, bool] = UNSET
    allow_employee_qualifications_self_service: Union[Unset, bool] = UNSET
    allow_employee_override_tax_codes: Union[Unset, bool] = UNSET
    allow_employees_to_edit_kiosk_timesheets: Union[Unset, bool] = UNSET
    ess_timesheet_setting: Union[Unset, AuFeaturesModelESSTimesheetSetting] = UNSET
    employee_must_accept_shifts: Union[Unset, bool] = UNSET
    allow_employee_timesheets_without_start_stop_times: Union[Unset, bool] = UNSET
    allow_employee_to_swap_shifts: Union[Unset, bool] = UNSET
    clock_on_require_photo: Union[Unset, bool] = UNSET
    clock_on_allow_employee_shift_selection: Union[Unset, bool] = UNSET
    clock_on_window_minutes: Union[Unset, int] = UNSET
    clock_off_window_minutes: Union[Unset, int] = UNSET
    timesheets_require_location: Union[Unset, bool] = UNSET
    timesheets_require_work_type: Union[Unset, bool] = UNSET
    enable_work_zone_clock_on: Union[Unset, bool] = UNSET
    shift_bidding: Union[Unset, bool] = UNSET
    allow_to_select_higher_classification: Union[Unset, bool] = UNSET
    allow_employee_work_eligibility_self_service: Union[Unset, bool] = UNSET
    paid_breaks_enabled: Union[Unset, bool] = UNSET
    timesheet_dimensions_enabled: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        allow_employee_super_fund_self_service = self.allow_employee_super_fund_self_service

        clock_on_can_specify_higher_classification = self.clock_on_can_specify_higher_classification

        allow_employee_leave_self_service = self.allow_employee_leave_self_service

        allow_employee_self_editing = self.allow_employee_self_editing

        allow_employee_timesheets_self_service = self.allow_employee_timesheets_self_service

        allow_employee_to_set_unavailability = self.allow_employee_to_set_unavailability

        allow_employee_to_decline_shifts = self.allow_employee_to_decline_shifts

        allow_employee_bank_account_self_service = self.allow_employee_bank_account_self_service

        allow_employee_satisfaction_survey = self.allow_employee_satisfaction_survey

        allow_employees_to_view_all_approved_leave = self.allow_employees_to_view_all_approved_leave

        unavailability_cut_off = self.unavailability_cut_off

        allow_employees_to_upload_profile_picture = self.allow_employees_to_upload_profile_picture

        allow_employee_rostering_self_service = self.allow_employee_rostering_self_service

        allow_employee_expenses_self_service = self.allow_employee_expenses_self_service

        allow_employee_qualifications_self_service = self.allow_employee_qualifications_self_service

        allow_employee_override_tax_codes = self.allow_employee_override_tax_codes

        allow_employees_to_edit_kiosk_timesheets = self.allow_employees_to_edit_kiosk_timesheets

        ess_timesheet_setting: Union[Unset, str] = UNSET
        if not isinstance(self.ess_timesheet_setting, Unset):
            ess_timesheet_setting = self.ess_timesheet_setting.value

        employee_must_accept_shifts = self.employee_must_accept_shifts

        allow_employee_timesheets_without_start_stop_times = self.allow_employee_timesheets_without_start_stop_times

        allow_employee_to_swap_shifts = self.allow_employee_to_swap_shifts

        clock_on_require_photo = self.clock_on_require_photo

        clock_on_allow_employee_shift_selection = self.clock_on_allow_employee_shift_selection

        clock_on_window_minutes = self.clock_on_window_minutes

        clock_off_window_minutes = self.clock_off_window_minutes

        timesheets_require_location = self.timesheets_require_location

        timesheets_require_work_type = self.timesheets_require_work_type

        enable_work_zone_clock_on = self.enable_work_zone_clock_on

        shift_bidding = self.shift_bidding

        allow_to_select_higher_classification = self.allow_to_select_higher_classification

        allow_employee_work_eligibility_self_service = self.allow_employee_work_eligibility_self_service

        paid_breaks_enabled = self.paid_breaks_enabled

        timesheet_dimensions_enabled = self.timesheet_dimensions_enabled

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if allow_employee_super_fund_self_service is not UNSET:
            field_dict["allowEmployeeSuperFundSelfService"] = allow_employee_super_fund_self_service
        if clock_on_can_specify_higher_classification is not UNSET:
            field_dict["clockOnCanSpecifyHigherClassification"] = clock_on_can_specify_higher_classification
        if allow_employee_leave_self_service is not UNSET:
            field_dict["allowEmployeeLeaveSelfService"] = allow_employee_leave_self_service
        if allow_employee_self_editing is not UNSET:
            field_dict["allowEmployeeSelfEditing"] = allow_employee_self_editing
        if allow_employee_timesheets_self_service is not UNSET:
            field_dict["allowEmployeeTimesheetsSelfService"] = allow_employee_timesheets_self_service
        if allow_employee_to_set_unavailability is not UNSET:
            field_dict["allowEmployeeToSetUnavailability"] = allow_employee_to_set_unavailability
        if allow_employee_to_decline_shifts is not UNSET:
            field_dict["allowEmployeeToDeclineShifts"] = allow_employee_to_decline_shifts
        if allow_employee_bank_account_self_service is not UNSET:
            field_dict["allowEmployeeBankAccountSelfService"] = allow_employee_bank_account_self_service
        if allow_employee_satisfaction_survey is not UNSET:
            field_dict["allowEmployeeSatisfactionSurvey"] = allow_employee_satisfaction_survey
        if allow_employees_to_view_all_approved_leave is not UNSET:
            field_dict["allowEmployeesToViewAllApprovedLeave"] = allow_employees_to_view_all_approved_leave
        if unavailability_cut_off is not UNSET:
            field_dict["unavailabilityCutOff"] = unavailability_cut_off
        if allow_employees_to_upload_profile_picture is not UNSET:
            field_dict["allowEmployeesToUploadProfilePicture"] = allow_employees_to_upload_profile_picture
        if allow_employee_rostering_self_service is not UNSET:
            field_dict["allowEmployeeRosteringSelfService"] = allow_employee_rostering_self_service
        if allow_employee_expenses_self_service is not UNSET:
            field_dict["allowEmployeeExpensesSelfService"] = allow_employee_expenses_self_service
        if allow_employee_qualifications_self_service is not UNSET:
            field_dict["allowEmployeeQualificationsSelfService"] = allow_employee_qualifications_self_service
        if allow_employee_override_tax_codes is not UNSET:
            field_dict["allowEmployeeOverrideTaxCodes"] = allow_employee_override_tax_codes
        if allow_employees_to_edit_kiosk_timesheets is not UNSET:
            field_dict["allowEmployeesToEditKioskTimesheets"] = allow_employees_to_edit_kiosk_timesheets
        if ess_timesheet_setting is not UNSET:
            field_dict["essTimesheetSetting"] = ess_timesheet_setting
        if employee_must_accept_shifts is not UNSET:
            field_dict["employeeMustAcceptShifts"] = employee_must_accept_shifts
        if allow_employee_timesheets_without_start_stop_times is not UNSET:
            field_dict["allowEmployeeTimesheetsWithoutStartStopTimes"] = (
                allow_employee_timesheets_without_start_stop_times
            )
        if allow_employee_to_swap_shifts is not UNSET:
            field_dict["allowEmployeeToSwapShifts"] = allow_employee_to_swap_shifts
        if clock_on_require_photo is not UNSET:
            field_dict["clockOnRequirePhoto"] = clock_on_require_photo
        if clock_on_allow_employee_shift_selection is not UNSET:
            field_dict["clockOnAllowEmployeeShiftSelection"] = clock_on_allow_employee_shift_selection
        if clock_on_window_minutes is not UNSET:
            field_dict["clockOnWindowMinutes"] = clock_on_window_minutes
        if clock_off_window_minutes is not UNSET:
            field_dict["clockOffWindowMinutes"] = clock_off_window_minutes
        if timesheets_require_location is not UNSET:
            field_dict["timesheetsRequireLocation"] = timesheets_require_location
        if timesheets_require_work_type is not UNSET:
            field_dict["timesheetsRequireWorkType"] = timesheets_require_work_type
        if enable_work_zone_clock_on is not UNSET:
            field_dict["enableWorkZoneClockOn"] = enable_work_zone_clock_on
        if shift_bidding is not UNSET:
            field_dict["shiftBidding"] = shift_bidding
        if allow_to_select_higher_classification is not UNSET:
            field_dict["allowToSelectHigherClassification"] = allow_to_select_higher_classification
        if allow_employee_work_eligibility_self_service is not UNSET:
            field_dict["allowEmployeeWorkEligibilitySelfService"] = allow_employee_work_eligibility_self_service
        if paid_breaks_enabled is not UNSET:
            field_dict["paidBreaksEnabled"] = paid_breaks_enabled
        if timesheet_dimensions_enabled is not UNSET:
            field_dict["timesheetDimensionsEnabled"] = timesheet_dimensions_enabled

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        allow_employee_super_fund_self_service = d.pop("allowEmployeeSuperFundSelfService", UNSET)

        clock_on_can_specify_higher_classification = d.pop("clockOnCanSpecifyHigherClassification", UNSET)

        allow_employee_leave_self_service = d.pop("allowEmployeeLeaveSelfService", UNSET)

        allow_employee_self_editing = d.pop("allowEmployeeSelfEditing", UNSET)

        allow_employee_timesheets_self_service = d.pop("allowEmployeeTimesheetsSelfService", UNSET)

        allow_employee_to_set_unavailability = d.pop("allowEmployeeToSetUnavailability", UNSET)

        allow_employee_to_decline_shifts = d.pop("allowEmployeeToDeclineShifts", UNSET)

        allow_employee_bank_account_self_service = d.pop("allowEmployeeBankAccountSelfService", UNSET)

        allow_employee_satisfaction_survey = d.pop("allowEmployeeSatisfactionSurvey", UNSET)

        allow_employees_to_view_all_approved_leave = d.pop("allowEmployeesToViewAllApprovedLeave", UNSET)

        unavailability_cut_off = d.pop("unavailabilityCutOff", UNSET)

        allow_employees_to_upload_profile_picture = d.pop("allowEmployeesToUploadProfilePicture", UNSET)

        allow_employee_rostering_self_service = d.pop("allowEmployeeRosteringSelfService", UNSET)

        allow_employee_expenses_self_service = d.pop("allowEmployeeExpensesSelfService", UNSET)

        allow_employee_qualifications_self_service = d.pop("allowEmployeeQualificationsSelfService", UNSET)

        allow_employee_override_tax_codes = d.pop("allowEmployeeOverrideTaxCodes", UNSET)

        allow_employees_to_edit_kiosk_timesheets = d.pop("allowEmployeesToEditKioskTimesheets", UNSET)

        _ess_timesheet_setting = d.pop("essTimesheetSetting", UNSET)
        ess_timesheet_setting: Union[Unset, AuFeaturesModelESSTimesheetSetting]
        if isinstance(_ess_timesheet_setting, Unset):
            ess_timesheet_setting = UNSET
        else:
            ess_timesheet_setting = AuFeaturesModelESSTimesheetSetting(_ess_timesheet_setting)

        employee_must_accept_shifts = d.pop("employeeMustAcceptShifts", UNSET)

        allow_employee_timesheets_without_start_stop_times = d.pop(
            "allowEmployeeTimesheetsWithoutStartStopTimes", UNSET
        )

        allow_employee_to_swap_shifts = d.pop("allowEmployeeToSwapShifts", UNSET)

        clock_on_require_photo = d.pop("clockOnRequirePhoto", UNSET)

        clock_on_allow_employee_shift_selection = d.pop("clockOnAllowEmployeeShiftSelection", UNSET)

        clock_on_window_minutes = d.pop("clockOnWindowMinutes", UNSET)

        clock_off_window_minutes = d.pop("clockOffWindowMinutes", UNSET)

        timesheets_require_location = d.pop("timesheetsRequireLocation", UNSET)

        timesheets_require_work_type = d.pop("timesheetsRequireWorkType", UNSET)

        enable_work_zone_clock_on = d.pop("enableWorkZoneClockOn", UNSET)

        shift_bidding = d.pop("shiftBidding", UNSET)

        allow_to_select_higher_classification = d.pop("allowToSelectHigherClassification", UNSET)

        allow_employee_work_eligibility_self_service = d.pop("allowEmployeeWorkEligibilitySelfService", UNSET)

        paid_breaks_enabled = d.pop("paidBreaksEnabled", UNSET)

        timesheet_dimensions_enabled = d.pop("timesheetDimensionsEnabled", UNSET)

        au_features_model = cls(
            allow_employee_super_fund_self_service=allow_employee_super_fund_self_service,
            clock_on_can_specify_higher_classification=clock_on_can_specify_higher_classification,
            allow_employee_leave_self_service=allow_employee_leave_self_service,
            allow_employee_self_editing=allow_employee_self_editing,
            allow_employee_timesheets_self_service=allow_employee_timesheets_self_service,
            allow_employee_to_set_unavailability=allow_employee_to_set_unavailability,
            allow_employee_to_decline_shifts=allow_employee_to_decline_shifts,
            allow_employee_bank_account_self_service=allow_employee_bank_account_self_service,
            allow_employee_satisfaction_survey=allow_employee_satisfaction_survey,
            allow_employees_to_view_all_approved_leave=allow_employees_to_view_all_approved_leave,
            unavailability_cut_off=unavailability_cut_off,
            allow_employees_to_upload_profile_picture=allow_employees_to_upload_profile_picture,
            allow_employee_rostering_self_service=allow_employee_rostering_self_service,
            allow_employee_expenses_self_service=allow_employee_expenses_self_service,
            allow_employee_qualifications_self_service=allow_employee_qualifications_self_service,
            allow_employee_override_tax_codes=allow_employee_override_tax_codes,
            allow_employees_to_edit_kiosk_timesheets=allow_employees_to_edit_kiosk_timesheets,
            ess_timesheet_setting=ess_timesheet_setting,
            employee_must_accept_shifts=employee_must_accept_shifts,
            allow_employee_timesheets_without_start_stop_times=allow_employee_timesheets_without_start_stop_times,
            allow_employee_to_swap_shifts=allow_employee_to_swap_shifts,
            clock_on_require_photo=clock_on_require_photo,
            clock_on_allow_employee_shift_selection=clock_on_allow_employee_shift_selection,
            clock_on_window_minutes=clock_on_window_minutes,
            clock_off_window_minutes=clock_off_window_minutes,
            timesheets_require_location=timesheets_require_location,
            timesheets_require_work_type=timesheets_require_work_type,
            enable_work_zone_clock_on=enable_work_zone_clock_on,
            shift_bidding=shift_bidding,
            allow_to_select_higher_classification=allow_to_select_higher_classification,
            allow_employee_work_eligibility_self_service=allow_employee_work_eligibility_self_service,
            paid_breaks_enabled=paid_breaks_enabled,
            timesheet_dimensions_enabled=timesheet_dimensions_enabled,
        )

        au_features_model.additional_properties = d
        return au_features_model

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
