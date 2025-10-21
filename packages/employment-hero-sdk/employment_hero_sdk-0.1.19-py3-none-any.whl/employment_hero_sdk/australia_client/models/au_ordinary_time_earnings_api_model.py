import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="AuOrdinaryTimeEarningsApiModel")


@_attrs_define
class AuOrdinaryTimeEarningsApiModel:
    """
    Attributes:
        super_ (Union[Unset, float]):
        super_percentage_of_earnings (Union[Unset, float]):
        employee_id (Union[Unset, int]):
        first_name (Union[Unset, str]):
        surname (Union[Unset, str]):
        external_id (Union[Unset, str]):
        pay_run (Union[Unset, str]):
        pay_category (Union[Unset, str]):
        pay_period_starting (Union[Unset, datetime.datetime]):
        pay_period_ending (Union[Unset, datetime.datetime]):
        earnings (Union[Unset, float]):
    """

    super_: Union[Unset, float] = UNSET
    super_percentage_of_earnings: Union[Unset, float] = UNSET
    employee_id: Union[Unset, int] = UNSET
    first_name: Union[Unset, str] = UNSET
    surname: Union[Unset, str] = UNSET
    external_id: Union[Unset, str] = UNSET
    pay_run: Union[Unset, str] = UNSET
    pay_category: Union[Unset, str] = UNSET
    pay_period_starting: Union[Unset, datetime.datetime] = UNSET
    pay_period_ending: Union[Unset, datetime.datetime] = UNSET
    earnings: Union[Unset, float] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        super_ = self.super_

        super_percentage_of_earnings = self.super_percentage_of_earnings

        employee_id = self.employee_id

        first_name = self.first_name

        surname = self.surname

        external_id = self.external_id

        pay_run = self.pay_run

        pay_category = self.pay_category

        pay_period_starting: Union[Unset, str] = UNSET
        if not isinstance(self.pay_period_starting, Unset):
            pay_period_starting = self.pay_period_starting.isoformat()

        pay_period_ending: Union[Unset, str] = UNSET
        if not isinstance(self.pay_period_ending, Unset):
            pay_period_ending = self.pay_period_ending.isoformat()

        earnings = self.earnings

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if super_ is not UNSET:
            field_dict["super"] = super_
        if super_percentage_of_earnings is not UNSET:
            field_dict["superPercentageOfEarnings"] = super_percentage_of_earnings
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if first_name is not UNSET:
            field_dict["firstName"] = first_name
        if surname is not UNSET:
            field_dict["surname"] = surname
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if pay_run is not UNSET:
            field_dict["payRun"] = pay_run
        if pay_category is not UNSET:
            field_dict["payCategory"] = pay_category
        if pay_period_starting is not UNSET:
            field_dict["payPeriodStarting"] = pay_period_starting
        if pay_period_ending is not UNSET:
            field_dict["payPeriodEnding"] = pay_period_ending
        if earnings is not UNSET:
            field_dict["earnings"] = earnings

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        super_ = d.pop("super", UNSET)

        super_percentage_of_earnings = d.pop("superPercentageOfEarnings", UNSET)

        employee_id = d.pop("employeeId", UNSET)

        first_name = d.pop("firstName", UNSET)

        surname = d.pop("surname", UNSET)

        external_id = d.pop("externalId", UNSET)

        pay_run = d.pop("payRun", UNSET)

        pay_category = d.pop("payCategory", UNSET)

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

        earnings = d.pop("earnings", UNSET)

        au_ordinary_time_earnings_api_model = cls(
            super_=super_,
            super_percentage_of_earnings=super_percentage_of_earnings,
            employee_id=employee_id,
            first_name=first_name,
            surname=surname,
            external_id=external_id,
            pay_run=pay_run,
            pay_category=pay_category,
            pay_period_starting=pay_period_starting,
            pay_period_ending=pay_period_ending,
            earnings=earnings,
        )

        au_ordinary_time_earnings_api_model.additional_properties = d
        return au_ordinary_time_earnings_api_model

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
