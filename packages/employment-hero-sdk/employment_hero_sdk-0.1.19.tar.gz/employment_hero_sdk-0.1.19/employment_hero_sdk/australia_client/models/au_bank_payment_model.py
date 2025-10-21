from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AuBankPaymentModel")


@_attrs_define
class AuBankPaymentModel:
    """
    Attributes:
        bsb (Union[Unset, str]):
        employee_id (Union[Unset, int]):
        employee_external_id (Union[Unset, str]):
        employee_first_name (Union[Unset, str]):
        employee_surname (Union[Unset, str]):
        account_name (Union[Unset, str]):
        account_number (Union[Unset, str]):
        amount (Union[Unset, float]):
        account_type (Union[Unset, str]):
        lodgement_reference (Union[Unset, str]):
    """

    bsb: Union[Unset, str] = UNSET
    employee_id: Union[Unset, int] = UNSET
    employee_external_id: Union[Unset, str] = UNSET
    employee_first_name: Union[Unset, str] = UNSET
    employee_surname: Union[Unset, str] = UNSET
    account_name: Union[Unset, str] = UNSET
    account_number: Union[Unset, str] = UNSET
    amount: Union[Unset, float] = UNSET
    account_type: Union[Unset, str] = UNSET
    lodgement_reference: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        bsb = self.bsb

        employee_id = self.employee_id

        employee_external_id = self.employee_external_id

        employee_first_name = self.employee_first_name

        employee_surname = self.employee_surname

        account_name = self.account_name

        account_number = self.account_number

        amount = self.amount

        account_type = self.account_type

        lodgement_reference = self.lodgement_reference

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if bsb is not UNSET:
            field_dict["bsb"] = bsb
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if employee_external_id is not UNSET:
            field_dict["employeeExternalId"] = employee_external_id
        if employee_first_name is not UNSET:
            field_dict["employeeFirstName"] = employee_first_name
        if employee_surname is not UNSET:
            field_dict["employeeSurname"] = employee_surname
        if account_name is not UNSET:
            field_dict["accountName"] = account_name
        if account_number is not UNSET:
            field_dict["accountNumber"] = account_number
        if amount is not UNSET:
            field_dict["amount"] = amount
        if account_type is not UNSET:
            field_dict["accountType"] = account_type
        if lodgement_reference is not UNSET:
            field_dict["lodgementReference"] = lodgement_reference

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        bsb = d.pop("bsb", UNSET)

        employee_id = d.pop("employeeId", UNSET)

        employee_external_id = d.pop("employeeExternalId", UNSET)

        employee_first_name = d.pop("employeeFirstName", UNSET)

        employee_surname = d.pop("employeeSurname", UNSET)

        account_name = d.pop("accountName", UNSET)

        account_number = d.pop("accountNumber", UNSET)

        amount = d.pop("amount", UNSET)

        account_type = d.pop("accountType", UNSET)

        lodgement_reference = d.pop("lodgementReference", UNSET)

        au_bank_payment_model = cls(
            bsb=bsb,
            employee_id=employee_id,
            employee_external_id=employee_external_id,
            employee_first_name=employee_first_name,
            employee_surname=employee_surname,
            account_name=account_name,
            account_number=account_number,
            amount=amount,
            account_type=account_type,
            lodgement_reference=lodgement_reference,
        )

        au_bank_payment_model.additional_properties = d
        return au_bank_payment_model

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
