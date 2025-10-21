import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="PayRunSummaryModel")


@_attrs_define
class PayRunSummaryModel:
    """
    Attributes:
        total_hours (Union[Unset, float]):
        total_net_wages (Union[Unset, float]):
        total_gross_wages (Union[Unset, float]):
        id (Union[Unset, int]):
        date_finalised (Union[Unset, datetime.datetime]):
        pay_schedule_id (Union[Unset, int]):
        pay_period_starting (Union[Unset, datetime.datetime]):
        pay_period_ending (Union[Unset, datetime.datetime]):
        date_paid (Union[Unset, datetime.datetime]):
        is_finalised (Union[Unset, bool]):
        pay_slips_published (Union[Unset, bool]):
        notation (Union[Unset, str]):
        external_id (Union[Unset, str]):
    """

    total_hours: Union[Unset, float] = UNSET
    total_net_wages: Union[Unset, float] = UNSET
    total_gross_wages: Union[Unset, float] = UNSET
    id: Union[Unset, int] = UNSET
    date_finalised: Union[Unset, datetime.datetime] = UNSET
    pay_schedule_id: Union[Unset, int] = UNSET
    pay_period_starting: Union[Unset, datetime.datetime] = UNSET
    pay_period_ending: Union[Unset, datetime.datetime] = UNSET
    date_paid: Union[Unset, datetime.datetime] = UNSET
    is_finalised: Union[Unset, bool] = UNSET
    pay_slips_published: Union[Unset, bool] = UNSET
    notation: Union[Unset, str] = UNSET
    external_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        total_hours = self.total_hours

        total_net_wages = self.total_net_wages

        total_gross_wages = self.total_gross_wages

        id = self.id

        date_finalised: Union[Unset, str] = UNSET
        if not isinstance(self.date_finalised, Unset):
            date_finalised = self.date_finalised.isoformat()

        pay_schedule_id = self.pay_schedule_id

        pay_period_starting: Union[Unset, str] = UNSET
        if not isinstance(self.pay_period_starting, Unset):
            pay_period_starting = self.pay_period_starting.isoformat()

        pay_period_ending: Union[Unset, str] = UNSET
        if not isinstance(self.pay_period_ending, Unset):
            pay_period_ending = self.pay_period_ending.isoformat()

        date_paid: Union[Unset, str] = UNSET
        if not isinstance(self.date_paid, Unset):
            date_paid = self.date_paid.isoformat()

        is_finalised = self.is_finalised

        pay_slips_published = self.pay_slips_published

        notation = self.notation

        external_id = self.external_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if total_hours is not UNSET:
            field_dict["totalHours"] = total_hours
        if total_net_wages is not UNSET:
            field_dict["totalNetWages"] = total_net_wages
        if total_gross_wages is not UNSET:
            field_dict["totalGrossWages"] = total_gross_wages
        if id is not UNSET:
            field_dict["id"] = id
        if date_finalised is not UNSET:
            field_dict["dateFinalised"] = date_finalised
        if pay_schedule_id is not UNSET:
            field_dict["payScheduleId"] = pay_schedule_id
        if pay_period_starting is not UNSET:
            field_dict["payPeriodStarting"] = pay_period_starting
        if pay_period_ending is not UNSET:
            field_dict["payPeriodEnding"] = pay_period_ending
        if date_paid is not UNSET:
            field_dict["datePaid"] = date_paid
        if is_finalised is not UNSET:
            field_dict["isFinalised"] = is_finalised
        if pay_slips_published is not UNSET:
            field_dict["paySlipsPublished"] = pay_slips_published
        if notation is not UNSET:
            field_dict["notation"] = notation
        if external_id is not UNSET:
            field_dict["externalId"] = external_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        total_hours = d.pop("totalHours", UNSET)

        total_net_wages = d.pop("totalNetWages", UNSET)

        total_gross_wages = d.pop("totalGrossWages", UNSET)

        id = d.pop("id", UNSET)

        _date_finalised = d.pop("dateFinalised", UNSET)
        date_finalised: Union[Unset, datetime.datetime]
        if isinstance(_date_finalised, Unset):
            date_finalised = UNSET
        else:
            date_finalised = isoparse(_date_finalised)

        pay_schedule_id = d.pop("payScheduleId", UNSET)

        _pay_period_starting = d.pop("payPeriodStarting", UNSET)
        pay_period_starting: Union[Unset, datetime.datetime]
        if isinstance(_pay_period_starting, Unset):
            pay_period_starting = UNSET
        else:
            pay_period_starting = isoparse(_pay_period_starting)

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

        is_finalised = d.pop("isFinalised", UNSET)

        pay_slips_published = d.pop("paySlipsPublished", UNSET)

        notation = d.pop("notation", UNSET)

        external_id = d.pop("externalId", UNSET)

        pay_run_summary_model = cls(
            total_hours=total_hours,
            total_net_wages=total_net_wages,
            total_gross_wages=total_gross_wages,
            id=id,
            date_finalised=date_finalised,
            pay_schedule_id=pay_schedule_id,
            pay_period_starting=pay_period_starting,
            pay_period_ending=pay_period_ending,
            date_paid=date_paid,
            is_finalised=is_finalised,
            pay_slips_published=pay_slips_published,
            notation=notation,
            external_id=external_id,
        )

        pay_run_summary_model.additional_properties = d
        return pay_run_summary_model

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
