from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.pay_run_finalise_default_settings_model_pay_run_finalise_action_preference import (
    PayRunFinaliseDefaultSettingsModelPayRunFinaliseActionPreference,
)
from ..models.pay_run_finalise_default_settings_model_pay_run_finalise_action_timeline import (
    PayRunFinaliseDefaultSettingsModelPayRunFinaliseActionTimeline,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="PayRunFinaliseDefaultSettingsModel")


@_attrs_define
class PayRunFinaliseDefaultSettingsModel:
    """
    Attributes:
        export_journals (Union[Unset, PayRunFinaliseDefaultSettingsModelPayRunFinaliseActionPreference]):
        export_journals_timeline (Union[Unset, PayRunFinaliseDefaultSettingsModelPayRunFinaliseActionTimeline]):
        export_journals_day (Union[Unset, int]):
        export_journals_time_of_day (Union[Unset, str]):
        lodge_pay_run (Union[Unset, PayRunFinaliseDefaultSettingsModelPayRunFinaliseActionPreference]):
        lodge_pay_run_day (Union[Unset, int]):
        lodge_pay_run_timeline (Union[Unset, PayRunFinaliseDefaultSettingsModelPayRunFinaliseActionTimeline]):
        lodge_pay_run_time_of_day (Union[Unset, str]):
        publish_pay_slips_day (Union[Unset, int]):
        publish_pay_slips_timeline (Union[Unset, PayRunFinaliseDefaultSettingsModelPayRunFinaliseActionTimeline]):
        publish_pay_slips (Union[Unset, PayRunFinaliseDefaultSettingsModelPayRunFinaliseActionPreference]):
        publish_pay_slips_time_of_day (Union[Unset, str]):
        suppress_notifications (Union[Unset, bool]):
        submit_to_pension_sync (Union[Unset, PayRunFinaliseDefaultSettingsModelPayRunFinaliseActionPreference]):
        submit_to_pension_sync_timeline (Union[Unset, PayRunFinaliseDefaultSettingsModelPayRunFinaliseActionTimeline]):
        submit_to_pension_sync_day (Union[Unset, int]):
        submit_to_pension_sync_time_of_day (Union[Unset, str]):
        run_report_packs (Union[Unset, PayRunFinaliseDefaultSettingsModelPayRunFinaliseActionPreference]):
        run_report_packs_timeline (Union[Unset, PayRunFinaliseDefaultSettingsModelPayRunFinaliseActionTimeline]):
        run_report_packs_day (Union[Unset, int]):
        run_report_packs_time_of_day (Union[Unset, str]):
        report_packs_to_run (Union[Unset, List[int]]):
        super_payment (Union[Unset, bool]):
    """

    export_journals: Union[Unset, PayRunFinaliseDefaultSettingsModelPayRunFinaliseActionPreference] = UNSET
    export_journals_timeline: Union[Unset, PayRunFinaliseDefaultSettingsModelPayRunFinaliseActionTimeline] = UNSET
    export_journals_day: Union[Unset, int] = UNSET
    export_journals_time_of_day: Union[Unset, str] = UNSET
    lodge_pay_run: Union[Unset, PayRunFinaliseDefaultSettingsModelPayRunFinaliseActionPreference] = UNSET
    lodge_pay_run_day: Union[Unset, int] = UNSET
    lodge_pay_run_timeline: Union[Unset, PayRunFinaliseDefaultSettingsModelPayRunFinaliseActionTimeline] = UNSET
    lodge_pay_run_time_of_day: Union[Unset, str] = UNSET
    publish_pay_slips_day: Union[Unset, int] = UNSET
    publish_pay_slips_timeline: Union[Unset, PayRunFinaliseDefaultSettingsModelPayRunFinaliseActionTimeline] = UNSET
    publish_pay_slips: Union[Unset, PayRunFinaliseDefaultSettingsModelPayRunFinaliseActionPreference] = UNSET
    publish_pay_slips_time_of_day: Union[Unset, str] = UNSET
    suppress_notifications: Union[Unset, bool] = UNSET
    submit_to_pension_sync: Union[Unset, PayRunFinaliseDefaultSettingsModelPayRunFinaliseActionPreference] = UNSET
    submit_to_pension_sync_timeline: Union[Unset, PayRunFinaliseDefaultSettingsModelPayRunFinaliseActionTimeline] = (
        UNSET
    )
    submit_to_pension_sync_day: Union[Unset, int] = UNSET
    submit_to_pension_sync_time_of_day: Union[Unset, str] = UNSET
    run_report_packs: Union[Unset, PayRunFinaliseDefaultSettingsModelPayRunFinaliseActionPreference] = UNSET
    run_report_packs_timeline: Union[Unset, PayRunFinaliseDefaultSettingsModelPayRunFinaliseActionTimeline] = UNSET
    run_report_packs_day: Union[Unset, int] = UNSET
    run_report_packs_time_of_day: Union[Unset, str] = UNSET
    report_packs_to_run: Union[Unset, List[int]] = UNSET
    super_payment: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        export_journals: Union[Unset, str] = UNSET
        if not isinstance(self.export_journals, Unset):
            export_journals = self.export_journals.value

        export_journals_timeline: Union[Unset, str] = UNSET
        if not isinstance(self.export_journals_timeline, Unset):
            export_journals_timeline = self.export_journals_timeline.value

        export_journals_day = self.export_journals_day

        export_journals_time_of_day = self.export_journals_time_of_day

        lodge_pay_run: Union[Unset, str] = UNSET
        if not isinstance(self.lodge_pay_run, Unset):
            lodge_pay_run = self.lodge_pay_run.value

        lodge_pay_run_day = self.lodge_pay_run_day

        lodge_pay_run_timeline: Union[Unset, str] = UNSET
        if not isinstance(self.lodge_pay_run_timeline, Unset):
            lodge_pay_run_timeline = self.lodge_pay_run_timeline.value

        lodge_pay_run_time_of_day = self.lodge_pay_run_time_of_day

        publish_pay_slips_day = self.publish_pay_slips_day

        publish_pay_slips_timeline: Union[Unset, str] = UNSET
        if not isinstance(self.publish_pay_slips_timeline, Unset):
            publish_pay_slips_timeline = self.publish_pay_slips_timeline.value

        publish_pay_slips: Union[Unset, str] = UNSET
        if not isinstance(self.publish_pay_slips, Unset):
            publish_pay_slips = self.publish_pay_slips.value

        publish_pay_slips_time_of_day = self.publish_pay_slips_time_of_day

        suppress_notifications = self.suppress_notifications

        submit_to_pension_sync: Union[Unset, str] = UNSET
        if not isinstance(self.submit_to_pension_sync, Unset):
            submit_to_pension_sync = self.submit_to_pension_sync.value

        submit_to_pension_sync_timeline: Union[Unset, str] = UNSET
        if not isinstance(self.submit_to_pension_sync_timeline, Unset):
            submit_to_pension_sync_timeline = self.submit_to_pension_sync_timeline.value

        submit_to_pension_sync_day = self.submit_to_pension_sync_day

        submit_to_pension_sync_time_of_day = self.submit_to_pension_sync_time_of_day

        run_report_packs: Union[Unset, str] = UNSET
        if not isinstance(self.run_report_packs, Unset):
            run_report_packs = self.run_report_packs.value

        run_report_packs_timeline: Union[Unset, str] = UNSET
        if not isinstance(self.run_report_packs_timeline, Unset):
            run_report_packs_timeline = self.run_report_packs_timeline.value

        run_report_packs_day = self.run_report_packs_day

        run_report_packs_time_of_day = self.run_report_packs_time_of_day

        report_packs_to_run: Union[Unset, List[int]] = UNSET
        if not isinstance(self.report_packs_to_run, Unset):
            report_packs_to_run = self.report_packs_to_run

        super_payment = self.super_payment

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if export_journals is not UNSET:
            field_dict["exportJournals"] = export_journals
        if export_journals_timeline is not UNSET:
            field_dict["exportJournalsTimeline"] = export_journals_timeline
        if export_journals_day is not UNSET:
            field_dict["exportJournalsDay"] = export_journals_day
        if export_journals_time_of_day is not UNSET:
            field_dict["exportJournalsTimeOfDay"] = export_journals_time_of_day
        if lodge_pay_run is not UNSET:
            field_dict["lodgePayRun"] = lodge_pay_run
        if lodge_pay_run_day is not UNSET:
            field_dict["lodgePayRunDay"] = lodge_pay_run_day
        if lodge_pay_run_timeline is not UNSET:
            field_dict["lodgePayRunTimeline"] = lodge_pay_run_timeline
        if lodge_pay_run_time_of_day is not UNSET:
            field_dict["lodgePayRunTimeOfDay"] = lodge_pay_run_time_of_day
        if publish_pay_slips_day is not UNSET:
            field_dict["publishPaySlipsDay"] = publish_pay_slips_day
        if publish_pay_slips_timeline is not UNSET:
            field_dict["publishPaySlipsTimeline"] = publish_pay_slips_timeline
        if publish_pay_slips is not UNSET:
            field_dict["publishPaySlips"] = publish_pay_slips
        if publish_pay_slips_time_of_day is not UNSET:
            field_dict["publishPaySlipsTimeOfDay"] = publish_pay_slips_time_of_day
        if suppress_notifications is not UNSET:
            field_dict["suppressNotifications"] = suppress_notifications
        if submit_to_pension_sync is not UNSET:
            field_dict["submitToPensionSync"] = submit_to_pension_sync
        if submit_to_pension_sync_timeline is not UNSET:
            field_dict["submitToPensionSyncTimeline"] = submit_to_pension_sync_timeline
        if submit_to_pension_sync_day is not UNSET:
            field_dict["submitToPensionSyncDay"] = submit_to_pension_sync_day
        if submit_to_pension_sync_time_of_day is not UNSET:
            field_dict["submitToPensionSyncTimeOfDay"] = submit_to_pension_sync_time_of_day
        if run_report_packs is not UNSET:
            field_dict["runReportPacks"] = run_report_packs
        if run_report_packs_timeline is not UNSET:
            field_dict["runReportPacksTimeline"] = run_report_packs_timeline
        if run_report_packs_day is not UNSET:
            field_dict["runReportPacksDay"] = run_report_packs_day
        if run_report_packs_time_of_day is not UNSET:
            field_dict["runReportPacksTimeOfDay"] = run_report_packs_time_of_day
        if report_packs_to_run is not UNSET:
            field_dict["reportPacksToRun"] = report_packs_to_run
        if super_payment is not UNSET:
            field_dict["superPayment"] = super_payment

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _export_journals = d.pop("exportJournals", UNSET)
        export_journals: Union[Unset, PayRunFinaliseDefaultSettingsModelPayRunFinaliseActionPreference]
        if isinstance(_export_journals, Unset):
            export_journals = UNSET
        else:
            export_journals = PayRunFinaliseDefaultSettingsModelPayRunFinaliseActionPreference(_export_journals)

        _export_journals_timeline = d.pop("exportJournalsTimeline", UNSET)
        export_journals_timeline: Union[Unset, PayRunFinaliseDefaultSettingsModelPayRunFinaliseActionTimeline]
        if isinstance(_export_journals_timeline, Unset):
            export_journals_timeline = UNSET
        else:
            export_journals_timeline = PayRunFinaliseDefaultSettingsModelPayRunFinaliseActionTimeline(
                _export_journals_timeline
            )

        export_journals_day = d.pop("exportJournalsDay", UNSET)

        export_journals_time_of_day = d.pop("exportJournalsTimeOfDay", UNSET)

        _lodge_pay_run = d.pop("lodgePayRun", UNSET)
        lodge_pay_run: Union[Unset, PayRunFinaliseDefaultSettingsModelPayRunFinaliseActionPreference]
        if isinstance(_lodge_pay_run, Unset):
            lodge_pay_run = UNSET
        else:
            lodge_pay_run = PayRunFinaliseDefaultSettingsModelPayRunFinaliseActionPreference(_lodge_pay_run)

        lodge_pay_run_day = d.pop("lodgePayRunDay", UNSET)

        _lodge_pay_run_timeline = d.pop("lodgePayRunTimeline", UNSET)
        lodge_pay_run_timeline: Union[Unset, PayRunFinaliseDefaultSettingsModelPayRunFinaliseActionTimeline]
        if isinstance(_lodge_pay_run_timeline, Unset):
            lodge_pay_run_timeline = UNSET
        else:
            lodge_pay_run_timeline = PayRunFinaliseDefaultSettingsModelPayRunFinaliseActionTimeline(
                _lodge_pay_run_timeline
            )

        lodge_pay_run_time_of_day = d.pop("lodgePayRunTimeOfDay", UNSET)

        publish_pay_slips_day = d.pop("publishPaySlipsDay", UNSET)

        _publish_pay_slips_timeline = d.pop("publishPaySlipsTimeline", UNSET)
        publish_pay_slips_timeline: Union[Unset, PayRunFinaliseDefaultSettingsModelPayRunFinaliseActionTimeline]
        if isinstance(_publish_pay_slips_timeline, Unset):
            publish_pay_slips_timeline = UNSET
        else:
            publish_pay_slips_timeline = PayRunFinaliseDefaultSettingsModelPayRunFinaliseActionTimeline(
                _publish_pay_slips_timeline
            )

        _publish_pay_slips = d.pop("publishPaySlips", UNSET)
        publish_pay_slips: Union[Unset, PayRunFinaliseDefaultSettingsModelPayRunFinaliseActionPreference]
        if isinstance(_publish_pay_slips, Unset):
            publish_pay_slips = UNSET
        else:
            publish_pay_slips = PayRunFinaliseDefaultSettingsModelPayRunFinaliseActionPreference(_publish_pay_slips)

        publish_pay_slips_time_of_day = d.pop("publishPaySlipsTimeOfDay", UNSET)

        suppress_notifications = d.pop("suppressNotifications", UNSET)

        _submit_to_pension_sync = d.pop("submitToPensionSync", UNSET)
        submit_to_pension_sync: Union[Unset, PayRunFinaliseDefaultSettingsModelPayRunFinaliseActionPreference]
        if isinstance(_submit_to_pension_sync, Unset):
            submit_to_pension_sync = UNSET
        else:
            submit_to_pension_sync = PayRunFinaliseDefaultSettingsModelPayRunFinaliseActionPreference(
                _submit_to_pension_sync
            )

        _submit_to_pension_sync_timeline = d.pop("submitToPensionSyncTimeline", UNSET)
        submit_to_pension_sync_timeline: Union[Unset, PayRunFinaliseDefaultSettingsModelPayRunFinaliseActionTimeline]
        if isinstance(_submit_to_pension_sync_timeline, Unset):
            submit_to_pension_sync_timeline = UNSET
        else:
            submit_to_pension_sync_timeline = PayRunFinaliseDefaultSettingsModelPayRunFinaliseActionTimeline(
                _submit_to_pension_sync_timeline
            )

        submit_to_pension_sync_day = d.pop("submitToPensionSyncDay", UNSET)

        submit_to_pension_sync_time_of_day = d.pop("submitToPensionSyncTimeOfDay", UNSET)

        _run_report_packs = d.pop("runReportPacks", UNSET)
        run_report_packs: Union[Unset, PayRunFinaliseDefaultSettingsModelPayRunFinaliseActionPreference]
        if isinstance(_run_report_packs, Unset):
            run_report_packs = UNSET
        else:
            run_report_packs = PayRunFinaliseDefaultSettingsModelPayRunFinaliseActionPreference(_run_report_packs)

        _run_report_packs_timeline = d.pop("runReportPacksTimeline", UNSET)
        run_report_packs_timeline: Union[Unset, PayRunFinaliseDefaultSettingsModelPayRunFinaliseActionTimeline]
        if isinstance(_run_report_packs_timeline, Unset):
            run_report_packs_timeline = UNSET
        else:
            run_report_packs_timeline = PayRunFinaliseDefaultSettingsModelPayRunFinaliseActionTimeline(
                _run_report_packs_timeline
            )

        run_report_packs_day = d.pop("runReportPacksDay", UNSET)

        run_report_packs_time_of_day = d.pop("runReportPacksTimeOfDay", UNSET)

        report_packs_to_run = cast(List[int], d.pop("reportPacksToRun", UNSET))

        super_payment = d.pop("superPayment", UNSET)

        pay_run_finalise_default_settings_model = cls(
            export_journals=export_journals,
            export_journals_timeline=export_journals_timeline,
            export_journals_day=export_journals_day,
            export_journals_time_of_day=export_journals_time_of_day,
            lodge_pay_run=lodge_pay_run,
            lodge_pay_run_day=lodge_pay_run_day,
            lodge_pay_run_timeline=lodge_pay_run_timeline,
            lodge_pay_run_time_of_day=lodge_pay_run_time_of_day,
            publish_pay_slips_day=publish_pay_slips_day,
            publish_pay_slips_timeline=publish_pay_slips_timeline,
            publish_pay_slips=publish_pay_slips,
            publish_pay_slips_time_of_day=publish_pay_slips_time_of_day,
            suppress_notifications=suppress_notifications,
            submit_to_pension_sync=submit_to_pension_sync,
            submit_to_pension_sync_timeline=submit_to_pension_sync_timeline,
            submit_to_pension_sync_day=submit_to_pension_sync_day,
            submit_to_pension_sync_time_of_day=submit_to_pension_sync_time_of_day,
            run_report_packs=run_report_packs,
            run_report_packs_timeline=run_report_packs_timeline,
            run_report_packs_day=run_report_packs_day,
            run_report_packs_time_of_day=run_report_packs_time_of_day,
            report_packs_to_run=report_packs_to_run,
            super_payment=super_payment,
        )

        pay_run_finalise_default_settings_model.additional_properties = d
        return pay_run_finalise_default_settings_model

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
