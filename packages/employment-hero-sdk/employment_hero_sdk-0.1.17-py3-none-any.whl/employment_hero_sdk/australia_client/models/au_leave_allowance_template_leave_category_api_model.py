from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.au_leave_allowance_template_leave_category_api_model_leave_accrual_cap_type import (
    AuLeaveAllowanceTemplateLeaveCategoryApiModelLeaveAccrualCapType,
)
from ..models.au_leave_allowance_template_leave_category_api_model_leave_accrual_carry_over_behaviour import (
    AuLeaveAllowanceTemplateLeaveCategoryApiModelLeaveAccrualCarryOverBehaviour,
)
from ..models.au_leave_allowance_template_leave_category_api_model_leave_accrual_type import (
    AuLeaveAllowanceTemplateLeaveCategoryApiModelLeaveAccrualType,
)
from ..models.au_leave_allowance_template_leave_category_api_model_nullable_leave_allowance_unit_enum import (
    AuLeaveAllowanceTemplateLeaveCategoryApiModelNullableLeaveAllowanceUnitEnum,
)
from ..models.au_leave_allowance_template_leave_category_api_model_nullable_leave_unit_type_enum import (
    AuLeaveAllowanceTemplateLeaveCategoryApiModelNullableLeaveUnitTypeEnum,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="AuLeaveAllowanceTemplateLeaveCategoryApiModel")


