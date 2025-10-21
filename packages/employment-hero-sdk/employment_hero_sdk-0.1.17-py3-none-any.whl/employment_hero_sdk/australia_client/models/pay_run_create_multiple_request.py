from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.pay_run_create_multiple_request_nullable_timesheet_import_option import (
    PayRunCreateMultipleRequestNullableTimesheetImportOption,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="PayRunCreateMultipleRequest")


@_attrs_define
class PayRunCreateMultipleRequest:
    """
    Attributes:
        pay_schedule_id (Union[Unset, int]):
        timesheet_import_option (Union[Unset, PayRunCreateMultipleRequestNullableTimesheetImportOption]):
        external_id (Union[Unset, str]):
        callback_url (Union[Unset, str]):
        create_with_empty_pays (Union[Unset, bool]):
        adhoc (Union[Unset, bool]):
    """

    pay_schedule_id: Union[Unset, int] = UNSET
    timesheet_import_option: Union[Unset, PayRunCreateMultipleRequestNullableTimesheetImportOption] = UNSET
    external_id: Union[Unset, str] = UNSET
    callback_url: Union[Unset, str] = UNSET
    create_with_empty_pays: Union[Unset, bool] = UNSET
    adhoc: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        pay_schedule_id = self.pay_schedule_id

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

        _timesheet_import_option = d.pop("timesheetImportOption", UNSET)
        timesheet_import_option: Union[Unset, PayRunCreateMultipleRequestNullableTimesheetImportOption]
        if isinstance(_timesheet_import_option, Unset):
            timesheet_import_option = UNSET
        else:
            timesheet_import_option = PayRunCreateMultipleRequestNullableTimesheetImportOption(_timesheet_import_option)

        external_id = d.pop("externalId", UNSET)

        callback_url = d.pop("callbackUrl", UNSET)

        create_with_empty_pays = d.pop("createWithEmptyPays", UNSET)

        adhoc = d.pop("adhoc", UNSET)

        pay_run_create_multiple_request = cls(
            pay_schedule_id=pay_schedule_id,
            timesheet_import_option=timesheet_import_option,
            external_id=external_id,
            callback_url=callback_url,
            create_with_empty_pays=create_with_empty_pays,
            adhoc=adhoc,
        )

        pay_run_create_multiple_request.additional_properties = d
        return pay_run_create_multiple_request

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
