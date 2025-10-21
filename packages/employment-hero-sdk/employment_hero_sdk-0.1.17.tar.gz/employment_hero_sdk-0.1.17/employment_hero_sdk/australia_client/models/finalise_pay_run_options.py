import datetime
from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.finalise_pay_run_options_nullable_hmrc_fps_late_submission_reason import (
    FinalisePayRunOptionsNullableHmrcFpsLateSubmissionReason,
)
from ..models.finalise_pay_run_options_nullable_pay_run_finalise_action_preference import (
    FinalisePayRunOptionsNullablePayRunFinaliseActionPreference,
)
from ..models.finalise_pay_run_options_publish_pay_slips_preference import (
    FinalisePayRunOptionsPublishPaySlipsPreference,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="FinalisePayRunOptions")


@_attrs_define
class FinalisePayRunOptions:
    """
    Attributes:
        pay_run_id (Union[Unset, int]):
        date_paid (Union[Unset, datetime.datetime]):
        export_journals (Union[Unset, bool]):
        publish_pay_slips (Union[Unset, FinalisePayRunOptionsPublishPaySlipsPreference]):
        publish_pay_slips_date_time (Union[Unset, datetime.datetime]):
        suppress_notifications (Union[Unset, bool]):
        lodge_pay_run (Union[Unset, bool]):
        lodge_pay_run_in_test_mode (Union[Unset, bool]):
        submit_to_pension_sync (Union[Unset, bool]):
        lodge_final_pay_run (Union[Unset, bool]):
        relodge_hmrc_late_submission_reason (Union[Unset, FinalisePayRunOptionsNullableHmrcFpsLateSubmissionReason]):
        relodge_selected_employees_only (Union[Unset, bool]):
        finalise_as_admin (Union[Unset, bool]):
        publish_pay_slips_preference (Union[Unset, FinalisePayRunOptionsNullablePayRunFinaliseActionPreference]):
        export_journals_preference (Union[Unset, FinalisePayRunOptionsNullablePayRunFinaliseActionPreference]):
        export_journals_date_time (Union[Unset, datetime.datetime]):
        lodge_pay_run_preference (Union[Unset, FinalisePayRunOptionsNullablePayRunFinaliseActionPreference]):
        super_payment_preference (Union[Unset, bool]):
        lodge_pay_run_date_time (Union[Unset, datetime.datetime]):
        run_report_packs_preference (Union[Unset, FinalisePayRunOptionsNullablePayRunFinaliseActionPreference]):
        run_report_packs_date_time (Union[Unset, datetime.datetime]):
        report_packs_to_run (Union[Unset, List[int]]):
        submit_to_pension_sync_preference (Union[Unset, FinalisePayRunOptionsNullablePayRunFinaliseActionPreference]):
        submit_to_pension_sync_date_time (Union[Unset, datetime.datetime]):
        save_changes_to_default_settings (Union[Unset, bool]):
        from_pay_run_automation (Union[Unset, bool]):
    """

    pay_run_id: Union[Unset, int] = UNSET
    date_paid: Union[Unset, datetime.datetime] = UNSET
    export_journals: Union[Unset, bool] = UNSET
    publish_pay_slips: Union[Unset, FinalisePayRunOptionsPublishPaySlipsPreference] = UNSET
    publish_pay_slips_date_time: Union[Unset, datetime.datetime] = UNSET
    suppress_notifications: Union[Unset, bool] = UNSET
    lodge_pay_run: Union[Unset, bool] = UNSET
    lodge_pay_run_in_test_mode: Union[Unset, bool] = UNSET
    submit_to_pension_sync: Union[Unset, bool] = UNSET
    lodge_final_pay_run: Union[Unset, bool] = UNSET
    relodge_hmrc_late_submission_reason: Union[Unset, FinalisePayRunOptionsNullableHmrcFpsLateSubmissionReason] = UNSET
    relodge_selected_employees_only: Union[Unset, bool] = UNSET
    finalise_as_admin: Union[Unset, bool] = UNSET
    publish_pay_slips_preference: Union[Unset, FinalisePayRunOptionsNullablePayRunFinaliseActionPreference] = UNSET
    export_journals_preference: Union[Unset, FinalisePayRunOptionsNullablePayRunFinaliseActionPreference] = UNSET
    export_journals_date_time: Union[Unset, datetime.datetime] = UNSET
    lodge_pay_run_preference: Union[Unset, FinalisePayRunOptionsNullablePayRunFinaliseActionPreference] = UNSET
    super_payment_preference: Union[Unset, bool] = UNSET
    lodge_pay_run_date_time: Union[Unset, datetime.datetime] = UNSET
    run_report_packs_preference: Union[Unset, FinalisePayRunOptionsNullablePayRunFinaliseActionPreference] = UNSET
    run_report_packs_date_time: Union[Unset, datetime.datetime] = UNSET
    report_packs_to_run: Union[Unset, List[int]] = UNSET
    submit_to_pension_sync_preference: Union[Unset, FinalisePayRunOptionsNullablePayRunFinaliseActionPreference] = UNSET
    submit_to_pension_sync_date_time: Union[Unset, datetime.datetime] = UNSET
    save_changes_to_default_settings: Union[Unset, bool] = UNSET
    from_pay_run_automation: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        pay_run_id = self.pay_run_id

        date_paid: Union[Unset, str] = UNSET
        if not isinstance(self.date_paid, Unset):
            date_paid = self.date_paid.isoformat()

        export_journals = self.export_journals

        publish_pay_slips: Union[Unset, str] = UNSET
        if not isinstance(self.publish_pay_slips, Unset):
            publish_pay_slips = self.publish_pay_slips.value

        publish_pay_slips_date_time: Union[Unset, str] = UNSET
        if not isinstance(self.publish_pay_slips_date_time, Unset):
            publish_pay_slips_date_time = self.publish_pay_slips_date_time.isoformat()

        suppress_notifications = self.suppress_notifications

        lodge_pay_run = self.lodge_pay_run

        lodge_pay_run_in_test_mode = self.lodge_pay_run_in_test_mode

        submit_to_pension_sync = self.submit_to_pension_sync

        lodge_final_pay_run = self.lodge_final_pay_run

        relodge_hmrc_late_submission_reason: Union[Unset, str] = UNSET
        if not isinstance(self.relodge_hmrc_late_submission_reason, Unset):
            relodge_hmrc_late_submission_reason = self.relodge_hmrc_late_submission_reason.value

        relodge_selected_employees_only = self.relodge_selected_employees_only

        finalise_as_admin = self.finalise_as_admin

        publish_pay_slips_preference: Union[Unset, str] = UNSET
        if not isinstance(self.publish_pay_slips_preference, Unset):
            publish_pay_slips_preference = self.publish_pay_slips_preference.value

        export_journals_preference: Union[Unset, str] = UNSET
        if not isinstance(self.export_journals_preference, Unset):
            export_journals_preference = self.export_journals_preference.value

        export_journals_date_time: Union[Unset, str] = UNSET
        if not isinstance(self.export_journals_date_time, Unset):
            export_journals_date_time = self.export_journals_date_time.isoformat()

        lodge_pay_run_preference: Union[Unset, str] = UNSET
        if not isinstance(self.lodge_pay_run_preference, Unset):
            lodge_pay_run_preference = self.lodge_pay_run_preference.value

        super_payment_preference = self.super_payment_preference

        lodge_pay_run_date_time: Union[Unset, str] = UNSET
        if not isinstance(self.lodge_pay_run_date_time, Unset):
            lodge_pay_run_date_time = self.lodge_pay_run_date_time.isoformat()

        run_report_packs_preference: Union[Unset, str] = UNSET
        if not isinstance(self.run_report_packs_preference, Unset):
            run_report_packs_preference = self.run_report_packs_preference.value

        run_report_packs_date_time: Union[Unset, str] = UNSET
        if not isinstance(self.run_report_packs_date_time, Unset):
            run_report_packs_date_time = self.run_report_packs_date_time.isoformat()

        report_packs_to_run: Union[Unset, List[int]] = UNSET
        if not isinstance(self.report_packs_to_run, Unset):
            report_packs_to_run = self.report_packs_to_run

        submit_to_pension_sync_preference: Union[Unset, str] = UNSET
        if not isinstance(self.submit_to_pension_sync_preference, Unset):
            submit_to_pension_sync_preference = self.submit_to_pension_sync_preference.value

        submit_to_pension_sync_date_time: Union[Unset, str] = UNSET
        if not isinstance(self.submit_to_pension_sync_date_time, Unset):
            submit_to_pension_sync_date_time = self.submit_to_pension_sync_date_time.isoformat()

        save_changes_to_default_settings = self.save_changes_to_default_settings

        from_pay_run_automation = self.from_pay_run_automation

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if pay_run_id is not UNSET:
            field_dict["payRunId"] = pay_run_id
        if date_paid is not UNSET:
            field_dict["datePaid"] = date_paid
        if export_journals is not UNSET:
            field_dict["exportJournals"] = export_journals
        if publish_pay_slips is not UNSET:
            field_dict["publishPaySlips"] = publish_pay_slips
        if publish_pay_slips_date_time is not UNSET:
            field_dict["publishPaySlipsDateTime"] = publish_pay_slips_date_time
        if suppress_notifications is not UNSET:
            field_dict["suppressNotifications"] = suppress_notifications
        if lodge_pay_run is not UNSET:
            field_dict["lodgePayRun"] = lodge_pay_run
        if lodge_pay_run_in_test_mode is not UNSET:
            field_dict["lodgePayRunInTestMode"] = lodge_pay_run_in_test_mode
        if submit_to_pension_sync is not UNSET:
            field_dict["submitToPensionSync"] = submit_to_pension_sync
        if lodge_final_pay_run is not UNSET:
            field_dict["lodgeFinalPayRun"] = lodge_final_pay_run
        if relodge_hmrc_late_submission_reason is not UNSET:
            field_dict["relodgeHmrcLateSubmissionReason"] = relodge_hmrc_late_submission_reason
        if relodge_selected_employees_only is not UNSET:
            field_dict["relodgeSelectedEmployeesOnly"] = relodge_selected_employees_only
        if finalise_as_admin is not UNSET:
            field_dict["finaliseAsAdmin"] = finalise_as_admin
        if publish_pay_slips_preference is not UNSET:
            field_dict["publishPaySlipsPreference"] = publish_pay_slips_preference
        if export_journals_preference is not UNSET:
            field_dict["exportJournalsPreference"] = export_journals_preference
        if export_journals_date_time is not UNSET:
            field_dict["exportJournalsDateTime"] = export_journals_date_time
        if lodge_pay_run_preference is not UNSET:
            field_dict["lodgePayRunPreference"] = lodge_pay_run_preference
        if super_payment_preference is not UNSET:
            field_dict["superPaymentPreference"] = super_payment_preference
        if lodge_pay_run_date_time is not UNSET:
            field_dict["lodgePayRunDateTime"] = lodge_pay_run_date_time
        if run_report_packs_preference is not UNSET:
            field_dict["runReportPacksPreference"] = run_report_packs_preference
        if run_report_packs_date_time is not UNSET:
            field_dict["runReportPacksDateTime"] = run_report_packs_date_time
        if report_packs_to_run is not UNSET:
            field_dict["reportPacksToRun"] = report_packs_to_run
        if submit_to_pension_sync_preference is not UNSET:
            field_dict["submitToPensionSyncPreference"] = submit_to_pension_sync_preference
        if submit_to_pension_sync_date_time is not UNSET:
            field_dict["submitToPensionSyncDateTime"] = submit_to_pension_sync_date_time
        if save_changes_to_default_settings is not UNSET:
            field_dict["saveChangesToDefaultSettings"] = save_changes_to_default_settings
        if from_pay_run_automation is not UNSET:
            field_dict["fromPayRunAutomation"] = from_pay_run_automation

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        pay_run_id = d.pop("payRunId", UNSET)

        _date_paid = d.pop("datePaid", UNSET)
        date_paid: Union[Unset, datetime.datetime]
        if isinstance(_date_paid, Unset):
            date_paid = UNSET
        else:
            date_paid = isoparse(_date_paid)

        export_journals = d.pop("exportJournals", UNSET)

        _publish_pay_slips = d.pop("publishPaySlips", UNSET)
        publish_pay_slips: Union[Unset, FinalisePayRunOptionsPublishPaySlipsPreference]
        if isinstance(_publish_pay_slips, Unset):
            publish_pay_slips = UNSET
        else:
            publish_pay_slips = FinalisePayRunOptionsPublishPaySlipsPreference(_publish_pay_slips)

        _publish_pay_slips_date_time = d.pop("publishPaySlipsDateTime", UNSET)
        publish_pay_slips_date_time: Union[Unset, datetime.datetime]
        if isinstance(_publish_pay_slips_date_time, Unset):
            publish_pay_slips_date_time = UNSET
        else:
            publish_pay_slips_date_time = isoparse(_publish_pay_slips_date_time)

        suppress_notifications = d.pop("suppressNotifications", UNSET)

        lodge_pay_run = d.pop("lodgePayRun", UNSET)

        lodge_pay_run_in_test_mode = d.pop("lodgePayRunInTestMode", UNSET)

        submit_to_pension_sync = d.pop("submitToPensionSync", UNSET)

        lodge_final_pay_run = d.pop("lodgeFinalPayRun", UNSET)

        _relodge_hmrc_late_submission_reason = d.pop("relodgeHmrcLateSubmissionReason", UNSET)
        relodge_hmrc_late_submission_reason: Union[Unset, FinalisePayRunOptionsNullableHmrcFpsLateSubmissionReason]
        if isinstance(_relodge_hmrc_late_submission_reason, Unset):
            relodge_hmrc_late_submission_reason = UNSET
        else:
            relodge_hmrc_late_submission_reason = FinalisePayRunOptionsNullableHmrcFpsLateSubmissionReason(
                _relodge_hmrc_late_submission_reason
            )

        relodge_selected_employees_only = d.pop("relodgeSelectedEmployeesOnly", UNSET)

        finalise_as_admin = d.pop("finaliseAsAdmin", UNSET)

        _publish_pay_slips_preference = d.pop("publishPaySlipsPreference", UNSET)
        publish_pay_slips_preference: Union[Unset, FinalisePayRunOptionsNullablePayRunFinaliseActionPreference]
        if isinstance(_publish_pay_slips_preference, Unset):
            publish_pay_slips_preference = UNSET
        else:
            publish_pay_slips_preference = FinalisePayRunOptionsNullablePayRunFinaliseActionPreference(
                _publish_pay_slips_preference
            )

        _export_journals_preference = d.pop("exportJournalsPreference", UNSET)
        export_journals_preference: Union[Unset, FinalisePayRunOptionsNullablePayRunFinaliseActionPreference]
        if isinstance(_export_journals_preference, Unset):
            export_journals_preference = UNSET
        else:
            export_journals_preference = FinalisePayRunOptionsNullablePayRunFinaliseActionPreference(
                _export_journals_preference
            )

        _export_journals_date_time = d.pop("exportJournalsDateTime", UNSET)
        export_journals_date_time: Union[Unset, datetime.datetime]
        if isinstance(_export_journals_date_time, Unset):
            export_journals_date_time = UNSET
        else:
            export_journals_date_time = isoparse(_export_journals_date_time)

        _lodge_pay_run_preference = d.pop("lodgePayRunPreference", UNSET)
        lodge_pay_run_preference: Union[Unset, FinalisePayRunOptionsNullablePayRunFinaliseActionPreference]
        if isinstance(_lodge_pay_run_preference, Unset):
            lodge_pay_run_preference = UNSET
        else:
            lodge_pay_run_preference = FinalisePayRunOptionsNullablePayRunFinaliseActionPreference(
                _lodge_pay_run_preference
            )

        super_payment_preference = d.pop("superPaymentPreference", UNSET)

        _lodge_pay_run_date_time = d.pop("lodgePayRunDateTime", UNSET)
        lodge_pay_run_date_time: Union[Unset, datetime.datetime]
        if isinstance(_lodge_pay_run_date_time, Unset):
            lodge_pay_run_date_time = UNSET
        else:
            lodge_pay_run_date_time = isoparse(_lodge_pay_run_date_time)

        _run_report_packs_preference = d.pop("runReportPacksPreference", UNSET)
        run_report_packs_preference: Union[Unset, FinalisePayRunOptionsNullablePayRunFinaliseActionPreference]
        if isinstance(_run_report_packs_preference, Unset):
            run_report_packs_preference = UNSET
        else:
            run_report_packs_preference = FinalisePayRunOptionsNullablePayRunFinaliseActionPreference(
                _run_report_packs_preference
            )

        _run_report_packs_date_time = d.pop("runReportPacksDateTime", UNSET)
        run_report_packs_date_time: Union[Unset, datetime.datetime]
        if isinstance(_run_report_packs_date_time, Unset):
            run_report_packs_date_time = UNSET
        else:
            run_report_packs_date_time = isoparse(_run_report_packs_date_time)

        report_packs_to_run = cast(List[int], d.pop("reportPacksToRun", UNSET))

        _submit_to_pension_sync_preference = d.pop("submitToPensionSyncPreference", UNSET)
        submit_to_pension_sync_preference: Union[Unset, FinalisePayRunOptionsNullablePayRunFinaliseActionPreference]
        if isinstance(_submit_to_pension_sync_preference, Unset):
            submit_to_pension_sync_preference = UNSET
        else:
            submit_to_pension_sync_preference = FinalisePayRunOptionsNullablePayRunFinaliseActionPreference(
                _submit_to_pension_sync_preference
            )

        _submit_to_pension_sync_date_time = d.pop("submitToPensionSyncDateTime", UNSET)
        submit_to_pension_sync_date_time: Union[Unset, datetime.datetime]
        if isinstance(_submit_to_pension_sync_date_time, Unset):
            submit_to_pension_sync_date_time = UNSET
        else:
            submit_to_pension_sync_date_time = isoparse(_submit_to_pension_sync_date_time)

        save_changes_to_default_settings = d.pop("saveChangesToDefaultSettings", UNSET)

        from_pay_run_automation = d.pop("fromPayRunAutomation", UNSET)

        finalise_pay_run_options = cls(
            pay_run_id=pay_run_id,
            date_paid=date_paid,
            export_journals=export_journals,
            publish_pay_slips=publish_pay_slips,
            publish_pay_slips_date_time=publish_pay_slips_date_time,
            suppress_notifications=suppress_notifications,
            lodge_pay_run=lodge_pay_run,
            lodge_pay_run_in_test_mode=lodge_pay_run_in_test_mode,
            submit_to_pension_sync=submit_to_pension_sync,
            lodge_final_pay_run=lodge_final_pay_run,
            relodge_hmrc_late_submission_reason=relodge_hmrc_late_submission_reason,
            relodge_selected_employees_only=relodge_selected_employees_only,
            finalise_as_admin=finalise_as_admin,
            publish_pay_slips_preference=publish_pay_slips_preference,
            export_journals_preference=export_journals_preference,
            export_journals_date_time=export_journals_date_time,
            lodge_pay_run_preference=lodge_pay_run_preference,
            super_payment_preference=super_payment_preference,
            lodge_pay_run_date_time=lodge_pay_run_date_time,
            run_report_packs_preference=run_report_packs_preference,
            run_report_packs_date_time=run_report_packs_date_time,
            report_packs_to_run=report_packs_to_run,
            submit_to_pension_sync_preference=submit_to_pension_sync_preference,
            submit_to_pension_sync_date_time=submit_to_pension_sync_date_time,
            save_changes_to_default_settings=save_changes_to_default_settings,
            from_pay_run_automation=from_pay_run_automation,
        )

        finalise_pay_run_options.additional_properties = d
        return finalise_pay_run_options

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
