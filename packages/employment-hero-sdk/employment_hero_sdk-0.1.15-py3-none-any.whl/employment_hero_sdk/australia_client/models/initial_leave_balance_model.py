from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.initial_leave_balance_model_leave_unit_type_enum import InitialLeaveBalanceModelLeaveUnitTypeEnum
from ..types import UNSET, Unset

T = TypeVar("T", bound="InitialLeaveBalanceModel")


@_attrs_define
class InitialLeaveBalanceModel:
    """
    Attributes:
        leave_category_id (Union[Unset, int]):
        name (Union[Unset, str]):
        amount (Union[Unset, float]):
        unit_type (Union[Unset, InitialLeaveBalanceModelLeaveUnitTypeEnum]):
    """

    leave_category_id: Union[Unset, int] = UNSET
    name: Union[Unset, str] = UNSET
    amount: Union[Unset, float] = UNSET
    unit_type: Union[Unset, InitialLeaveBalanceModelLeaveUnitTypeEnum] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        leave_category_id = self.leave_category_id

        name = self.name

        amount = self.amount

        unit_type: Union[Unset, str] = UNSET
        if not isinstance(self.unit_type, Unset):
            unit_type = self.unit_type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if leave_category_id is not UNSET:
            field_dict["leaveCategoryId"] = leave_category_id
        if name is not UNSET:
            field_dict["name"] = name
        if amount is not UNSET:
            field_dict["amount"] = amount
        if unit_type is not UNSET:
            field_dict["unitType"] = unit_type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        leave_category_id = d.pop("leaveCategoryId", UNSET)

        name = d.pop("name", UNSET)

        amount = d.pop("amount", UNSET)

        _unit_type = d.pop("unitType", UNSET)
        unit_type: Union[Unset, InitialLeaveBalanceModelLeaveUnitTypeEnum]
        if isinstance(_unit_type, Unset):
            unit_type = UNSET
        else:
            unit_type = InitialLeaveBalanceModelLeaveUnitTypeEnum(_unit_type)

        initial_leave_balance_model = cls(
            leave_category_id=leave_category_id,
            name=name,
            amount=amount,
            unit_type=unit_type,
        )

        initial_leave_balance_model.additional_properties = d
        return initial_leave_balance_model

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
