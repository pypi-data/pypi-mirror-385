from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ApiPaySlipDeductionModel")


@_attrs_define
class ApiPaySlipDeductionModel:
    """
    Attributes:
        notes (Union[Unset, str]):
        amount (Union[Unset, float]):
        tax_status (Union[Unset, str]):
        name (Union[Unset, str]):
    """

    notes: Union[Unset, str] = UNSET
    amount: Union[Unset, float] = UNSET
    tax_status: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        notes = self.notes

        amount = self.amount

        tax_status = self.tax_status

        name = self.name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if notes is not UNSET:
            field_dict["notes"] = notes
        if amount is not UNSET:
            field_dict["amount"] = amount
        if tax_status is not UNSET:
            field_dict["taxStatus"] = tax_status
        if name is not UNSET:
            field_dict["name"] = name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        notes = d.pop("notes", UNSET)

        amount = d.pop("amount", UNSET)

        tax_status = d.pop("taxStatus", UNSET)

        name = d.pop("name", UNSET)

        api_pay_slip_deduction_model = cls(
            notes=notes,
            amount=amount,
            tax_status=tax_status,
            name=name,
        )

        api_pay_slip_deduction_model.additional_properties = d
        return api_pay_slip_deduction_model

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
