from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="LeaveAccrualModel")


@_attrs_define
class LeaveAccrualModel:
    """
    Attributes:
        id (Union[Unset, int]):
        leave_category_name (Union[Unset, str]):
        leave_category_id (Union[Unset, str]):
        amount (Union[Unset, float]):
        notes (Union[Unset, str]):
        accrual_type (Union[Unset, str]):
    """

    id: Union[Unset, int] = UNSET
    leave_category_name: Union[Unset, str] = UNSET
    leave_category_id: Union[Unset, str] = UNSET
    amount: Union[Unset, float] = UNSET
    notes: Union[Unset, str] = UNSET
    accrual_type: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        leave_category_name = self.leave_category_name

        leave_category_id = self.leave_category_id

        amount = self.amount

        notes = self.notes

        accrual_type = self.accrual_type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if leave_category_name is not UNSET:
            field_dict["leaveCategoryName"] = leave_category_name
        if leave_category_id is not UNSET:
            field_dict["leaveCategoryId"] = leave_category_id
        if amount is not UNSET:
            field_dict["amount"] = amount
        if notes is not UNSET:
            field_dict["notes"] = notes
        if accrual_type is not UNSET:
            field_dict["accrualType"] = accrual_type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        leave_category_name = d.pop("leaveCategoryName", UNSET)

        leave_category_id = d.pop("leaveCategoryId", UNSET)

        amount = d.pop("amount", UNSET)

        notes = d.pop("notes", UNSET)

        accrual_type = d.pop("accrualType", UNSET)

        leave_accrual_model = cls(
            id=id,
            leave_category_name=leave_category_name,
            leave_category_id=leave_category_id,
            amount=amount,
            notes=notes,
            accrual_type=accrual_type,
        )

        leave_accrual_model.additional_properties = d
        return leave_accrual_model

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
