import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="AdditionalEarningsInputModel")


@_attrs_define
class AdditionalEarningsInputModel:
    """
    Attributes:
        id (Union[Unset, int]):
        pay_category_id (Union[Unset, int]):
        employee_id (Union[Unset, int]):
        amount (Union[Unset, float]):
        expiry_date (Union[Unset, datetime.datetime]):
        maximum_amount_paid (Union[Unset, float]):
        notes (Union[Unset, str]):
        units (Union[Unset, float]):
        location_id (Union[Unset, int]):
        super_rate (Union[Unset, float]):
        override_super_rate (Union[Unset, bool]):
    """

    id: Union[Unset, int] = UNSET
    pay_category_id: Union[Unset, int] = UNSET
    employee_id: Union[Unset, int] = UNSET
    amount: Union[Unset, float] = UNSET
    expiry_date: Union[Unset, datetime.datetime] = UNSET
    maximum_amount_paid: Union[Unset, float] = UNSET
    notes: Union[Unset, str] = UNSET
    units: Union[Unset, float] = UNSET
    location_id: Union[Unset, int] = UNSET
    super_rate: Union[Unset, float] = UNSET
    override_super_rate: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        pay_category_id = self.pay_category_id

        employee_id = self.employee_id

        amount = self.amount

        expiry_date: Union[Unset, str] = UNSET
        if not isinstance(self.expiry_date, Unset):
            expiry_date = self.expiry_date.isoformat()

        maximum_amount_paid = self.maximum_amount_paid

        notes = self.notes

        units = self.units

        location_id = self.location_id

        super_rate = self.super_rate

        override_super_rate = self.override_super_rate

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if pay_category_id is not UNSET:
            field_dict["payCategoryId"] = pay_category_id
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if amount is not UNSET:
            field_dict["amount"] = amount
        if expiry_date is not UNSET:
            field_dict["expiryDate"] = expiry_date
        if maximum_amount_paid is not UNSET:
            field_dict["maximumAmountPaid"] = maximum_amount_paid
        if notes is not UNSET:
            field_dict["notes"] = notes
        if units is not UNSET:
            field_dict["units"] = units
        if location_id is not UNSET:
            field_dict["locationId"] = location_id
        if super_rate is not UNSET:
            field_dict["superRate"] = super_rate
        if override_super_rate is not UNSET:
            field_dict["overrideSuperRate"] = override_super_rate

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        pay_category_id = d.pop("payCategoryId", UNSET)

        employee_id = d.pop("employeeId", UNSET)

        amount = d.pop("amount", UNSET)

        _expiry_date = d.pop("expiryDate", UNSET)
        expiry_date: Union[Unset, datetime.datetime]
        if isinstance(_expiry_date, Unset):
            expiry_date = UNSET
        else:
            expiry_date = isoparse(_expiry_date)

        maximum_amount_paid = d.pop("maximumAmountPaid", UNSET)

        notes = d.pop("notes", UNSET)

        units = d.pop("units", UNSET)

        location_id = d.pop("locationId", UNSET)

        super_rate = d.pop("superRate", UNSET)

        override_super_rate = d.pop("overrideSuperRate", UNSET)

        additional_earnings_input_model = cls(
            id=id,
            pay_category_id=pay_category_id,
            employee_id=employee_id,
            amount=amount,
            expiry_date=expiry_date,
            maximum_amount_paid=maximum_amount_paid,
            notes=notes,
            units=units,
            location_id=location_id,
            super_rate=super_rate,
            override_super_rate=override_super_rate,
        )

        additional_earnings_input_model.additional_properties = d
        return additional_earnings_input_model

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
