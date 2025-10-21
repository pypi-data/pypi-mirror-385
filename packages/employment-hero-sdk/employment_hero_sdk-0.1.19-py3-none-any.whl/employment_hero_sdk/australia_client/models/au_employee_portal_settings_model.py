from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.au_employee_portal_settings_model_ess_timesheet_setting_model_enum import (
    AuEmployeePortalSettingsModelESSTimesheetSettingModelEnum,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="AuEmployeePortalSettingsModel")


@_attrs_define
class AuEmployeePortalSettingsModel:
    """
    Attributes:
        allow_employee_super_fund_self_service (Union[Unset, bool]):
        can_specify_higher_classification (Union[Unset, bool]):
        allow_employee_leave_self_service (Union[Unset, bool]):
        allow_employee_self_editing (Union[Unset, bool]):
        timesheet_setting (Union[Unset, AuEmployeePortalSettingsModelESSTimesheetSettingModelEnum]):
        allow_employee_to_set_unavailability (Union[Unset, bool]):
        allow_employee_bank_account_self_service (Union[Unset, bool]):
        allow_employee_satisfaction_survey (Union[Unset, bool]):
        allow_employees_to_view_all_approved_leave (Union[Unset, bool]):
        unavailability_cut_off (Union[Unset, int]):
        allow_employees_to_upload_profile_picture (Union[Unset, bool]):
        allow_employee_expenses_self_service (Union[Unset, bool]):
        allow_employee_override_tax_codes (Union[Unset, bool]):
        show_pay_days_in_employee_calendar (Union[Unset, bool]):
        enable_work_zone_clock_on (Union[Unset, bool]):
        require_photo (Union[Unset, bool]):
        allow_employee_shift_selection (Union[Unset, bool]):
        clock_on_window_minutes (Union[Unset, int]):
        clock_off_window_minutes (Union[Unset, int]):
        clock_on_reminder_notification_minutes (Union[Unset, int]):
        clock_off_reminder_notification_minutes (Union[Unset, int]):
        send_employee_details_update_notifications (Union[Unset, bool]):
    """

    allow_employee_super_fund_self_service: Union[Unset, bool] = UNSET
    can_specify_higher_classification: Union[Unset, bool] = UNSET
    allow_employee_leave_self_service: Union[Unset, bool] = UNSET
    allow_employee_self_editing: Union[Unset, bool] = UNSET
    timesheet_setting: Union[Unset, AuEmployeePortalSettingsModelESSTimesheetSettingModelEnum] = UNSET
    allow_employee_to_set_unavailability: Union[Unset, bool] = UNSET
    allow_employee_bank_account_self_service: Union[Unset, bool] = UNSET
    allow_employee_satisfaction_survey: Union[Unset, bool] = UNSET
    allow_employees_to_view_all_approved_leave: Union[Unset, bool] = UNSET
    unavailability_cut_off: Union[Unset, int] = UNSET
    allow_employees_to_upload_profile_picture: Union[Unset, bool] = UNSET
    allow_employee_expenses_self_service: Union[Unset, bool] = UNSET
    allow_employee_override_tax_codes: Union[Unset, bool] = UNSET
    show_pay_days_in_employee_calendar: Union[Unset, bool] = UNSET
    enable_work_zone_clock_on: Union[Unset, bool] = UNSET
    require_photo: Union[Unset, bool] = UNSET
    allow_employee_shift_selection: Union[Unset, bool] = UNSET
    clock_on_window_minutes: Union[Unset, int] = UNSET
    clock_off_window_minutes: Union[Unset, int] = UNSET
    clock_on_reminder_notification_minutes: Union[Unset, int] = UNSET
    clock_off_reminder_notification_minutes: Union[Unset, int] = UNSET
    send_employee_details_update_notifications: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        allow_employee_super_fund_self_service = self.allow_employee_super_fund_self_service

        can_specify_higher_classification = self.can_specify_higher_classification

        allow_employee_leave_self_service = self.allow_employee_leave_self_service

        allow_employee_self_editing = self.allow_employee_self_editing

        timesheet_setting: Union[Unset, str] = UNSET
        if not isinstance(self.timesheet_setting, Unset):
            timesheet_setting = self.timesheet_setting.value

        allow_employee_to_set_unavailability = self.allow_employee_to_set_unavailability

        allow_employee_bank_account_self_service = self.allow_employee_bank_account_self_service

        allow_employee_satisfaction_survey = self.allow_employee_satisfaction_survey

        allow_employees_to_view_all_approved_leave = self.allow_employees_to_view_all_approved_leave

        unavailability_cut_off = self.unavailability_cut_off

        allow_employees_to_upload_profile_picture = self.allow_employees_to_upload_profile_picture

        allow_employee_expenses_self_service = self.allow_employee_expenses_self_service

        allow_employee_override_tax_codes = self.allow_employee_override_tax_codes

        show_pay_days_in_employee_calendar = self.show_pay_days_in_employee_calendar

        enable_work_zone_clock_on = self.enable_work_zone_clock_on

        require_photo = self.require_photo

        allow_employee_shift_selection = self.allow_employee_shift_selection

        clock_on_window_minutes = self.clock_on_window_minutes

        clock_off_window_minutes = self.clock_off_window_minutes

        clock_on_reminder_notification_minutes = self.clock_on_reminder_notification_minutes

        clock_off_reminder_notification_minutes = self.clock_off_reminder_notification_minutes

        send_employee_details_update_notifications = self.send_employee_details_update_notifications

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if allow_employee_super_fund_self_service is not UNSET:
            field_dict["allowEmployeeSuperFundSelfService"] = allow_employee_super_fund_self_service
        if can_specify_higher_classification is not UNSET:
            field_dict["canSpecifyHigherClassification"] = can_specify_higher_classification
        if allow_employee_leave_self_service is not UNSET:
            field_dict["allowEmployeeLeaveSelfService"] = allow_employee_leave_self_service
        if allow_employee_self_editing is not UNSET:
            field_dict["allowEmployeeSelfEditing"] = allow_employee_self_editing
        if timesheet_setting is not UNSET:
            field_dict["timesheetSetting"] = timesheet_setting
        if allow_employee_to_set_unavailability is not UNSET:
            field_dict["allowEmployeeToSetUnavailability"] = allow_employee_to_set_unavailability
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
        if allow_employee_expenses_self_service is not UNSET:
            field_dict["allowEmployeeExpensesSelfService"] = allow_employee_expenses_self_service
        if allow_employee_override_tax_codes is not UNSET:
            field_dict["allowEmployeeOverrideTaxCodes"] = allow_employee_override_tax_codes
        if show_pay_days_in_employee_calendar is not UNSET:
            field_dict["showPayDaysInEmployeeCalendar"] = show_pay_days_in_employee_calendar
        if enable_work_zone_clock_on is not UNSET:
            field_dict["enableWorkZoneClockOn"] = enable_work_zone_clock_on
        if require_photo is not UNSET:
            field_dict["requirePhoto"] = require_photo
        if allow_employee_shift_selection is not UNSET:
            field_dict["allowEmployeeShiftSelection"] = allow_employee_shift_selection
        if clock_on_window_minutes is not UNSET:
            field_dict["clockOnWindowMinutes"] = clock_on_window_minutes
        if clock_off_window_minutes is not UNSET:
            field_dict["clockOffWindowMinutes"] = clock_off_window_minutes
        if clock_on_reminder_notification_minutes is not UNSET:
            field_dict["clockOnReminderNotificationMinutes"] = clock_on_reminder_notification_minutes
        if clock_off_reminder_notification_minutes is not UNSET:
            field_dict["clockOffReminderNotificationMinutes"] = clock_off_reminder_notification_minutes
        if send_employee_details_update_notifications is not UNSET:
            field_dict["sendEmployeeDetailsUpdateNotifications"] = send_employee_details_update_notifications

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        allow_employee_super_fund_self_service = d.pop("allowEmployeeSuperFundSelfService", UNSET)

        can_specify_higher_classification = d.pop("canSpecifyHigherClassification", UNSET)

        allow_employee_leave_self_service = d.pop("allowEmployeeLeaveSelfService", UNSET)

        allow_employee_self_editing = d.pop("allowEmployeeSelfEditing", UNSET)

        _timesheet_setting = d.pop("timesheetSetting", UNSET)
        timesheet_setting: Union[Unset, AuEmployeePortalSettingsModelESSTimesheetSettingModelEnum]
        if isinstance(_timesheet_setting, Unset):
            timesheet_setting = UNSET
        else:
            timesheet_setting = AuEmployeePortalSettingsModelESSTimesheetSettingModelEnum(_timesheet_setting)

        allow_employee_to_set_unavailability = d.pop("allowEmployeeToSetUnavailability", UNSET)

        allow_employee_bank_account_self_service = d.pop("allowEmployeeBankAccountSelfService", UNSET)

        allow_employee_satisfaction_survey = d.pop("allowEmployeeSatisfactionSurvey", UNSET)

        allow_employees_to_view_all_approved_leave = d.pop("allowEmployeesToViewAllApprovedLeave", UNSET)

        unavailability_cut_off = d.pop("unavailabilityCutOff", UNSET)

        allow_employees_to_upload_profile_picture = d.pop("allowEmployeesToUploadProfilePicture", UNSET)

        allow_employee_expenses_self_service = d.pop("allowEmployeeExpensesSelfService", UNSET)

        allow_employee_override_tax_codes = d.pop("allowEmployeeOverrideTaxCodes", UNSET)

        show_pay_days_in_employee_calendar = d.pop("showPayDaysInEmployeeCalendar", UNSET)

        enable_work_zone_clock_on = d.pop("enableWorkZoneClockOn", UNSET)

        require_photo = d.pop("requirePhoto", UNSET)

        allow_employee_shift_selection = d.pop("allowEmployeeShiftSelection", UNSET)

        clock_on_window_minutes = d.pop("clockOnWindowMinutes", UNSET)

        clock_off_window_minutes = d.pop("clockOffWindowMinutes", UNSET)

        clock_on_reminder_notification_minutes = d.pop("clockOnReminderNotificationMinutes", UNSET)

        clock_off_reminder_notification_minutes = d.pop("clockOffReminderNotificationMinutes", UNSET)

        send_employee_details_update_notifications = d.pop("sendEmployeeDetailsUpdateNotifications", UNSET)

        au_employee_portal_settings_model = cls(
            allow_employee_super_fund_self_service=allow_employee_super_fund_self_service,
            can_specify_higher_classification=can_specify_higher_classification,
            allow_employee_leave_self_service=allow_employee_leave_self_service,
            allow_employee_self_editing=allow_employee_self_editing,
            timesheet_setting=timesheet_setting,
            allow_employee_to_set_unavailability=allow_employee_to_set_unavailability,
            allow_employee_bank_account_self_service=allow_employee_bank_account_self_service,
            allow_employee_satisfaction_survey=allow_employee_satisfaction_survey,
            allow_employees_to_view_all_approved_leave=allow_employees_to_view_all_approved_leave,
            unavailability_cut_off=unavailability_cut_off,
            allow_employees_to_upload_profile_picture=allow_employees_to_upload_profile_picture,
            allow_employee_expenses_self_service=allow_employee_expenses_self_service,
            allow_employee_override_tax_codes=allow_employee_override_tax_codes,
            show_pay_days_in_employee_calendar=show_pay_days_in_employee_calendar,
            enable_work_zone_clock_on=enable_work_zone_clock_on,
            require_photo=require_photo,
            allow_employee_shift_selection=allow_employee_shift_selection,
            clock_on_window_minutes=clock_on_window_minutes,
            clock_off_window_minutes=clock_off_window_minutes,
            clock_on_reminder_notification_minutes=clock_on_reminder_notification_minutes,
            clock_off_reminder_notification_minutes=clock_off_reminder_notification_minutes,
            send_employee_details_update_notifications=send_employee_details_update_notifications,
        )

        au_employee_portal_settings_model.additional_properties = d
        return au_employee_portal_settings_model

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
