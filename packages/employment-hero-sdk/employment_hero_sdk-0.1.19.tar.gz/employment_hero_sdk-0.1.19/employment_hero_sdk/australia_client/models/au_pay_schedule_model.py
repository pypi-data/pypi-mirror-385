import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.au_pay_schedule_model_au_pay_cycle_frequency_enum import AuPayScheduleModelAuPayCycleFrequencyEnum
from ..models.au_pay_schedule_model_nullable_pay_run_employee_selection_strategy import (
    AuPayScheduleModelNullablePayRunEmployeeSelectionStrategy,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.au_auto_pay_configuration_model import AuAutoPayConfigurationModel
    from ..models.pay_run_finalise_default_settings_model import PayRunFinaliseDefaultSettingsModel
    from ..models.pay_schedule_approval_settings_model import PayScheduleApprovalSettingsModel


T = TypeVar("T", bound="AuPayScheduleModel")


@_attrs_define
class AuPayScheduleModel:
    """
    Attributes:
        aba_details_id (Union[Unset, int]):
        payg_account_bsb (Union[Unset, str]):
        payg_account_number (Union[Unset, str]):
        payg_account_name (Union[Unset, str]):
        payg_reference (Union[Unset, str]):
        auto_pay_configuration (Union[Unset, AuAutoPayConfigurationModel]):
        frequency (Union[Unset, AuPayScheduleModelAuPayCycleFrequencyEnum]):
        pay_schedule_payment_approval_settings (Union[Unset, PayScheduleApprovalSettingsModel]):
        id (Union[Unset, int]):
        name (Union[Unset, str]):
        employee_selection_strategy (Union[Unset, AuPayScheduleModelNullablePayRunEmployeeSelectionStrategy]):
        last_date_paid (Union[Unset, datetime.datetime]):
        last_pay_run (Union[Unset, datetime.datetime]):
        external_id (Union[Unset, str]):
        source (Union[Unset, str]):
        locations (Union[Unset, List[int]]):
        equal_monthly_payments (Union[Unset, bool]):
        ignored_pay_run_warnings (Union[Unset, List[int]]):
        default_finalise_settings (Union[Unset, PayRunFinaliseDefaultSettingsModel]):
        pay_schedule_approval_settings (Union[Unset, PayScheduleApprovalSettingsModel]):
    """

    aba_details_id: Union[Unset, int] = UNSET
    payg_account_bsb: Union[Unset, str] = UNSET
    payg_account_number: Union[Unset, str] = UNSET
    payg_account_name: Union[Unset, str] = UNSET
    payg_reference: Union[Unset, str] = UNSET
    auto_pay_configuration: Union[Unset, "AuAutoPayConfigurationModel"] = UNSET
    frequency: Union[Unset, AuPayScheduleModelAuPayCycleFrequencyEnum] = UNSET
    pay_schedule_payment_approval_settings: Union[Unset, "PayScheduleApprovalSettingsModel"] = UNSET
    id: Union[Unset, int] = UNSET
    name: Union[Unset, str] = UNSET
    employee_selection_strategy: Union[Unset, AuPayScheduleModelNullablePayRunEmployeeSelectionStrategy] = UNSET
    last_date_paid: Union[Unset, datetime.datetime] = UNSET
    last_pay_run: Union[Unset, datetime.datetime] = UNSET
    external_id: Union[Unset, str] = UNSET
    source: Union[Unset, str] = UNSET
    locations: Union[Unset, List[int]] = UNSET
    equal_monthly_payments: Union[Unset, bool] = UNSET
    ignored_pay_run_warnings: Union[Unset, List[int]] = UNSET
    default_finalise_settings: Union[Unset, "PayRunFinaliseDefaultSettingsModel"] = UNSET
    pay_schedule_approval_settings: Union[Unset, "PayScheduleApprovalSettingsModel"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        aba_details_id = self.aba_details_id

        payg_account_bsb = self.payg_account_bsb

        payg_account_number = self.payg_account_number

        payg_account_name = self.payg_account_name

        payg_reference = self.payg_reference

        auto_pay_configuration: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.auto_pay_configuration, Unset):
            auto_pay_configuration = self.auto_pay_configuration.to_dict()

        frequency: Union[Unset, str] = UNSET
        if not isinstance(self.frequency, Unset):
            frequency = self.frequency.value

        pay_schedule_payment_approval_settings: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.pay_schedule_payment_approval_settings, Unset):
            pay_schedule_payment_approval_settings = self.pay_schedule_payment_approval_settings.to_dict()

        id = self.id

        name = self.name

        employee_selection_strategy: Union[Unset, str] = UNSET
        if not isinstance(self.employee_selection_strategy, Unset):
            employee_selection_strategy = self.employee_selection_strategy.value

        last_date_paid: Union[Unset, str] = UNSET
        if not isinstance(self.last_date_paid, Unset):
            last_date_paid = self.last_date_paid.isoformat()

        last_pay_run: Union[Unset, str] = UNSET
        if not isinstance(self.last_pay_run, Unset):
            last_pay_run = self.last_pay_run.isoformat()

        external_id = self.external_id

        source = self.source

        locations: Union[Unset, List[int]] = UNSET
        if not isinstance(self.locations, Unset):
            locations = self.locations

        equal_monthly_payments = self.equal_monthly_payments

        ignored_pay_run_warnings: Union[Unset, List[int]] = UNSET
        if not isinstance(self.ignored_pay_run_warnings, Unset):
            ignored_pay_run_warnings = self.ignored_pay_run_warnings

        default_finalise_settings: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.default_finalise_settings, Unset):
            default_finalise_settings = self.default_finalise_settings.to_dict()

        pay_schedule_approval_settings: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.pay_schedule_approval_settings, Unset):
            pay_schedule_approval_settings = self.pay_schedule_approval_settings.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if aba_details_id is not UNSET:
            field_dict["abaDetailsId"] = aba_details_id
        if payg_account_bsb is not UNSET:
            field_dict["paygAccountBsb"] = payg_account_bsb
        if payg_account_number is not UNSET:
            field_dict["paygAccountNumber"] = payg_account_number
        if payg_account_name is not UNSET:
            field_dict["paygAccountName"] = payg_account_name
        if payg_reference is not UNSET:
            field_dict["paygReference"] = payg_reference
        if auto_pay_configuration is not UNSET:
            field_dict["autoPayConfiguration"] = auto_pay_configuration
        if frequency is not UNSET:
            field_dict["frequency"] = frequency
        if pay_schedule_payment_approval_settings is not UNSET:
            field_dict["paySchedulePaymentApprovalSettings"] = pay_schedule_payment_approval_settings
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if employee_selection_strategy is not UNSET:
            field_dict["employeeSelectionStrategy"] = employee_selection_strategy
        if last_date_paid is not UNSET:
            field_dict["lastDatePaid"] = last_date_paid
        if last_pay_run is not UNSET:
            field_dict["lastPayRun"] = last_pay_run
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if source is not UNSET:
            field_dict["source"] = source
        if locations is not UNSET:
            field_dict["locations"] = locations
        if equal_monthly_payments is not UNSET:
            field_dict["equalMonthlyPayments"] = equal_monthly_payments
        if ignored_pay_run_warnings is not UNSET:
            field_dict["ignoredPayRunWarnings"] = ignored_pay_run_warnings
        if default_finalise_settings is not UNSET:
            field_dict["defaultFinaliseSettings"] = default_finalise_settings
        if pay_schedule_approval_settings is not UNSET:
            field_dict["payScheduleApprovalSettings"] = pay_schedule_approval_settings

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.au_auto_pay_configuration_model import AuAutoPayConfigurationModel
        from ..models.pay_run_finalise_default_settings_model import PayRunFinaliseDefaultSettingsModel
        from ..models.pay_schedule_approval_settings_model import PayScheduleApprovalSettingsModel

        d = src_dict.copy()
        aba_details_id = d.pop("abaDetailsId", UNSET)

        payg_account_bsb = d.pop("paygAccountBsb", UNSET)

        payg_account_number = d.pop("paygAccountNumber", UNSET)

        payg_account_name = d.pop("paygAccountName", UNSET)

        payg_reference = d.pop("paygReference", UNSET)

        _auto_pay_configuration = d.pop("autoPayConfiguration", UNSET)
        auto_pay_configuration: Union[Unset, AuAutoPayConfigurationModel]
        if isinstance(_auto_pay_configuration, Unset):
            auto_pay_configuration = UNSET
        else:
            auto_pay_configuration = AuAutoPayConfigurationModel.from_dict(_auto_pay_configuration)

        _frequency = d.pop("frequency", UNSET)
        frequency: Union[Unset, AuPayScheduleModelAuPayCycleFrequencyEnum]
        if isinstance(_frequency, Unset):
            frequency = UNSET
        else:
            frequency = AuPayScheduleModelAuPayCycleFrequencyEnum(_frequency)

        _pay_schedule_payment_approval_settings = d.pop("paySchedulePaymentApprovalSettings", UNSET)
        pay_schedule_payment_approval_settings: Union[Unset, PayScheduleApprovalSettingsModel]
        if isinstance(_pay_schedule_payment_approval_settings, Unset):
            pay_schedule_payment_approval_settings = UNSET
        else:
            pay_schedule_payment_approval_settings = PayScheduleApprovalSettingsModel.from_dict(
                _pay_schedule_payment_approval_settings
            )

        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        _employee_selection_strategy = d.pop("employeeSelectionStrategy", UNSET)
        employee_selection_strategy: Union[Unset, AuPayScheduleModelNullablePayRunEmployeeSelectionStrategy]
        if isinstance(_employee_selection_strategy, Unset):
            employee_selection_strategy = UNSET
        else:
            employee_selection_strategy = AuPayScheduleModelNullablePayRunEmployeeSelectionStrategy(
                _employee_selection_strategy
            )

        _last_date_paid = d.pop("lastDatePaid", UNSET)
        last_date_paid: Union[Unset, datetime.datetime]
        if isinstance(_last_date_paid, Unset):
            last_date_paid = UNSET
        else:
            last_date_paid = isoparse(_last_date_paid)

        _last_pay_run = d.pop("lastPayRun", UNSET)
        last_pay_run: Union[Unset, datetime.datetime]
        if isinstance(_last_pay_run, Unset):
            last_pay_run = UNSET
        else:
            last_pay_run = isoparse(_last_pay_run)

        external_id = d.pop("externalId", UNSET)

        source = d.pop("source", UNSET)

        locations = cast(List[int], d.pop("locations", UNSET))

        equal_monthly_payments = d.pop("equalMonthlyPayments", UNSET)

        ignored_pay_run_warnings = cast(List[int], d.pop("ignoredPayRunWarnings", UNSET))

        _default_finalise_settings = d.pop("defaultFinaliseSettings", UNSET)
        default_finalise_settings: Union[Unset, PayRunFinaliseDefaultSettingsModel]
        if isinstance(_default_finalise_settings, Unset):
            default_finalise_settings = UNSET
        else:
            default_finalise_settings = PayRunFinaliseDefaultSettingsModel.from_dict(_default_finalise_settings)

        _pay_schedule_approval_settings = d.pop("payScheduleApprovalSettings", UNSET)
        pay_schedule_approval_settings: Union[Unset, PayScheduleApprovalSettingsModel]
        if isinstance(_pay_schedule_approval_settings, Unset):
            pay_schedule_approval_settings = UNSET
        else:
            pay_schedule_approval_settings = PayScheduleApprovalSettingsModel.from_dict(_pay_schedule_approval_settings)

        au_pay_schedule_model = cls(
            aba_details_id=aba_details_id,
            payg_account_bsb=payg_account_bsb,
            payg_account_number=payg_account_number,
            payg_account_name=payg_account_name,
            payg_reference=payg_reference,
            auto_pay_configuration=auto_pay_configuration,
            frequency=frequency,
            pay_schedule_payment_approval_settings=pay_schedule_payment_approval_settings,
            id=id,
            name=name,
            employee_selection_strategy=employee_selection_strategy,
            last_date_paid=last_date_paid,
            last_pay_run=last_pay_run,
            external_id=external_id,
            source=source,
            locations=locations,
            equal_monthly_payments=equal_monthly_payments,
            ignored_pay_run_warnings=ignored_pay_run_warnings,
            default_finalise_settings=default_finalise_settings,
            pay_schedule_approval_settings=pay_schedule_approval_settings,
        )

        au_pay_schedule_model.additional_properties = d
        return au_pay_schedule_model

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
