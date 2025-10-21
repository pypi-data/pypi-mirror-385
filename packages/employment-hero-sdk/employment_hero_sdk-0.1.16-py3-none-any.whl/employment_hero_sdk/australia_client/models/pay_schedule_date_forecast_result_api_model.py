import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="PayScheduleDateForecastResultApiModel")


@_attrs_define
class PayScheduleDateForecastResultApiModel:
    """
    Attributes:
        pay_schedule_id (Union[Unset, int]):
        next_scheduled_from_date (Union[Unset, datetime.datetime]):
        next_scheduled_to_date (Union[Unset, datetime.datetime]):
        next_scheduled_paid_date (Union[Unset, datetime.datetime]):
    """

    pay_schedule_id: Union[Unset, int] = UNSET
    next_scheduled_from_date: Union[Unset, datetime.datetime] = UNSET
    next_scheduled_to_date: Union[Unset, datetime.datetime] = UNSET
    next_scheduled_paid_date: Union[Unset, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        pay_schedule_id = self.pay_schedule_id

        next_scheduled_from_date: Union[Unset, str] = UNSET
        if not isinstance(self.next_scheduled_from_date, Unset):
            next_scheduled_from_date = self.next_scheduled_from_date.isoformat()

        next_scheduled_to_date: Union[Unset, str] = UNSET
        if not isinstance(self.next_scheduled_to_date, Unset):
            next_scheduled_to_date = self.next_scheduled_to_date.isoformat()

        next_scheduled_paid_date: Union[Unset, str] = UNSET
        if not isinstance(self.next_scheduled_paid_date, Unset):
            next_scheduled_paid_date = self.next_scheduled_paid_date.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if pay_schedule_id is not UNSET:
            field_dict["payScheduleId"] = pay_schedule_id
        if next_scheduled_from_date is not UNSET:
            field_dict["nextScheduledFromDate"] = next_scheduled_from_date
        if next_scheduled_to_date is not UNSET:
            field_dict["nextScheduledToDate"] = next_scheduled_to_date
        if next_scheduled_paid_date is not UNSET:
            field_dict["nextScheduledPaidDate"] = next_scheduled_paid_date

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        pay_schedule_id = d.pop("payScheduleId", UNSET)

        _next_scheduled_from_date = d.pop("nextScheduledFromDate", UNSET)
        next_scheduled_from_date: Union[Unset, datetime.datetime]
        if isinstance(_next_scheduled_from_date, Unset):
            next_scheduled_from_date = UNSET
        else:
            next_scheduled_from_date = isoparse(_next_scheduled_from_date)

        _next_scheduled_to_date = d.pop("nextScheduledToDate", UNSET)
        next_scheduled_to_date: Union[Unset, datetime.datetime]
        if isinstance(_next_scheduled_to_date, Unset):
            next_scheduled_to_date = UNSET
        else:
            next_scheduled_to_date = isoparse(_next_scheduled_to_date)

        _next_scheduled_paid_date = d.pop("nextScheduledPaidDate", UNSET)
        next_scheduled_paid_date: Union[Unset, datetime.datetime]
        if isinstance(_next_scheduled_paid_date, Unset):
            next_scheduled_paid_date = UNSET
        else:
            next_scheduled_paid_date = isoparse(_next_scheduled_paid_date)

        pay_schedule_date_forecast_result_api_model = cls(
            pay_schedule_id=pay_schedule_id,
            next_scheduled_from_date=next_scheduled_from_date,
            next_scheduled_to_date=next_scheduled_to_date,
            next_scheduled_paid_date=next_scheduled_paid_date,
        )

        pay_schedule_date_forecast_result_api_model.additional_properties = d
        return pay_schedule_date_forecast_result_api_model

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
