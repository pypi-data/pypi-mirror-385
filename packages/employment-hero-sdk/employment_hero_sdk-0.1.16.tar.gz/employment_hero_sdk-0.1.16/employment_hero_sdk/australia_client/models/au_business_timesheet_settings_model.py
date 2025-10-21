from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AuBusinessTimesheetSettingsModel")


@_attrs_define
class AuBusinessTimesheetSettingsModel:
    """
    Attributes:
        allow_to_select_higher_classification (Union[Unset, bool]):
        require_start_and_stop_times (Union[Unset, bool]):
        require_work_type (Union[Unset, bool]):
        can_set_require_work_type_setting (Union[Unset, bool]):
        require_location (Union[Unset, bool]):
        include_all_timesheet_notes_in_pay_run (Union[Unset, bool]):
        timesheet_rejection_notifications (Union[Unset, bool]):
        managers_can_create_timesheets_for_employees_that_are_not_enabled (Union[Unset, bool]):
        timesheets_enabled (Union[Unset, bool]):
        approve_if_matches_roster_shift (Union[Unset, bool]):
        allow_paid_breaks (Union[Unset, bool]):
        has_maximum_paid_break_duration (Union[Unset, bool]):
        maximum_paid_break_duration (Union[Unset, int]):
    """

    allow_to_select_higher_classification: Union[Unset, bool] = UNSET
    require_start_and_stop_times: Union[Unset, bool] = UNSET
    require_work_type: Union[Unset, bool] = UNSET
    can_set_require_work_type_setting: Union[Unset, bool] = UNSET
    require_location: Union[Unset, bool] = UNSET
    include_all_timesheet_notes_in_pay_run: Union[Unset, bool] = UNSET
    timesheet_rejection_notifications: Union[Unset, bool] = UNSET
    managers_can_create_timesheets_for_employees_that_are_not_enabled: Union[Unset, bool] = UNSET
    timesheets_enabled: Union[Unset, bool] = UNSET
    approve_if_matches_roster_shift: Union[Unset, bool] = UNSET
    allow_paid_breaks: Union[Unset, bool] = UNSET
    has_maximum_paid_break_duration: Union[Unset, bool] = UNSET
    maximum_paid_break_duration: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        allow_to_select_higher_classification = self.allow_to_select_higher_classification

        require_start_and_stop_times = self.require_start_and_stop_times

        require_work_type = self.require_work_type

        can_set_require_work_type_setting = self.can_set_require_work_type_setting

        require_location = self.require_location

        include_all_timesheet_notes_in_pay_run = self.include_all_timesheet_notes_in_pay_run

        timesheet_rejection_notifications = self.timesheet_rejection_notifications

        managers_can_create_timesheets_for_employees_that_are_not_enabled = (
            self.managers_can_create_timesheets_for_employees_that_are_not_enabled
        )

        timesheets_enabled = self.timesheets_enabled

        approve_if_matches_roster_shift = self.approve_if_matches_roster_shift

        allow_paid_breaks = self.allow_paid_breaks

        has_maximum_paid_break_duration = self.has_maximum_paid_break_duration

        maximum_paid_break_duration = self.maximum_paid_break_duration

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if allow_to_select_higher_classification is not UNSET:
            field_dict["allowToSelectHigherClassification"] = allow_to_select_higher_classification
        if require_start_and_stop_times is not UNSET:
            field_dict["requireStartAndStopTimes"] = require_start_and_stop_times
        if require_work_type is not UNSET:
            field_dict["requireWorkType"] = require_work_type
        if can_set_require_work_type_setting is not UNSET:
            field_dict["canSetRequireWorkTypeSetting"] = can_set_require_work_type_setting
        if require_location is not UNSET:
            field_dict["requireLocation"] = require_location
        if include_all_timesheet_notes_in_pay_run is not UNSET:
            field_dict["includeAllTimesheetNotesInPayRun"] = include_all_timesheet_notes_in_pay_run
        if timesheet_rejection_notifications is not UNSET:
            field_dict["timesheetRejectionNotifications"] = timesheet_rejection_notifications
        if managers_can_create_timesheets_for_employees_that_are_not_enabled is not UNSET:
            field_dict["managersCanCreateTimesheetsForEmployeesThatAreNotEnabled"] = (
                managers_can_create_timesheets_for_employees_that_are_not_enabled
            )
        if timesheets_enabled is not UNSET:
            field_dict["timesheetsEnabled"] = timesheets_enabled
        if approve_if_matches_roster_shift is not UNSET:
            field_dict["approveIfMatchesRosterShift"] = approve_if_matches_roster_shift
        if allow_paid_breaks is not UNSET:
            field_dict["allowPaidBreaks"] = allow_paid_breaks
        if has_maximum_paid_break_duration is not UNSET:
            field_dict["hasMaximumPaidBreakDuration"] = has_maximum_paid_break_duration
        if maximum_paid_break_duration is not UNSET:
            field_dict["maximumPaidBreakDuration"] = maximum_paid_break_duration

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        allow_to_select_higher_classification = d.pop("allowToSelectHigherClassification", UNSET)

        require_start_and_stop_times = d.pop("requireStartAndStopTimes", UNSET)

        require_work_type = d.pop("requireWorkType", UNSET)

        can_set_require_work_type_setting = d.pop("canSetRequireWorkTypeSetting", UNSET)

        require_location = d.pop("requireLocation", UNSET)

        include_all_timesheet_notes_in_pay_run = d.pop("includeAllTimesheetNotesInPayRun", UNSET)

        timesheet_rejection_notifications = d.pop("timesheetRejectionNotifications", UNSET)

        managers_can_create_timesheets_for_employees_that_are_not_enabled = d.pop(
            "managersCanCreateTimesheetsForEmployeesThatAreNotEnabled", UNSET
        )

        timesheets_enabled = d.pop("timesheetsEnabled", UNSET)

        approve_if_matches_roster_shift = d.pop("approveIfMatchesRosterShift", UNSET)

        allow_paid_breaks = d.pop("allowPaidBreaks", UNSET)

        has_maximum_paid_break_duration = d.pop("hasMaximumPaidBreakDuration", UNSET)

        maximum_paid_break_duration = d.pop("maximumPaidBreakDuration", UNSET)

        au_business_timesheet_settings_model = cls(
            allow_to_select_higher_classification=allow_to_select_higher_classification,
            require_start_and_stop_times=require_start_and_stop_times,
            require_work_type=require_work_type,
            can_set_require_work_type_setting=can_set_require_work_type_setting,
            require_location=require_location,
            include_all_timesheet_notes_in_pay_run=include_all_timesheet_notes_in_pay_run,
            timesheet_rejection_notifications=timesheet_rejection_notifications,
            managers_can_create_timesheets_for_employees_that_are_not_enabled=managers_can_create_timesheets_for_employees_that_are_not_enabled,
            timesheets_enabled=timesheets_enabled,
            approve_if_matches_roster_shift=approve_if_matches_roster_shift,
            allow_paid_breaks=allow_paid_breaks,
            has_maximum_paid_break_duration=has_maximum_paid_break_duration,
            maximum_paid_break_duration=maximum_paid_break_duration,
        )

        au_business_timesheet_settings_model.additional_properties = d
        return au_business_timesheet_settings_model

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
