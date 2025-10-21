from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AuApiPaySlipBankPaymentModel")


@_attrs_define
class AuApiPaySlipBankPaymentModel:
    """
    Attributes:
        bsb (Union[Unset, str]):
        account_name (Union[Unset, str]):
        account_number (Union[Unset, str]):
        lodgement_reference (Union[Unset, str]):
        amount (Union[Unset, float]):
    """

    bsb: Union[Unset, str] = UNSET
    account_name: Union[Unset, str] = UNSET
    account_number: Union[Unset, str] = UNSET
    lodgement_reference: Union[Unset, str] = UNSET
    amount: Union[Unset, float] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        bsb = self.bsb

        account_name = self.account_name

        account_number = self.account_number

        lodgement_reference = self.lodgement_reference

        amount = self.amount

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if bsb is not UNSET:
            field_dict["bsb"] = bsb
        if account_name is not UNSET:
            field_dict["accountName"] = account_name
        if account_number is not UNSET:
            field_dict["accountNumber"] = account_number
        if lodgement_reference is not UNSET:
            field_dict["lodgementReference"] = lodgement_reference
        if amount is not UNSET:
            field_dict["amount"] = amount

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        bsb = d.pop("bsb", UNSET)

        account_name = d.pop("accountName", UNSET)

        account_number = d.pop("accountNumber", UNSET)

        lodgement_reference = d.pop("lodgementReference", UNSET)

        amount = d.pop("amount", UNSET)

        au_api_pay_slip_bank_payment_model = cls(
            bsb=bsb,
            account_name=account_name,
            account_number=account_number,
            lodgement_reference=lodgement_reference,
            amount=amount,
        )

        au_api_pay_slip_bank_payment_model.additional_properties = d
        return au_api_pay_slip_bank_payment_model

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
