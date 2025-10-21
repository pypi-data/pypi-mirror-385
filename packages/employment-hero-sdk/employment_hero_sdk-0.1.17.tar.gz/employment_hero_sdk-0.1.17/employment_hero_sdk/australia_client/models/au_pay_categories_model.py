import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="AuPayCategoriesModel")


@_attrs_define
class AuPayCategoriesModel:
    """
    Attributes:
        super_amount (Union[Unset, float]):
        pay_category (Union[Unset, str]):
        pay_run (Union[Unset, str]):
        date_paid (Union[Unset, datetime.datetime]):
        employee_id (Union[Unset, int]):
        first_name (Union[Unset, str]):
        surname (Union[Unset, str]):
        external_id (Union[Unset, str]):
        location (Union[Unset, str]):
        units (Union[Unset, float]):
        rate (Union[Unset, float]):
        amount (Union[Unset, float]):
    """

    super_amount: Union[Unset, float] = UNSET
    pay_category: Union[Unset, str] = UNSET
    pay_run: Union[Unset, str] = UNSET
    date_paid: Union[Unset, datetime.datetime] = UNSET
    employee_id: Union[Unset, int] = UNSET
    first_name: Union[Unset, str] = UNSET
    surname: Union[Unset, str] = UNSET
    external_id: Union[Unset, str] = UNSET
    location: Union[Unset, str] = UNSET
    units: Union[Unset, float] = UNSET
    rate: Union[Unset, float] = UNSET
    amount: Union[Unset, float] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        super_amount = self.super_amount

        pay_category = self.pay_category

        pay_run = self.pay_run

        date_paid: Union[Unset, str] = UNSET
        if not isinstance(self.date_paid, Unset):
            date_paid = self.date_paid.isoformat()

        employee_id = self.employee_id

        first_name = self.first_name

        surname = self.surname

        external_id = self.external_id

        location = self.location

        units = self.units

        rate = self.rate

        amount = self.amount

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if super_amount is not UNSET:
            field_dict["superAmount"] = super_amount
        if pay_category is not UNSET:
            field_dict["payCategory"] = pay_category
        if pay_run is not UNSET:
            field_dict["payRun"] = pay_run
        if date_paid is not UNSET:
            field_dict["datePaid"] = date_paid
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if first_name is not UNSET:
            field_dict["firstName"] = first_name
        if surname is not UNSET:
            field_dict["surname"] = surname
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if location is not UNSET:
            field_dict["location"] = location
        if units is not UNSET:
            field_dict["units"] = units
        if rate is not UNSET:
            field_dict["rate"] = rate
        if amount is not UNSET:
            field_dict["amount"] = amount

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        super_amount = d.pop("superAmount", UNSET)

        pay_category = d.pop("payCategory", UNSET)

        pay_run = d.pop("payRun", UNSET)

        _date_paid = d.pop("datePaid", UNSET)
        date_paid: Union[Unset, datetime.datetime]
        if isinstance(_date_paid, Unset):
            date_paid = UNSET
        else:
            date_paid = isoparse(_date_paid)

        employee_id = d.pop("employeeId", UNSET)

        first_name = d.pop("firstName", UNSET)

        surname = d.pop("surname", UNSET)

        external_id = d.pop("externalId", UNSET)

        location = d.pop("location", UNSET)

        units = d.pop("units", UNSET)

        rate = d.pop("rate", UNSET)

        amount = d.pop("amount", UNSET)

        au_pay_categories_model = cls(
            super_amount=super_amount,
            pay_category=pay_category,
            pay_run=pay_run,
            date_paid=date_paid,
            employee_id=employee_id,
            first_name=first_name,
            surname=surname,
            external_id=external_id,
            location=location,
            units=units,
            rate=rate,
            amount=amount,
        )

        au_pay_categories_model.additional_properties = d
        return au_pay_categories_model

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
