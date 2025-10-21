from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ApiPaySlipLeaveModel")


@_attrs_define
class ApiPaySlipLeaveModel:
    """
    Attributes:
        leave_category (Union[Unset, str]):
        amount (Union[Unset, float]):
        notes (Union[Unset, str]):
    """

    leave_category: Union[Unset, str] = UNSET
    amount: Union[Unset, float] = UNSET
    notes: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        leave_category = self.leave_category

        amount = self.amount

        notes = self.notes

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if leave_category is not UNSET:
            field_dict["leaveCategory"] = leave_category
        if amount is not UNSET:
            field_dict["amount"] = amount
        if notes is not UNSET:
            field_dict["notes"] = notes

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        leave_category = d.pop("leaveCategory", UNSET)

        amount = d.pop("amount", UNSET)

        notes = d.pop("notes", UNSET)

        api_pay_slip_leave_model = cls(
            leave_category=leave_category,
            amount=amount,
            notes=notes,
        )

        api_pay_slip_leave_model.additional_properties = d
        return api_pay_slip_leave_model

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
