import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.pay_run_create_request_nullable_timesheet_import_option import (
    PayRunCreateRequestNullableTimesheetImportOption,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="PayRunCreateRequest")


@_attrs_define
class PayRunCreateRequest:
    """
    Attributes:
        pay_schedule_id (Union[Unset, int]):
        pay_period_ending (Union[Unset, datetime.datetime]):
        date_paid (Union[Unset, datetime.datetime]):
        timesheet_import_option (Union[Unset, PayRunCreateRequestNullableTimesheetImportOption]):
        external_id (Union[Unset, str]):
        callback_url (Union[Unset, str]):
        create_with_empty_pays (Union[Unset, bool]):
        adhoc (Union[Unset, bool]):
    """

    pay_schedule_id: Union[Unset, int] = UNSET
    pay_period_ending: Union[Unset, datetime.datetime] = UNSET
    date_paid: Union[Unset, datetime.datetime] = UNSET
    timesheet_import_option: Union[Unset, PayRunCreateRequestNullableTimesheetImportOption] = UNSET
    external_id: Union[Unset, str] = UNSET
    callback_url: Union[Unset, str] = UNSET
    create_with_empty_pays: Union[Unset, bool] = UNSET
    adhoc: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        pay_schedule_id = self.pay_schedule_id

        pay_period_ending: Union[Unset, str] = UNSET
        if not isinstance(self.pay_period_ending, Unset):
            pay_period_ending = self.pay_period_ending.isoformat()

        date_paid: Union[Unset, str] = UNSET
        if not isinstance(self.date_paid, Unset):
            date_paid = self.date_paid.isoformat()

        timesheet_import_option: Union[Unset, str] = UNSET
        if not isinstance(self.timesheet_import_option, Unset):
            timesheet_import_option = self.timesheet_import_option.value

        external_id = self.external_id

        callback_url = self.callback_url

        create_with_empty_pays = self.create_with_empty_pays

        adhoc = self.adhoc

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if pay_schedule_id is not UNSET:
            field_dict["payScheduleId"] = pay_schedule_id
        if pay_period_ending is not UNSET:
            field_dict["payPeriodEnding"] = pay_period_ending
        if date_paid is not UNSET:
            field_dict["datePaid"] = date_paid
        if timesheet_import_option is not UNSET:
            field_dict["timesheetImportOption"] = timesheet_import_option
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if callback_url is not UNSET:
            field_dict["callbackUrl"] = callback_url
        if create_with_empty_pays is not UNSET:
            field_dict["createWithEmptyPays"] = create_with_empty_pays
        if adhoc is not UNSET:
            field_dict["adhoc"] = adhoc

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        pay_schedule_id = d.pop("payScheduleId", UNSET)

        _pay_period_ending = d.pop("payPeriodEnding", UNSET)
        pay_period_ending: Union[Unset, datetime.datetime]
        if isinstance(_pay_period_ending, Unset):
            pay_period_ending = UNSET
        else:
            pay_period_ending = isoparse(_pay_period_ending)

        _date_paid = d.pop("datePaid", UNSET)
        date_paid: Union[Unset, datetime.datetime]
        if isinstance(_date_paid, Unset):
            date_paid = UNSET
        else:
            date_paid = isoparse(_date_paid)

        _timesheet_import_option = d.pop("timesheetImportOption", UNSET)
        timesheet_import_option: Union[Unset, PayRunCreateRequestNullableTimesheetImportOption]
        if isinstance(_timesheet_import_option, Unset):
            timesheet_import_option = UNSET
        else:
            timesheet_import_option = PayRunCreateRequestNullableTimesheetImportOption(_timesheet_import_option)

        external_id = d.pop("externalId", UNSET)

        callback_url = d.pop("callbackUrl", UNSET)

        create_with_empty_pays = d.pop("createWithEmptyPays", UNSET)

        adhoc = d.pop("adhoc", UNSET)

        pay_run_create_request = cls(
            pay_schedule_id=pay_schedule_id,
            pay_period_ending=pay_period_ending,
            date_paid=date_paid,
            timesheet_import_option=timesheet_import_option,
            external_id=external_id,
            callback_url=callback_url,
            create_with_empty_pays=create_with_empty_pays,
            adhoc=adhoc,
        )

        pay_run_create_request.additional_properties = d
        return pay_run_create_request

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