@_attrs_define
class AuLeaveAllowanceTemplateLeaveCategoryApiModel:
    """
    Attributes:
        leave_loading (Union[Unset, float]):
        contingent_period (Union[Unset, float]):
        entitlement_period (Union[Unset, float]):
        unit_type (Union[Unset, AuLeaveAllowanceTemplateLeaveCategoryApiModelNullableLeaveAllowanceUnitEnum]):
        leave_unit_type (Union[Unset, AuLeaveAllowanceTemplateLeaveCategoryApiModelNullableLeaveUnitTypeEnum]):
        accrual_rule_leave_year_offset_amount (Union[Unset, int]):
        leave_category_id (Union[Unset, int]):
        leave_category_name (Union[Unset, str]):
        units (Union[Unset, float]):
        can_apply_for_leave (Union[Unset, bool]):
        leave_accrual_rule_accrual_type (Union[Unset, AuLeaveAllowanceTemplateLeaveCategoryApiModelLeaveAccrualType]):
        leave_accrual_rule_cap_type (Union[Unset, AuLeaveAllowanceTemplateLeaveCategoryApiModelLeaveAccrualCapType]):
        leave_accrual_rule_unit_cap (Union[Unset, float]):
        leave_accrual_rule_carry_over_behaviour (Union[Unset,
            AuLeaveAllowanceTemplateLeaveCategoryApiModelLeaveAccrualCarryOverBehaviour]):
        leave_accrual_rule_carry_over_amount (Union[Unset, float]):
        leave_accrual_rule_accrue_in_advance (Union[Unset, bool]):
    """

    leave_loading: Union[Unset, float] = UNSET
    contingent_period: Union[Unset, float] = UNSET
    entitlement_period: Union[Unset, float] = UNSET
    unit_type: Union[Unset, AuLeaveAllowanceTemplateLeaveCategoryApiModelNullableLeaveAllowanceUnitEnum] = UNSET
    leave_unit_type: Union[Unset, AuLeaveAllowanceTemplateLeaveCategoryApiModelNullableLeaveUnitTypeEnum] = UNSET
    accrual_rule_leave_year_offset_amount: Union[Unset, int] = UNSET
    leave_category_id: Union[Unset, int] = UNSET
    leave_category_name: Union[Unset, str] = UNSET
    units: Union[Unset, float] = UNSET
    can_apply_for_leave: Union[Unset, bool] = UNSET
    leave_accrual_rule_accrual_type: Union[Unset, AuLeaveAllowanceTemplateLeaveCategoryApiModelLeaveAccrualType] = UNSET
    leave_accrual_rule_cap_type: Union[Unset, AuLeaveAllowanceTemplateLeaveCategoryApiModelLeaveAccrualCapType] = UNSET
    leave_accrual_rule_unit_cap: Union[Unset, float] = UNSET
    leave_accrual_rule_carry_over_behaviour: Union[
        Unset, AuLeaveAllowanceTemplateLeaveCategoryApiModelLeaveAccrualCarryOverBehaviour
    ] = UNSET
    leave_accrual_rule_carry_over_amount: Union[Unset, float] = UNSET
    leave_accrual_rule_accrue_in_advance: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        leave_loading = self.leave_loading

        contingent_period = self.contingent_period

        entitlement_period = self.entitlement_period

        unit_type: Union[Unset, str] = UNSET
        if not isinstance(self.unit_type, Unset):
            unit_type = self.unit_type.value

        leave_unit_type: Union[Unset, str] = UNSET
        if not isinstance(self.leave_unit_type, Unset):
            leave_unit_type = self.leave_unit_type.value

        accrual_rule_leave_year_offset_amount = self.accrual_rule_leave_year_offset_amount

        leave_category_id = self.leave_category_id

        leave_category_name = self.leave_category_name

        units = self.units

        can_apply_for_leave = self.can_apply_for_leave

        leave_accrual_rule_accrual_type: Union[Unset, str] = UNSET
        if not isinstance(self.leave_accrual_rule_accrual_type, Unset):
            leave_accrual_rule_accrual_type = self.leave_accrual_rule_accrual_type.value

        leave_accrual_rule_cap_type: Union[Unset, str] = UNSET
        if not isinstance(self.leave_accrual_rule_cap_type, Unset):
            leave_accrual_rule_cap_type = self.leave_accrual_rule_cap_type.value

        leave_accrual_rule_unit_cap = self.leave_accrual_rule_unit_cap

        leave_accrual_rule_carry_over_behaviour: Union[Unset, str] = UNSET
        if not isinstance(self.leave_accrual_rule_carry_over_behaviour, Unset):
            leave_accrual_rule_carry_over_behaviour = self.leave_accrual_rule_carry_over_behaviour.value

        leave_accrual_rule_carry_over_amount = self.leave_accrual_rule_carry_over_amount

        leave_accrual_rule_accrue_in_advance = self.leave_accrual_rule_accrue_in_advance

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if leave_loading is not UNSET:
            field_dict["leaveLoading"] = leave_loading
        if contingent_period is not UNSET:
            field_dict["contingentPeriod"] = contingent_period
        if entitlement_period is not UNSET:
            field_dict["entitlementPeriod"] = entitlement_period
        if unit_type is not UNSET:
            field_dict["unitType"] = unit_type
        if leave_unit_type is not UNSET:
            field_dict["leaveUnitType"] = leave_unit_type
        if accrual_rule_leave_year_offset_amount is not UNSET:
            field_dict["accrualRuleLeaveYearOffsetAmount"] = accrual_rule_leave_year_offset_amount
        if leave_category_id is not UNSET:
            field_dict["leaveCategoryId"] = leave_category_id
        if leave_category_name is not UNSET:
            field_dict["leaveCategoryName"] = leave_category_name
        if units is not UNSET:
            field_dict["units"] = units
        if can_apply_for_leave is not UNSET:
            field_dict["canApplyForLeave"] = can_apply_for_leave
        if leave_accrual_rule_accrual_type is not UNSET:
            field_dict["leaveAccrualRuleAccrualType"] = leave_accrual_rule_accrual_type
        if leave_accrual_rule_cap_type is not UNSET:
            field_dict["leaveAccrualRuleCapType"] = leave_accrual_rule_cap_type
        if leave_accrual_rule_unit_cap is not UNSET:
            field_dict["leaveAccrualRuleUnitCap"] = leave_accrual_rule_unit_cap
        if leave_accrual_rule_carry_over_behaviour is not UNSET:
            field_dict["leaveAccrualRuleCarryOverBehaviour"] = leave_accrual_rule_carry_over_behaviour
        if leave_accrual_rule_carry_over_amount is not UNSET:
            field_dict["leaveAccrualRuleCarryOverAmount"] = leave_accrual_rule_carry_over_amount
        if leave_accrual_rule_accrue_in_advance is not UNSET:
            field_dict["leaveAccrualRuleAccrueInAdvance"] = leave_accrual_rule_accrue_in_advance

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        leave_loading = d.pop("leaveLoading", UNSET)

        contingent_period = d.pop("contingentPeriod", UNSET)

        entitlement_period = d.pop("entitlementPeriod", UNSET)

        _unit_type = d.pop("unitType", UNSET)
        unit_type: Union[Unset, AuLeaveAllowanceTemplateLeaveCategoryApiModelNullableLeaveAllowanceUnitEnum]
        if isinstance(_unit_type, Unset):
            unit_type = UNSET
        else:
            unit_type = AuLeaveAllowanceTemplateLeaveCategoryApiModelNullableLeaveAllowanceUnitEnum(_unit_type)

        _leave_unit_type = d.pop("leaveUnitType", UNSET)
        leave_unit_type: Union[Unset, AuLeaveAllowanceTemplateLeaveCategoryApiModelNullableLeaveUnitTypeEnum]
        if isinstance(_leave_unit_type, Unset):
            leave_unit_type = UNSET
        else:
            leave_unit_type = AuLeaveAllowanceTemplateLeaveCategoryApiModelNullableLeaveUnitTypeEnum(_leave_unit_type)

        accrual_rule_leave_year_offset_amount = d.pop("accrualRuleLeaveYearOffsetAmount", UNSET)

        leave_category_id = d.pop("leaveCategoryId", UNSET)

        leave_category_name = d.pop("leaveCategoryName", UNSET)

        units = d.pop("units", UNSET)

        can_apply_for_leave = d.pop("canApplyForLeave", UNSET)

        _leave_accrual_rule_accrual_type = d.pop("leaveAccrualRuleAccrualType", UNSET)
        leave_accrual_rule_accrual_type: Union[Unset, AuLeaveAllowanceTemplateLeaveCategoryApiModelLeaveAccrualType]
        if isinstance(_leave_accrual_rule_accrual_type, Unset):
            leave_accrual_rule_accrual_type = UNSET
        else:
            leave_accrual_rule_accrual_type = AuLeaveAllowanceTemplateLeaveCategoryApiModelLeaveAccrualType(
                _leave_accrual_rule_accrual_type
            )

        _leave_accrual_rule_cap_type = d.pop("leaveAccrualRuleCapType", UNSET)
        leave_accrual_rule_cap_type: Union[Unset, AuLeaveAllowanceTemplateLeaveCategoryApiModelLeaveAccrualCapType]
        if isinstance(_leave_accrual_rule_cap_type, Unset):
            leave_accrual_rule_cap_type = UNSET
        else:
            leave_accrual_rule_cap_type = AuLeaveAllowanceTemplateLeaveCategoryApiModelLeaveAccrualCapType(
                _leave_accrual_rule_cap_type
            )

        leave_accrual_rule_unit_cap = d.pop("leaveAccrualRuleUnitCap", UNSET)

        _leave_accrual_rule_carry_over_behaviour = d.pop("leaveAccrualRuleCarryOverBehaviour", UNSET)
        leave_accrual_rule_carry_over_behaviour: Union[
            Unset, AuLeaveAllowanceTemplateLeaveCategoryApiModelLeaveAccrualCarryOverBehaviour
        ]
        if isinstance(_leave_accrual_rule_carry_over_behaviour, Unset):
            leave_accrual_rule_carry_over_behaviour = UNSET
        else:
            leave_accrual_rule_carry_over_behaviour = (
                AuLeaveAllowanceTemplateLeaveCategoryApiModelLeaveAccrualCarryOverBehaviour(
                    _leave_accrual_rule_carry_over_behaviour
                )
            )

        leave_accrual_rule_carry_over_amount = d.pop("leaveAccrualRuleCarryOverAmount", UNSET)

        leave_accrual_rule_accrue_in_advance = d.pop("leaveAccrualRuleAccrueInAdvance", UNSET)

        au_leave_allowance_template_leave_category_api_model = cls(
            leave_loading=leave_loading,
            contingent_period=contingent_period,
            entitlement_period=entitlement_period,
            unit_type=unit_type,
            leave_unit_type=leave_unit_type,
            accrual_rule_leave_year_offset_amount=accrual_rule_leave_year_offset_amount,
            leave_category_id=leave_category_id,
            leave_category_name=leave_category_name,
            units=units,
            can_apply_for_leave=can_apply_for_leave,
            leave_accrual_rule_accrual_type=leave_accrual_rule_accrual_type,
            leave_accrual_rule_cap_type=leave_accrual_rule_cap_type,
            leave_accrual_rule_unit_cap=leave_accrual_rule_unit_cap,
            leave_accrual_rule_carry_over_behaviour=leave_accrual_rule_carry_over_behaviour,
            leave_accrual_rule_carry_over_amount=leave_accrual_rule_carry_over_amount,
            leave_accrual_rule_accrue_in_advance=leave_accrual_rule_accrue_in_advance,
        )

        au_leave_allowance_template_leave_category_api_model.additional_properties = d
        return au_leave_allowance_template_leave_category_api_model

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
