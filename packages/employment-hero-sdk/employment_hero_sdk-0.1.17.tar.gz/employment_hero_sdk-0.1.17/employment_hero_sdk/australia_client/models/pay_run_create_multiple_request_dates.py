import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="PayRunCreateMultipleRequestDates")


@_attrs_define
class PayRunCreateMultipleRequestDates:
    """
    Attributes:
        pay_period_ending (Union[Unset, datetime.datetime]):
        date_paid (Union[Unset, datetime.datetime]):
    """

    pay_period_ending: Union[Unset, datetime.datetime] = UNSET
    date_paid: Union[Unset, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        pay_period_ending: Union[Unset, str] = UNSET
        if not isinstance(self.pay_period_ending, Unset):
            pay_period_ending = self.pay_period_ending.isoformat()

        date_paid: Union[Unset, str] = UNSET
        if not isinstance(self.date_paid, Unset):
            date_paid = self.date_paid.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if pay_period_ending is not UNSET:
            field_dict["payPeriodEnding"] = pay_period_ending
        if date_paid is not UNSET:
            field_dict["datePaid"] = date_paid

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
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

        pay_run_create_multiple_request_dates = cls(
            pay_period_ending=pay_period_ending,
            date_paid=date_paid,
        )

        pay_run_create_multiple_request_dates.additional_properties = d
        return pay_run_create_multiple_request_dates

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
