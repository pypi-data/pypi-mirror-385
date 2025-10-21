from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ApiPaySlipSuperPaymentModel")


@_attrs_define
class ApiPaySlipSuperPaymentModel:
    """
    Attributes:
        fund_name (Union[Unset, str]):
        member_number (Union[Unset, str]):
        amount (Union[Unset, float]):
    """

    fund_name: Union[Unset, str] = UNSET
    member_number: Union[Unset, str] = UNSET
    amount: Union[Unset, float] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        fund_name = self.fund_name

        member_number = self.member_number

        amount = self.amount

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if fund_name is not UNSET:
            field_dict["fundName"] = fund_name
        if member_number is not UNSET:
            field_dict["memberNumber"] = member_number
        if amount is not UNSET:
            field_dict["amount"] = amount

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        fund_name = d.pop("fundName", UNSET)

        member_number = d.pop("memberNumber", UNSET)

        amount = d.pop("amount", UNSET)

        api_pay_slip_super_payment_model = cls(
            fund_name=fund_name,
            member_number=member_number,
            amount=amount,
        )

        api_pay_slip_super_payment_model.additional_properties = d
        return api_pay_slip_super_payment_model

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
