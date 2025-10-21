import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="AuPaymentHistoryModel")


@_attrs_define
class AuPaymentHistoryModel:
    """
    Attributes:
        bsb (Union[Unset, str]):
        employee_id (Union[Unset, int]):
        first_name (Union[Unset, str]):
        surname (Union[Unset, str]):
        external_id (Union[Unset, str]):
        date_paid (Union[Unset, datetime.datetime]):
        location_name (Union[Unset, str]):
        account_name (Union[Unset, str]):
        account_number (Union[Unset, str]):
        account_type (Union[Unset, str]):
        taxable_earnings (Union[Unset, float]):
        net_earnings (Union[Unset, float]):
        total_allowances (Union[Unset, float]):
        total_deductions (Union[Unset, float]):
        amount (Union[Unset, float]):
    """

    bsb: Union[Unset, str] = UNSET
    employee_id: Union[Unset, int] = UNSET
    first_name: Union[Unset, str] = UNSET
    surname: Union[Unset, str] = UNSET
    external_id: Union[Unset, str] = UNSET
    date_paid: Union[Unset, datetime.datetime] = UNSET
    location_name: Union[Unset, str] = UNSET
    account_name: Union[Unset, str] = UNSET
    account_number: Union[Unset, str] = UNSET
    account_type: Union[Unset, str] = UNSET
    taxable_earnings: Union[Unset, float] = UNSET
    net_earnings: Union[Unset, float] = UNSET
    total_allowances: Union[Unset, float] = UNSET
    total_deductions: Union[Unset, float] = UNSET
    amount: Union[Unset, float] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        bsb = self.bsb

        employee_id = self.employee_id

        first_name = self.first_name

        surname = self.surname

        external_id = self.external_id

        date_paid: Union[Unset, str] = UNSET
        if not isinstance(self.date_paid, Unset):
            date_paid = self.date_paid.isoformat()

        location_name = self.location_name

        account_name = self.account_name

        account_number = self.account_number

        account_type = self.account_type

        taxable_earnings = self.taxable_earnings

        net_earnings = self.net_earnings

        total_allowances = self.total_allowances

        total_deductions = self.total_deductions

        amount = self.amount

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if bsb is not UNSET:
            field_dict["bsb"] = bsb
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if first_name is not UNSET:
            field_dict["firstName"] = first_name
        if surname is not UNSET:
            field_dict["surname"] = surname
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if date_paid is not UNSET:
            field_dict["datePaid"] = date_paid
        if location_name is not UNSET:
            field_dict["locationName"] = location_name
        if account_name is not UNSET:
            field_dict["accountName"] = account_name
        if account_number is not UNSET:
            field_dict["accountNumber"] = account_number
        if account_type is not UNSET:
            field_dict["accountType"] = account_type
        if taxable_earnings is not UNSET:
            field_dict["taxableEarnings"] = taxable_earnings
        if net_earnings is not UNSET:
            field_dict["netEarnings"] = net_earnings
        if total_allowances is not UNSET:
            field_dict["totalAllowances"] = total_allowances
        if total_deductions is not UNSET:
            field_dict["totalDeductions"] = total_deductions
        if amount is not UNSET:
            field_dict["amount"] = amount

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        bsb = d.pop("bsb", UNSET)

        employee_id = d.pop("employeeId", UNSET)

        first_name = d.pop("firstName", UNSET)

        surname = d.pop("surname", UNSET)

        external_id = d.pop("externalId", UNSET)

        _date_paid = d.pop("datePaid", UNSET)
        date_paid: Union[Unset, datetime.datetime]
        if isinstance(_date_paid, Unset):
            date_paid = UNSET
        else:
            date_paid = isoparse(_date_paid)

        location_name = d.pop("locationName", UNSET)

        account_name = d.pop("accountName", UNSET)

        account_number = d.pop("accountNumber", UNSET)

        account_type = d.pop("accountType", UNSET)

        taxable_earnings = d.pop("taxableEarnings", UNSET)

        net_earnings = d.pop("netEarnings", UNSET)

        total_allowances = d.pop("totalAllowances", UNSET)

        total_deductions = d.pop("totalDeductions", UNSET)

        amount = d.pop("amount", UNSET)

        au_payment_history_model = cls(
            bsb=bsb,
            employee_id=employee_id,
            first_name=first_name,
            surname=surname,
            external_id=external_id,
            date_paid=date_paid,
            location_name=location_name,
            account_name=account_name,
            account_number=account_number,
            account_type=account_type,
            taxable_earnings=taxable_earnings,
            net_earnings=net_earnings,
            total_allowances=total_allowances,
            total_deductions=total_deductions,
            amount=amount,
        )

        au_payment_history_model.additional_properties = d
        return au_payment_history_model

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
