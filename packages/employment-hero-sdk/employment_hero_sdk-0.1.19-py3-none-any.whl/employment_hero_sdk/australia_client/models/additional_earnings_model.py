import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.additional_earnings_model_expiration_type_enum import AdditionalEarningsModelExpirationTypeEnum
from ..types import UNSET, Unset

T = TypeVar("T", bound="AdditionalEarningsModel")


@_attrs_define
class AdditionalEarningsModel:
    """
    Attributes:
        id (Union[Unset, int]):
        name (Union[Unset, str]):
        pay_category_id (Union[Unset, int]):
        employee_id (Union[Unset, int]):
        amount (Union[Unset, float]):
        start_date (Union[Unset, datetime.datetime]):
        expiry_date (Union[Unset, datetime.datetime]):
        maximum_amount_paid (Union[Unset, float]):
        is_active (Union[Unset, bool]):
        notes (Union[Unset, str]):
        expiration_type (Union[Unset, AdditionalEarningsModelExpirationTypeEnum]):
        total_amount_paid (Union[Unset, float]):
        units (Union[Unset, float]):
        location_id (Union[Unset, int]):
        location_name (Union[Unset, str]):
        super_rate (Union[Unset, float]):
        override_super_rate (Union[Unset, bool]):
    """

    id: Union[Unset, int] = UNSET
    name: Union[Unset, str] = UNSET
    pay_category_id: Union[Unset, int] = UNSET
    employee_id: Union[Unset, int] = UNSET
    amount: Union[Unset, float] = UNSET
    start_date: Union[Unset, datetime.datetime] = UNSET
    expiry_date: Union[Unset, datetime.datetime] = UNSET
    maximum_amount_paid: Union[Unset, float] = UNSET
    is_active: Union[Unset, bool] = UNSET
    notes: Union[Unset, str] = UNSET
    expiration_type: Union[Unset, AdditionalEarningsModelExpirationTypeEnum] = UNSET
    total_amount_paid: Union[Unset, float] = UNSET
    units: Union[Unset, float] = UNSET
    location_id: Union[Unset, int] = UNSET
    location_name: Union[Unset, str] = UNSET
    super_rate: Union[Unset, float] = UNSET
    override_super_rate: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        name = self.name

        pay_category_id = self.pay_category_id

        employee_id = self.employee_id

        amount = self.amount

        start_date: Union[Unset, str] = UNSET
        if not isinstance(self.start_date, Unset):
            start_date = self.start_date.isoformat()

        expiry_date: Union[Unset, str] = UNSET
        if not isinstance(self.expiry_date, Unset):
            expiry_date = self.expiry_date.isoformat()

        maximum_amount_paid = self.maximum_amount_paid

        is_active = self.is_active

        notes = self.notes

        expiration_type: Union[Unset, str] = UNSET
        if not isinstance(self.expiration_type, Unset):
            expiration_type = self.expiration_type.value

        total_amount_paid = self.total_amount_paid

        units = self.units

        location_id = self.location_id

        location_name = self.location_name

        super_rate = self.super_rate

        override_super_rate = self.override_super_rate

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if pay_category_id is not UNSET:
            field_dict["payCategoryId"] = pay_category_id
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if amount is not UNSET:
            field_dict["amount"] = amount
        if start_date is not UNSET:
            field_dict["startDate"] = start_date
        if expiry_date is not UNSET:
            field_dict["expiryDate"] = expiry_date
        if maximum_amount_paid is not UNSET:
            field_dict["maximumAmountPaid"] = maximum_amount_paid
        if is_active is not UNSET:
            field_dict["isActive"] = is_active
        if notes is not UNSET:
            field_dict["notes"] = notes
        if expiration_type is not UNSET:
            field_dict["expirationType"] = expiration_type
        if total_amount_paid is not UNSET:
            field_dict["totalAmountPaid"] = total_amount_paid
        if units is not UNSET:
            field_dict["units"] = units
        if location_id is not UNSET:
            field_dict["locationId"] = location_id
        if location_name is not UNSET:
            field_dict["locationName"] = location_name
        if super_rate is not UNSET:
            field_dict["superRate"] = super_rate
        if override_super_rate is not UNSET:
            field_dict["overrideSuperRate"] = override_super_rate

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        pay_category_id = d.pop("payCategoryId", UNSET)

        employee_id = d.pop("employeeId", UNSET)

        amount = d.pop("amount", UNSET)

        _start_date = d.pop("startDate", UNSET)
        start_date: Union[Unset, datetime.datetime]
        if isinstance(_start_date, Unset):
            start_date = UNSET
        else:
            start_date = isoparse(_start_date)

        _expiry_date = d.pop("expiryDate", UNSET)
        expiry_date: Union[Unset, datetime.datetime]
        if isinstance(_expiry_date, Unset):
            expiry_date = UNSET
        else:
            expiry_date = isoparse(_expiry_date)

        maximum_amount_paid = d.pop("maximumAmountPaid", UNSET)

        is_active = d.pop("isActive", UNSET)

        notes = d.pop("notes", UNSET)

        _expiration_type = d.pop("expirationType", UNSET)
        expiration_type: Union[Unset, AdditionalEarningsModelExpirationTypeEnum]
        if isinstance(_expiration_type, Unset):
            expiration_type = UNSET
        else:
            expiration_type = AdditionalEarningsModelExpirationTypeEnum(_expiration_type)

        total_amount_paid = d.pop("totalAmountPaid", UNSET)

        units = d.pop("units", UNSET)

        location_id = d.pop("locationId", UNSET)

        location_name = d.pop("locationName", UNSET)

        super_rate = d.pop("superRate", UNSET)

        override_super_rate = d.pop("overrideSuperRate", UNSET)

        additional_earnings_model = cls(
            id=id,
            name=name,
            pay_category_id=pay_category_id,
            employee_id=employee_id,
            amount=amount,
            start_date=start_date,
            expiry_date=expiry_date,
            maximum_amount_paid=maximum_amount_paid,
            is_active=is_active,
            notes=notes,
            expiration_type=expiration_type,
            total_amount_paid=total_amount_paid,
            units=units,
            location_id=location_id,
            location_name=location_name,
            super_rate=super_rate,
            override_super_rate=override_super_rate,
        )

        additional_earnings_model.additional_properties = d
        return additional_earnings_model

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
