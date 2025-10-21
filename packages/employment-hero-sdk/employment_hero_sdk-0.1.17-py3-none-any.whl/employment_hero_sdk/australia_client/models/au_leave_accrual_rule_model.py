from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.au_leave_accrual_rule_model_leave_accrual_cap_type import AuLeaveAccrualRuleModelLeaveAccrualCapType
from ..models.au_leave_accrual_rule_model_leave_accrual_carry_over_behaviour import (
    AuLeaveAccrualRuleModelLeaveAccrualCarryOverBehaviour,
)
from ..models.au_leave_accrual_rule_model_leave_accrual_type import AuLeaveAccrualRuleModelLeaveAccrualType
from ..types import UNSET, Unset

T = TypeVar("T", bound="AuLeaveAccrualRuleModel")


@_attrs_define
class AuLeaveAccrualRuleModel:
    """
    Attributes:
        leave_year_offset_amount (Union[Unset, int]):
        id (Union[Unset, int]):
        cap_type (Union[Unset, AuLeaveAccrualRuleModelLeaveAccrualCapType]):
        unit_cap (Union[Unset, float]):
        carry_over_behaviour (Union[Unset, AuLeaveAccrualRuleModelLeaveAccrualCarryOverBehaviour]):
        carry_over_amount (Union[Unset, float]):
        accrue_in_advance (Union[Unset, bool]):
        accrual_type (Union[Unset, AuLeaveAccrualRuleModelLeaveAccrualType]):
    """

    leave_year_offset_amount: Union[Unset, int] = UNSET
    id: Union[Unset, int] = UNSET
    cap_type: Union[Unset, AuLeaveAccrualRuleModelLeaveAccrualCapType] = UNSET
    unit_cap: Union[Unset, float] = UNSET
    carry_over_behaviour: Union[Unset, AuLeaveAccrualRuleModelLeaveAccrualCarryOverBehaviour] = UNSET
    carry_over_amount: Union[Unset, float] = UNSET
    accrue_in_advance: Union[Unset, bool] = UNSET
    accrual_type: Union[Unset, AuLeaveAccrualRuleModelLeaveAccrualType] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        leave_year_offset_amount = self.leave_year_offset_amount

        id = self.id

        cap_type: Union[Unset, str] = UNSET
        if not isinstance(self.cap_type, Unset):
            cap_type = self.cap_type.value

        unit_cap = self.unit_cap

        carry_over_behaviour: Union[Unset, str] = UNSET
        if not isinstance(self.carry_over_behaviour, Unset):
            carry_over_behaviour = self.carry_over_behaviour.value

        carry_over_amount = self.carry_over_amount

        accrue_in_advance = self.accrue_in_advance

        accrual_type: Union[Unset, str] = UNSET
        if not isinstance(self.accrual_type, Unset):
            accrual_type = self.accrual_type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if leave_year_offset_amount is not UNSET:
            field_dict["leaveYearOffsetAmount"] = leave_year_offset_amount
        if id is not UNSET:
            field_dict["id"] = id
        if cap_type is not UNSET:
            field_dict["capType"] = cap_type
        if unit_cap is not UNSET:
            field_dict["unitCap"] = unit_cap
        if carry_over_behaviour is not UNSET:
            field_dict["carryOverBehaviour"] = carry_over_behaviour
        if carry_over_amount is not UNSET:
            field_dict["carryOverAmount"] = carry_over_amount
        if accrue_in_advance is not UNSET:
            field_dict["accrueInAdvance"] = accrue_in_advance
        if accrual_type is not UNSET:
            field_dict["accrualType"] = accrual_type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        leave_year_offset_amount = d.pop("leaveYearOffsetAmount", UNSET)

        id = d.pop("id", UNSET)

        _cap_type = d.pop("capType", UNSET)
        cap_type: Union[Unset, AuLeaveAccrualRuleModelLeaveAccrualCapType]
        if isinstance(_cap_type, Unset):
            cap_type = UNSET
        else:
            cap_type = AuLeaveAccrualRuleModelLeaveAccrualCapType(_cap_type)

        unit_cap = d.pop("unitCap", UNSET)

        _carry_over_behaviour = d.pop("carryOverBehaviour", UNSET)
        carry_over_behaviour: Union[Unset, AuLeaveAccrualRuleModelLeaveAccrualCarryOverBehaviour]
        if isinstance(_carry_over_behaviour, Unset):
            carry_over_behaviour = UNSET
        else:
            carry_over_behaviour = AuLeaveAccrualRuleModelLeaveAccrualCarryOverBehaviour(_carry_over_behaviour)

        carry_over_amount = d.pop("carryOverAmount", UNSET)

        accrue_in_advance = d.pop("accrueInAdvance", UNSET)

        _accrual_type = d.pop("accrualType", UNSET)
        accrual_type: Union[Unset, AuLeaveAccrualRuleModelLeaveAccrualType]
        if isinstance(_accrual_type, Unset):
            accrual_type = UNSET
        else:
            accrual_type = AuLeaveAccrualRuleModelLeaveAccrualType(_accrual_type)

        au_leave_accrual_rule_model = cls(
            leave_year_offset_amount=leave_year_offset_amount,
            id=id,
            cap_type=cap_type,
            unit_cap=unit_cap,
            carry_over_behaviour=carry_over_behaviour,
            carry_over_amount=carry_over_amount,
            accrue_in_advance=accrue_in_advance,
            accrual_type=accrual_type,
        )

        au_leave_accrual_rule_model.additional_properties = d
        return au_leave_accrual_rule_model

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
