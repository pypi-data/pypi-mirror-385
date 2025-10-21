import datetime
from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.au_auto_pay_configuration_model_publish_pay_slips_preference import (
    AuAutoPayConfigurationModelPublishPaySlipsPreference,
)
from ..models.au_auto_pay_configuration_model_timesheet_import_option import (
    AuAutoPayConfigurationModelTimesheetImportOption,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="AuAutoPayConfigurationModel")


@_attrs_define
class AuAutoPayConfigurationModel:
    """
    Attributes:
        enabled (Union[Unset, bool]):
        paused (Union[Unset, bool]):
        initial_pay_period_ending (Union[Unset, datetime.datetime]):
        initial_date_paid (Union[Unset, datetime.datetime]):
        initial_pay_run_creation_date_time (Union[Unset, datetime.datetime]):
        scheduled_end_date (Union[Unset, datetime.datetime]):
        next_scheduled_creation_date_time_utc (Union[Unset, datetime.datetime]):
        finalise (Union[Unset, bool]):
        timesheet_import_option (Union[Unset, AuAutoPayConfigurationModelTimesheetImportOption]):
        export_journals (Union[Unset, bool]):
        lodge_pay_run (Union[Unset, bool]):
        publish_pay_slips (Union[Unset, AuAutoPayConfigurationModelPublishPaySlipsPreference]):
        publish_pay_slips_hour (Union[Unset, int]):
        suppress_notifications (Union[Unset, bool]):
        users_to_notify (Union[Unset, List[str]]):
        run_on_specific_day_of_month (Union[Unset, bool]):
        adjust_run_date_to_work_day (Union[Unset, bool]):
        adjust_date_paid_to_work_day (Union[Unset, bool]):
        specific_day_of_month (Union[Unset, int]):
        week_of_month (Union[Unset, int]):
        day_of_week (Union[Unset, int]):
        report_packs_to_run (Union[Unset, List[int]]):
    """

    enabled: Union[Unset, bool] = UNSET
    paused: Union[Unset, bool] = UNSET
    initial_pay_period_ending: Union[Unset, datetime.datetime] = UNSET
    initial_date_paid: Union[Unset, datetime.datetime] = UNSET
    initial_pay_run_creation_date_time: Union[Unset, datetime.datetime] = UNSET
    scheduled_end_date: Union[Unset, datetime.datetime] = UNSET
    next_scheduled_creation_date_time_utc: Union[Unset, datetime.datetime] = UNSET
    finalise: Union[Unset, bool] = UNSET
    timesheet_import_option: Union[Unset, AuAutoPayConfigurationModelTimesheetImportOption] = UNSET
    export_journals: Union[Unset, bool] = UNSET
    lodge_pay_run: Union[Unset, bool] = UNSET
    publish_pay_slips: Union[Unset, AuAutoPayConfigurationModelPublishPaySlipsPreference] = UNSET
    publish_pay_slips_hour: Union[Unset, int] = UNSET
    suppress_notifications: Union[Unset, bool] = UNSET
    users_to_notify: Union[Unset, List[str]] = UNSET
    run_on_specific_day_of_month: Union[Unset, bool] = UNSET
    adjust_run_date_to_work_day: Union[Unset, bool] = UNSET
    adjust_date_paid_to_work_day: Union[Unset, bool] = UNSET
    specific_day_of_month: Union[Unset, int] = UNSET
    week_of_month: Union[Unset, int] = UNSET
    day_of_week: Union[Unset, int] = UNSET
    report_packs_to_run: Union[Unset, List[int]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        enabled = self.enabled

        paused = self.paused

        initial_pay_period_ending: Union[Unset, str] = UNSET
        if not isinstance(self.initial_pay_period_ending, Unset):
            initial_pay_period_ending = self.initial_pay_period_ending.isoformat()

        initial_date_paid: Union[Unset, str] = UNSET
        if not isinstance(self.initial_date_paid, Unset):
            initial_date_paid = self.initial_date_paid.isoformat()

        initial_pay_run_creation_date_time: Union[Unset, str] = UNSET
        if not isinstance(self.initial_pay_run_creation_date_time, Unset):
            initial_pay_run_creation_date_time = self.initial_pay_run_creation_date_time.isoformat()

        scheduled_end_date: Union[Unset, str] = UNSET
        if not isinstance(self.scheduled_end_date, Unset):
            scheduled_end_date = self.scheduled_end_date.isoformat()

        next_scheduled_creation_date_time_utc: Union[Unset, str] = UNSET
        if not isinstance(self.next_scheduled_creation_date_time_utc, Unset):
            next_scheduled_creation_date_time_utc = self.next_scheduled_creation_date_time_utc.isoformat()

        finalise = self.finalise

        timesheet_import_option: Union[Unset, str] = UNSET
        if not isinstance(self.timesheet_import_option, Unset):
            timesheet_import_option = self.timesheet_import_option.value

        export_journals = self.export_journals

        lodge_pay_run = self.lodge_pay_run

        publish_pay_slips: Union[Unset, str] = UNSET
        if not isinstance(self.publish_pay_slips, Unset):
            publish_pay_slips = self.publish_pay_slips.value

        publish_pay_slips_hour = self.publish_pay_slips_hour

        suppress_notifications = self.suppress_notifications

        users_to_notify: Union[Unset, List[str]] = UNSET
        if not isinstance(self.users_to_notify, Unset):
            users_to_notify = self.users_to_notify

        run_on_specific_day_of_month = self.run_on_specific_day_of_month

        adjust_run_date_to_work_day = self.adjust_run_date_to_work_day

        adjust_date_paid_to_work_day = self.adjust_date_paid_to_work_day

        specific_day_of_month = self.specific_day_of_month

        week_of_month = self.week_of_month

        day_of_week = self.day_of_week

        report_packs_to_run: Union[Unset, List[int]] = UNSET
        if not isinstance(self.report_packs_to_run, Unset):
            report_packs_to_run = self.report_packs_to_run

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if paused is not UNSET:
            field_dict["paused"] = paused
        if initial_pay_period_ending is not UNSET:
            field_dict["initialPayPeriodEnding"] = initial_pay_period_ending
        if initial_date_paid is not UNSET:
            field_dict["initialDatePaid"] = initial_date_paid
        if initial_pay_run_creation_date_time is not UNSET:
            field_dict["initialPayRunCreationDateTime"] = initial_pay_run_creation_date_time
        if scheduled_end_date is not UNSET:
            field_dict["scheduledEndDate"] = scheduled_end_date
        if next_scheduled_creation_date_time_utc is not UNSET:
            field_dict["nextScheduledCreationDateTimeUtc"] = next_scheduled_creation_date_time_utc
        if finalise is not UNSET:
            field_dict["finalise"] = finalise
        if timesheet_import_option is not UNSET:
            field_dict["timesheetImportOption"] = timesheet_import_option
        if export_journals is not UNSET:
            field_dict["exportJournals"] = export_journals
        if lodge_pay_run is not UNSET:
            field_dict["lodgePayRun"] = lodge_pay_run
        if publish_pay_slips is not UNSET:
            field_dict["publishPaySlips"] = publish_pay_slips
        if publish_pay_slips_hour is not UNSET:
            field_dict["publishPaySlipsHour"] = publish_pay_slips_hour
        if suppress_notifications is not UNSET:
            field_dict["suppressNotifications"] = suppress_notifications
        if users_to_notify is not UNSET:
            field_dict["usersToNotify"] = users_to_notify
        if run_on_specific_day_of_month is not UNSET:
            field_dict["runOnSpecificDayOfMonth"] = run_on_specific_day_of_month
        if adjust_run_date_to_work_day is not UNSET:
            field_dict["adjustRunDateToWorkDay"] = adjust_run_date_to_work_day
        if adjust_date_paid_to_work_day is not UNSET:
            field_dict["adjustDatePaidToWorkDay"] = adjust_date_paid_to_work_day
        if specific_day_of_month is not UNSET:
            field_dict["specificDayOfMonth"] = specific_day_of_month
        if week_of_month is not UNSET:
            field_dict["weekOfMonth"] = week_of_month
        if day_of_week is not UNSET:
            field_dict["dayOfWeek"] = day_of_week
        if report_packs_to_run is not UNSET:
            field_dict["reportPacksToRun"] = report_packs_to_run

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        enabled = d.pop("enabled", UNSET)

        paused = d.pop("paused", UNSET)

        _initial_pay_period_ending = d.pop("initialPayPeriodEnding", UNSET)
        initial_pay_period_ending: Union[Unset, datetime.datetime]
        if isinstance(_initial_pay_period_ending, Unset):
            initial_pay_period_ending = UNSET
        else:
            initial_pay_period_ending = isoparse(_initial_pay_period_ending)

        _initial_date_paid = d.pop("initialDatePaid", UNSET)
        initial_date_paid: Union[Unset, datetime.datetime]
        if isinstance(_initial_date_paid, Unset):
            initial_date_paid = UNSET
        else:
            initial_date_paid = isoparse(_initial_date_paid)

        _initial_pay_run_creation_date_time = d.pop("initialPayRunCreationDateTime", UNSET)
        initial_pay_run_creation_date_time: Union[Unset, datetime.datetime]
        if isinstance(_initial_pay_run_creation_date_time, Unset):
            initial_pay_run_creation_date_time = UNSET
        else:
            initial_pay_run_creation_date_time = isoparse(_initial_pay_run_creation_date_time)

        _scheduled_end_date = d.pop("scheduledEndDate", UNSET)
        scheduled_end_date: Union[Unset, datetime.datetime]
        if isinstance(_scheduled_end_date, Unset):
            scheduled_end_date = UNSET
        else:
            scheduled_end_date = isoparse(_scheduled_end_date)

        _next_scheduled_creation_date_time_utc = d.pop("nextScheduledCreationDateTimeUtc", UNSET)
        next_scheduled_creation_date_time_utc: Union[Unset, datetime.datetime]
        if isinstance(_next_scheduled_creation_date_time_utc, Unset):
            next_scheduled_creation_date_time_utc = UNSET
        else:
            next_scheduled_creation_date_time_utc = isoparse(_next_scheduled_creation_date_time_utc)

        finalise = d.pop("finalise", UNSET)

        _timesheet_import_option = d.pop("timesheetImportOption", UNSET)
        timesheet_import_option: Union[Unset, AuAutoPayConfigurationModelTimesheetImportOption]
        if isinstance(_timesheet_import_option, Unset):
            timesheet_import_option = UNSET
        else:
            timesheet_import_option = AuAutoPayConfigurationModelTimesheetImportOption(_timesheet_import_option)

        export_journals = d.pop("exportJournals", UNSET)

        lodge_pay_run = d.pop("lodgePayRun", UNSET)

        _publish_pay_slips = d.pop("publishPaySlips", UNSET)
        publish_pay_slips: Union[Unset, AuAutoPayConfigurationModelPublishPaySlipsPreference]
        if isinstance(_publish_pay_slips, Unset):
            publish_pay_slips = UNSET
        else:
            publish_pay_slips = AuAutoPayConfigurationModelPublishPaySlipsPreference(_publish_pay_slips)

        publish_pay_slips_hour = d.pop("publishPaySlipsHour", UNSET)

        suppress_notifications = d.pop("suppressNotifications", UNSET)

        users_to_notify = cast(List[str], d.pop("usersToNotify", UNSET))

        run_on_specific_day_of_month = d.pop("runOnSpecificDayOfMonth", UNSET)

        adjust_run_date_to_work_day = d.pop("adjustRunDateToWorkDay", UNSET)

        adjust_date_paid_to_work_day = d.pop("adjustDatePaidToWorkDay", UNSET)

        specific_day_of_month = d.pop("specificDayOfMonth", UNSET)

        week_of_month = d.pop("weekOfMonth", UNSET)

        day_of_week = d.pop("dayOfWeek", UNSET)

        report_packs_to_run = cast(List[int], d.pop("reportPacksToRun", UNSET))

        au_auto_pay_configuration_model = cls(
            enabled=enabled,
            paused=paused,
            initial_pay_period_ending=initial_pay_period_ending,
            initial_date_paid=initial_date_paid,
            initial_pay_run_creation_date_time=initial_pay_run_creation_date_time,
            scheduled_end_date=scheduled_end_date,
            next_scheduled_creation_date_time_utc=next_scheduled_creation_date_time_utc,
            finalise=finalise,
            timesheet_import_option=timesheet_import_option,
            export_journals=export_journals,
            lodge_pay_run=lodge_pay_run,
            publish_pay_slips=publish_pay_slips,
            publish_pay_slips_hour=publish_pay_slips_hour,
            suppress_notifications=suppress_notifications,
            users_to_notify=users_to_notify,
            run_on_specific_day_of_month=run_on_specific_day_of_month,
            adjust_run_date_to_work_day=adjust_run_date_to_work_day,
            adjust_date_paid_to_work_day=adjust_date_paid_to_work_day,
            specific_day_of_month=specific_day_of_month,
            week_of_month=week_of_month,
            day_of_week=day_of_week,
            report_packs_to_run=report_packs_to_run,
        )

        au_auto_pay_configuration_model.additional_properties = d
        return au_auto_pay_configuration_model

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
