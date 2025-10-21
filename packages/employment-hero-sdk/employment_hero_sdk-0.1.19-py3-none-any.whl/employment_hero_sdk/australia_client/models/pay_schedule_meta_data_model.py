from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.pay_run_warning_model import PayRunWarningModel
    from ..models.report_pack_model import ReportPackModel


T = TypeVar("T", bound="PayScheduleMetaDataModel")


@_attrs_define
class PayScheduleMetaDataModel:
    """
    Attributes:
        pay_run_warnings (Union[Unset, List['PayRunWarningModel']]):
        frequencies (Union[Unset, List[str]]):
        employment_selection_strategies (Union[Unset, List[str]]):
        timesheet_import_options (Union[Unset, List[str]]):
        publish_pay_slips_preferences (Union[Unset, List[str]]):
        report_packs (Union[Unset, List['ReportPackModel']]):
        users_to_notify (Union[Unset, List[str]]):
    """

    pay_run_warnings: Union[Unset, List["PayRunWarningModel"]] = UNSET
    frequencies: Union[Unset, List[str]] = UNSET
    employment_selection_strategies: Union[Unset, List[str]] = UNSET
    timesheet_import_options: Union[Unset, List[str]] = UNSET
    publish_pay_slips_preferences: Union[Unset, List[str]] = UNSET
    report_packs: Union[Unset, List["ReportPackModel"]] = UNSET
    users_to_notify: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        pay_run_warnings: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.pay_run_warnings, Unset):
            pay_run_warnings = []
            for pay_run_warnings_item_data in self.pay_run_warnings:
                pay_run_warnings_item = pay_run_warnings_item_data.to_dict()
                pay_run_warnings.append(pay_run_warnings_item)

        frequencies: Union[Unset, List[str]] = UNSET
        if not isinstance(self.frequencies, Unset):
            frequencies = self.frequencies

        employment_selection_strategies: Union[Unset, List[str]] = UNSET
        if not isinstance(self.employment_selection_strategies, Unset):
            employment_selection_strategies = self.employment_selection_strategies

        timesheet_import_options: Union[Unset, List[str]] = UNSET
        if not isinstance(self.timesheet_import_options, Unset):
            timesheet_import_options = self.timesheet_import_options

        publish_pay_slips_preferences: Union[Unset, List[str]] = UNSET
        if not isinstance(self.publish_pay_slips_preferences, Unset):
            publish_pay_slips_preferences = self.publish_pay_slips_preferences

        report_packs: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.report_packs, Unset):
            report_packs = []
            for report_packs_item_data in self.report_packs:
                report_packs_item = report_packs_item_data.to_dict()
                report_packs.append(report_packs_item)

        users_to_notify: Union[Unset, List[str]] = UNSET
        if not isinstance(self.users_to_notify, Unset):
            users_to_notify = self.users_to_notify

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if pay_run_warnings is not UNSET:
            field_dict["payRunWarnings"] = pay_run_warnings
        if frequencies is not UNSET:
            field_dict["frequencies"] = frequencies
        if employment_selection_strategies is not UNSET:
            field_dict["employmentSelectionStrategies"] = employment_selection_strategies
        if timesheet_import_options is not UNSET:
            field_dict["timesheetImportOptions"] = timesheet_import_options
        if publish_pay_slips_preferences is not UNSET:
            field_dict["publishPaySlipsPreferences"] = publish_pay_slips_preferences
        if report_packs is not UNSET:
            field_dict["reportPacks"] = report_packs
        if users_to_notify is not UNSET:
            field_dict["usersToNotify"] = users_to_notify

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.pay_run_warning_model import PayRunWarningModel
        from ..models.report_pack_model import ReportPackModel

        d = src_dict.copy()
        pay_run_warnings = []
        _pay_run_warnings = d.pop("payRunWarnings", UNSET)
        for pay_run_warnings_item_data in _pay_run_warnings or []:
            pay_run_warnings_item = PayRunWarningModel.from_dict(pay_run_warnings_item_data)

            pay_run_warnings.append(pay_run_warnings_item)

        frequencies = cast(List[str], d.pop("frequencies", UNSET))

        employment_selection_strategies = cast(List[str], d.pop("employmentSelectionStrategies", UNSET))

        timesheet_import_options = cast(List[str], d.pop("timesheetImportOptions", UNSET))

        publish_pay_slips_preferences = cast(List[str], d.pop("publishPaySlipsPreferences", UNSET))

        report_packs = []
        _report_packs = d.pop("reportPacks", UNSET)
        for report_packs_item_data in _report_packs or []:
            report_packs_item = ReportPackModel.from_dict(report_packs_item_data)

            report_packs.append(report_packs_item)

        users_to_notify = cast(List[str], d.pop("usersToNotify", UNSET))

        pay_schedule_meta_data_model = cls(
            pay_run_warnings=pay_run_warnings,
            frequencies=frequencies,
            employment_selection_strategies=employment_selection_strategies,
            timesheet_import_options=timesheet_import_options,
            publish_pay_slips_preferences=publish_pay_slips_preferences,
            report_packs=report_packs,
            users_to_notify=users_to_notify,
        )

        pay_schedule_meta_data_model.additional_properties = d
        return pay_schedule_meta_data_model

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
