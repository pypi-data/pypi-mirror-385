from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.leave_balance_model_leave_unit_type_enum import LeaveBalanceModelLeaveUnitTypeEnum
from ..types import UNSET, Unset

T = TypeVar("T", bound="LeaveBalanceModel")


@_attrs_define
class LeaveBalanceModel:
    """
    Attributes:
        leave_category_id (Union[Unset, int]):
        leave_category_name (Union[Unset, str]):
        accrued_amount (Union[Unset, float]):
        unit_type (Union[Unset, LeaveBalanceModelLeaveUnitTypeEnum]):
    """

    leave_category_id: Union[Unset, int] = UNSET
    leave_category_name: Union[Unset, str] = UNSET
    accrued_amount: Union[Unset, float] = UNSET
    unit_type: Union[Unset, LeaveBalanceModelLeaveUnitTypeEnum] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        leave_category_id = self.leave_category_id

        leave_category_name = self.leave_category_name

        accrued_amount = self.accrued_amount

        unit_type: Union[Unset, str] = UNSET
        if not isinstance(self.unit_type, Unset):
            unit_type = self.unit_type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if leave_category_id is not UNSET:
            field_dict["leaveCategoryId"] = leave_category_id
        if leave_category_name is not UNSET:
            field_dict["leaveCategoryName"] = leave_category_name
        if accrued_amount is not UNSET:
            field_dict["accruedAmount"] = accrued_amount
        if unit_type is not UNSET:
            field_dict["unitType"] = unit_type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        leave_category_id = d.pop("leaveCategoryId", UNSET)

        leave_category_name = d.pop("leaveCategoryName", UNSET)

        accrued_amount = d.pop("accruedAmount", UNSET)

        _unit_type = d.pop("unitType", UNSET)
        unit_type: Union[Unset, LeaveBalanceModelLeaveUnitTypeEnum]
        if isinstance(_unit_type, Unset):
            unit_type = UNSET
        else:
            unit_type = LeaveBalanceModelLeaveUnitTypeEnum(_unit_type)

        leave_balance_model = cls(
            leave_category_id=leave_category_id,
            leave_category_name=leave_category_name,
            accrued_amount=accrued_amount,
            unit_type=unit_type,
        )

        leave_balance_model.additional_properties = d
        return leave_balance_model

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
