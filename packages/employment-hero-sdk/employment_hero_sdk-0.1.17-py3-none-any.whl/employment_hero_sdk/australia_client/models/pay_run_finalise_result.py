import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.pay_run_finalise_result_pay_run_finalise_action_preference import (
    PayRunFinaliseResultPayRunFinaliseActionPreference,
)
from ..models.pay_run_finalise_result_publish_pay_slips_preference import PayRunFinaliseResultPublishPaySlipsPreference
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.journal_export_result import JournalExportResult
    from ..models.pay_run_super_batch_model import PayRunSuperBatchModel
    from ..models.pay_slip_notification_response import PaySlipNotificationResponse


T = TypeVar("T", bound="PayRunFinaliseResult")


@_attrs_define
class PayRunFinaliseResult:
    """
    Attributes:
        journal_export_result (Union[Unset, JournalExportResult]):
        journal_export_failed_message (Union[Unset, str]):
        removed_employees (Union[Unset, List[int]]):
        notifications (Union[Unset, PaySlipNotificationResponse]):
        pay_slips_published (Union[Unset, bool]):
        publish_preference (Union[Unset, PayRunFinaliseResultPublishPaySlipsPreference]):
        date_paid (Union[Unset, datetime.datetime]):
        export_journals_preference (Union[Unset, bool]):
        publish_pay_slips_scheduled_date_time_utc (Union[Unset, datetime.datetime]):
        pay_run_lodgement_job_id (Union[Unset, str]):  Example: 00000000-0000-0000-0000-000000000000.
        pension_sync_job_id (Union[Unset, str]):  Example: 00000000-0000-0000-0000-000000000000.
        active_employees (Union[Unset, int]):
        publish_pay_slips (Union[Unset, PayRunFinaliseResultPayRunFinaliseActionPreference]):
        publish_preference_time_of_day (Union[Unset, str]):
        export_journals (Union[Unset, PayRunFinaliseResultPayRunFinaliseActionPreference]):
        export_journals_scheduled_date_time_utc (Union[Unset, datetime.datetime]):
        lodge_pay_run (Union[Unset, PayRunFinaliseResultPayRunFinaliseActionPreference]):
        lodge_pay_run_scheduled_date_time_utc (Union[Unset, datetime.datetime]):
        run_report_packs (Union[Unset, PayRunFinaliseResultPayRunFinaliseActionPreference]):
        run_report_packs_scheduled_date_time_utc (Union[Unset, datetime.datetime]):
        are_report_packs_processed (Union[Unset, bool]):
        selected_report_packs (Union[Unset, List[str]]):
        submit_to_pension_sync (Union[Unset, PayRunFinaliseResultPayRunFinaliseActionPreference]):
        submit_to_pension_sync_scheduled_date_time_utc (Union[Unset, datetime.datetime]):
        super_payments (Union[Unset, List['PayRunSuperBatchModel']]):
        is_first_finalisation (Union[Unset, bool]):
    """

    journal_export_result: Union[Unset, "JournalExportResult"] = UNSET
    journal_export_failed_message: Union[Unset, str] = UNSET
    removed_employees: Union[Unset, List[int]] = UNSET
    notifications: Union[Unset, "PaySlipNotificationResponse"] = UNSET
    pay_slips_published: Union[Unset, bool] = UNSET
    publish_preference: Union[Unset, PayRunFinaliseResultPublishPaySlipsPreference] = UNSET
    date_paid: Union[Unset, datetime.datetime] = UNSET
    export_journals_preference: Union[Unset, bool] = UNSET
    publish_pay_slips_scheduled_date_time_utc: Union[Unset, datetime.datetime] = UNSET
    pay_run_lodgement_job_id: Union[Unset, str] = UNSET
    pension_sync_job_id: Union[Unset, str] = UNSET
    active_employees: Union[Unset, int] = UNSET
    publish_pay_slips: Union[Unset, PayRunFinaliseResultPayRunFinaliseActionPreference] = UNSET
    publish_preference_time_of_day: Union[Unset, str] = UNSET
    export_journals: Union[Unset, PayRunFinaliseResultPayRunFinaliseActionPreference] = UNSET
    export_journals_scheduled_date_time_utc: Union[Unset, datetime.datetime] = UNSET
    lodge_pay_run: Union[Unset, PayRunFinaliseResultPayRunFinaliseActionPreference] = UNSET
    lodge_pay_run_scheduled_date_time_utc: Union[Unset, datetime.datetime] = UNSET
    run_report_packs: Union[Unset, PayRunFinaliseResultPayRunFinaliseActionPreference] = UNSET
    run_report_packs_scheduled_date_time_utc: Union[Unset, datetime.datetime] = UNSET
    are_report_packs_processed: Union[Unset, bool] = UNSET
    selected_report_packs: Union[Unset, List[str]] = UNSET
    submit_to_pension_sync: Union[Unset, PayRunFinaliseResultPayRunFinaliseActionPreference] = UNSET
    submit_to_pension_sync_scheduled_date_time_utc: Union[Unset, datetime.datetime] = UNSET
    super_payments: Union[Unset, List["PayRunSuperBatchModel"]] = UNSET
    is_first_finalisation: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        journal_export_result: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.journal_export_result, Unset):
            journal_export_result = self.journal_export_result.to_dict()

        journal_export_failed_message = self.journal_export_failed_message

        removed_employees: Union[Unset, List[int]] = UNSET
        if not isinstance(self.removed_employees, Unset):
            removed_employees = self.removed_employees

        notifications: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.notifications, Unset):
            notifications = self.notifications.to_dict()

        pay_slips_published = self.pay_slips_published

        publish_preference: Union[Unset, str] = UNSET
        if not isinstance(self.publish_preference, Unset):
            publish_preference = self.publish_preference.value

        date_paid: Union[Unset, str] = UNSET
        if not isinstance(self.date_paid, Unset):
            date_paid = self.date_paid.isoformat()

        export_journals_preference = self.export_journals_preference

        publish_pay_slips_scheduled_date_time_utc: Union[Unset, str] = UNSET
        if not isinstance(self.publish_pay_slips_scheduled_date_time_utc, Unset):
            publish_pay_slips_scheduled_date_time_utc = self.publish_pay_slips_scheduled_date_time_utc.isoformat()

        pay_run_lodgement_job_id = self.pay_run_lodgement_job_id

        pension_sync_job_id = self.pension_sync_job_id

        active_employees = self.active_employees

        publish_pay_slips: Union[Unset, str] = UNSET
        if not isinstance(self.publish_pay_slips, Unset):
            publish_pay_slips = self.publish_pay_slips.value

        publish_preference_time_of_day = self.publish_preference_time_of_day

        export_journals: Union[Unset, str] = UNSET
        if not isinstance(self.export_journals, Unset):
            export_journals = self.export_journals.value

        export_journals_scheduled_date_time_utc: Union[Unset, str] = UNSET
        if not isinstance(self.export_journals_scheduled_date_time_utc, Unset):
            export_journals_scheduled_date_time_utc = self.export_journals_scheduled_date_time_utc.isoformat()

        lodge_pay_run: Union[Unset, str] = UNSET
        if not isinstance(self.lodge_pay_run, Unset):
            lodge_pay_run = self.lodge_pay_run.value

        lodge_pay_run_scheduled_date_time_utc: Union[Unset, str] = UNSET
        if not isinstance(self.lodge_pay_run_scheduled_date_time_utc, Unset):
            lodge_pay_run_scheduled_date_time_utc = self.lodge_pay_run_scheduled_date_time_utc.isoformat()

        run_report_packs: Union[Unset, str] = UNSET
        if not isinstance(self.run_report_packs, Unset):
            run_report_packs = self.run_report_packs.value

        run_report_packs_scheduled_date_time_utc: Union[Unset, str] = UNSET
        if not isinstance(self.run_report_packs_scheduled_date_time_utc, Unset):
            run_report_packs_scheduled_date_time_utc = self.run_report_packs_scheduled_date_time_utc.isoformat()

        are_report_packs_processed = self.are_report_packs_processed

        selected_report_packs: Union[Unset, List[str]] = UNSET
        if not isinstance(self.selected_report_packs, Unset):
            selected_report_packs = self.selected_report_packs

        submit_to_pension_sync: Union[Unset, str] = UNSET
        if not isinstance(self.submit_to_pension_sync, Unset):
            submit_to_pension_sync = self.submit_to_pension_sync.value

        submit_to_pension_sync_scheduled_date_time_utc: Union[Unset, str] = UNSET
        if not isinstance(self.submit_to_pension_sync_scheduled_date_time_utc, Unset):
            submit_to_pension_sync_scheduled_date_time_utc = (
                self.submit_to_pension_sync_scheduled_date_time_utc.isoformat()
            )

        super_payments: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.super_payments, Unset):
            super_payments = []
            for super_payments_item_data in self.super_payments:
                super_payments_item = super_payments_item_data.to_dict()
                super_payments.append(super_payments_item)

        is_first_finalisation = self.is_first_finalisation

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if journal_export_result is not UNSET:
            field_dict["journalExportResult"] = journal_export_result
        if journal_export_failed_message is not UNSET:
            field_dict["journalExportFailedMessage"] = journal_export_failed_message
        if removed_employees is not UNSET:
            field_dict["removedEmployees"] = removed_employees
        if notifications is not UNSET:
            field_dict["notifications"] = notifications
        if pay_slips_published is not UNSET:
            field_dict["paySlipsPublished"] = pay_slips_published
        if publish_preference is not UNSET:
            field_dict["publishPreference"] = publish_preference
        if date_paid is not UNSET:
            field_dict["datePaid"] = date_paid
        if export_journals_preference is not UNSET:
            field_dict["exportJournalsPreference"] = export_journals_preference
        if publish_pay_slips_scheduled_date_time_utc is not UNSET:
            field_dict["publishPaySlipsScheduledDateTimeUtc"] = publish_pay_slips_scheduled_date_time_utc
        if pay_run_lodgement_job_id is not UNSET:
            field_dict["payRunLodgementJobId"] = pay_run_lodgement_job_id
        if pension_sync_job_id is not UNSET:
            field_dict["pensionSyncJobId"] = pension_sync_job_id
        if active_employees is not UNSET:
            field_dict["activeEmployees"] = active_employees
        if publish_pay_slips is not UNSET:
            field_dict["publishPaySlips"] = publish_pay_slips
        if publish_preference_time_of_day is not UNSET:
            field_dict["publishPreferenceTimeOfDay"] = publish_preference_time_of_day
        if export_journals is not UNSET:
            field_dict["exportJournals"] = export_journals
        if export_journals_scheduled_date_time_utc is not UNSET:
            field_dict["exportJournalsScheduledDateTimeUtc"] = export_journals_scheduled_date_time_utc
        if lodge_pay_run is not UNSET:
            field_dict["lodgePayRun"] = lodge_pay_run
        if lodge_pay_run_scheduled_date_time_utc is not UNSET:
            field_dict["lodgePayRunScheduledDateTimeUtc"] = lodge_pay_run_scheduled_date_time_utc
        if run_report_packs is not UNSET:
            field_dict["runReportPacks"] = run_report_packs
        if run_report_packs_scheduled_date_time_utc is not UNSET:
            field_dict["runReportPacksScheduledDateTimeUtc"] = run_report_packs_scheduled_date_time_utc
        if are_report_packs_processed is not UNSET:
            field_dict["areReportPacksProcessed"] = are_report_packs_processed
        if selected_report_packs is not UNSET:
            field_dict["selectedReportPacks"] = selected_report_packs
        if submit_to_pension_sync is not UNSET:
            field_dict["submitToPensionSync"] = submit_to_pension_sync
        if submit_to_pension_sync_scheduled_date_time_utc is not UNSET:
            field_dict["submitToPensionSyncScheduledDateTimeUtc"] = submit_to_pension_sync_scheduled_date_time_utc
        if super_payments is not UNSET:
            field_dict["superPayments"] = super_payments
        if is_first_finalisation is not UNSET:
            field_dict["isFirstFinalisation"] = is_first_finalisation

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.journal_export_result import JournalExportResult
        from ..models.pay_run_super_batch_model import PayRunSuperBatchModel
        from ..models.pay_slip_notification_response import PaySlipNotificationResponse

        d = src_dict.copy()
        _journal_export_result = d.pop("journalExportResult", UNSET)
        journal_export_result: Union[Unset, JournalExportResult]
        if isinstance(_journal_export_result, Unset):
            journal_export_result = UNSET
        else:
            journal_export_result = JournalExportResult.from_dict(_journal_export_result)

        journal_export_failed_message = d.pop("journalExportFailedMessage", UNSET)

        removed_employees = cast(List[int], d.pop("removedEmployees", UNSET))

        _notifications = d.pop("notifications", UNSET)
        notifications: Union[Unset, PaySlipNotificationResponse]
        if isinstance(_notifications, Unset):
            notifications = UNSET
        else:
            notifications = PaySlipNotificationResponse.from_dict(_notifications)

        pay_slips_published = d.pop("paySlipsPublished", UNSET)

        _publish_preference = d.pop("publishPreference", UNSET)
        publish_preference: Union[Unset, PayRunFinaliseResultPublishPaySlipsPreference]
        if isinstance(_publish_preference, Unset):
            publish_preference = UNSET
        else:
            publish_preference = PayRunFinaliseResultPublishPaySlipsPreference(_publish_preference)

        _date_paid = d.pop("datePaid", UNSET)
        date_paid: Union[Unset, datetime.datetime]
        if isinstance(_date_paid, Unset):
            date_paid = UNSET
        else:
            date_paid = isoparse(_date_paid)

        export_journals_preference = d.pop("exportJournalsPreference", UNSET)

        _publish_pay_slips_scheduled_date_time_utc = d.pop("publishPaySlipsScheduledDateTimeUtc", UNSET)
        publish_pay_slips_scheduled_date_time_utc: Union[Unset, datetime.datetime]
        if isinstance(_publish_pay_slips_scheduled_date_time_utc, Unset):
            publish_pay_slips_scheduled_date_time_utc = UNSET
        else:
            publish_pay_slips_scheduled_date_time_utc = isoparse(_publish_pay_slips_scheduled_date_time_utc)

        pay_run_lodgement_job_id = d.pop("payRunLodgementJobId", UNSET)

        pension_sync_job_id = d.pop("pensionSyncJobId", UNSET)

        active_employees = d.pop("activeEmployees", UNSET)

        _publish_pay_slips = d.pop("publishPaySlips", UNSET)
        publish_pay_slips: Union[Unset, PayRunFinaliseResultPayRunFinaliseActionPreference]
        if isinstance(_publish_pay_slips, Unset):
            publish_pay_slips = UNSET
        else:
            publish_pay_slips = PayRunFinaliseResultPayRunFinaliseActionPreference(_publish_pay_slips)

        publish_preference_time_of_day = d.pop("publishPreferenceTimeOfDay", UNSET)

        _export_journals = d.pop("exportJournals", UNSET)
        export_journals: Union[Unset, PayRunFinaliseResultPayRunFinaliseActionPreference]
        if isinstance(_export_journals, Unset):
            export_journals = UNSET
        else:
            export_journals = PayRunFinaliseResultPayRunFinaliseActionPreference(_export_journals)

        _export_journals_scheduled_date_time_utc = d.pop("exportJournalsScheduledDateTimeUtc", UNSET)
        export_journals_scheduled_date_time_utc: Union[Unset, datetime.datetime]
        if isinstance(_export_journals_scheduled_date_time_utc, Unset):
            export_journals_scheduled_date_time_utc = UNSET
        else:
            export_journals_scheduled_date_time_utc = isoparse(_export_journals_scheduled_date_time_utc)

        _lodge_pay_run = d.pop("lodgePayRun", UNSET)
        lodge_pay_run: Union[Unset, PayRunFinaliseResultPayRunFinaliseActionPreference]
        if isinstance(_lodge_pay_run, Unset):
            lodge_pay_run = UNSET
        else:
            lodge_pay_run = PayRunFinaliseResultPayRunFinaliseActionPreference(_lodge_pay_run)

        _lodge_pay_run_scheduled_date_time_utc = d.pop("lodgePayRunScheduledDateTimeUtc", UNSET)
        lodge_pay_run_scheduled_date_time_utc: Union[Unset, datetime.datetime]
        if isinstance(_lodge_pay_run_scheduled_date_time_utc, Unset):
            lodge_pay_run_scheduled_date_time_utc = UNSET
        else:
            lodge_pay_run_scheduled_date_time_utc = isoparse(_lodge_pay_run_scheduled_date_time_utc)

        _run_report_packs = d.pop("runReportPacks", UNSET)
        run_report_packs: Union[Unset, PayRunFinaliseResultPayRunFinaliseActionPreference]
        if isinstance(_run_report_packs, Unset):
            run_report_packs = UNSET
        else:
            run_report_packs = PayRunFinaliseResultPayRunFinaliseActionPreference(_run_report_packs)

        _run_report_packs_scheduled_date_time_utc = d.pop("runReportPacksScheduledDateTimeUtc", UNSET)
        run_report_packs_scheduled_date_time_utc: Union[Unset, datetime.datetime]
        if isinstance(_run_report_packs_scheduled_date_time_utc, Unset):
            run_report_packs_scheduled_date_time_utc = UNSET
        else:
            run_report_packs_scheduled_date_time_utc = isoparse(_run_report_packs_scheduled_date_time_utc)

        are_report_packs_processed = d.pop("areReportPacksProcessed", UNSET)

        selected_report_packs = cast(List[str], d.pop("selectedReportPacks", UNSET))

        _submit_to_pension_sync = d.pop("submitToPensionSync", UNSET)
        submit_to_pension_sync: Union[Unset, PayRunFinaliseResultPayRunFinaliseActionPreference]
        if isinstance(_submit_to_pension_sync, Unset):
            submit_to_pension_sync = UNSET
        else:
            submit_to_pension_sync = PayRunFinaliseResultPayRunFinaliseActionPreference(_submit_to_pension_sync)

        _submit_to_pension_sync_scheduled_date_time_utc = d.pop("submitToPensionSyncScheduledDateTimeUtc", UNSET)
        submit_to_pension_sync_scheduled_date_time_utc: Union[Unset, datetime.datetime]
        if isinstance(_submit_to_pension_sync_scheduled_date_time_utc, Unset):
            submit_to_pension_sync_scheduled_date_time_utc = UNSET
        else:
            submit_to_pension_sync_scheduled_date_time_utc = isoparse(_submit_to_pension_sync_scheduled_date_time_utc)

        super_payments = []
        _super_payments = d.pop("superPayments", UNSET)
        for super_payments_item_data in _super_payments or []:
            super_payments_item = PayRunSuperBatchModel.from_dict(super_payments_item_data)

            super_payments.append(super_payments_item)

        is_first_finalisation = d.pop("isFirstFinalisation", UNSET)

        pay_run_finalise_result = cls(
            journal_export_result=journal_export_result,
            journal_export_failed_message=journal_export_failed_message,
            removed_employees=removed_employees,
            notifications=notifications,
            pay_slips_published=pay_slips_published,
            publish_preference=publish_preference,
            date_paid=date_paid,
            export_journals_preference=export_journals_preference,
            publish_pay_slips_scheduled_date_time_utc=publish_pay_slips_scheduled_date_time_utc,
            pay_run_lodgement_job_id=pay_run_lodgement_job_id,
            pension_sync_job_id=pension_sync_job_id,
            active_employees=active_employees,
            publish_pay_slips=publish_pay_slips,
            publish_preference_time_of_day=publish_preference_time_of_day,
            export_journals=export_journals,
            export_journals_scheduled_date_time_utc=export_journals_scheduled_date_time_utc,
            lodge_pay_run=lodge_pay_run,
            lodge_pay_run_scheduled_date_time_utc=lodge_pay_run_scheduled_date_time_utc,
            run_report_packs=run_report_packs,
            run_report_packs_scheduled_date_time_utc=run_report_packs_scheduled_date_time_utc,
            are_report_packs_processed=are_report_packs_processed,
            selected_report_packs=selected_report_packs,
            submit_to_pension_sync=submit_to_pension_sync,
            submit_to_pension_sync_scheduled_date_time_utc=submit_to_pension_sync_scheduled_date_time_utc,
            super_payments=super_payments,
            is_first_finalisation=is_first_finalisation,
        )

        pay_run_finalise_result.additional_properties = d
        return pay_run_finalise_result

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
