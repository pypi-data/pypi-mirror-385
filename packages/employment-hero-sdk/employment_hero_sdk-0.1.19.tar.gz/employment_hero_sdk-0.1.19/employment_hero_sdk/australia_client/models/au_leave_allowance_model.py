from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.au_leave_accrual_rule_model import AuLeaveAccrualRuleModel


T = TypeVar("T", bound="AuLeaveAllowanceModel")


@_attrs_define
class AuLeaveAllowanceModel:
    """
    Attributes:
        leave_loading (Union[Unset, float]):
        leave_accrual_rule (Union[Unset, AuLeaveAccrualRuleModel]):
        leave_category_id (Union[Unset, str]):
        leave_category_name (Union[Unset, str]):
        units (Union[Unset, float]):
        unit_type (Union[Unset, str]):
        leave_unit_type (Union[Unset, str]):
        hours_per_year (Union[Unset, float]):
        automatically_accrues (Union[Unset, bool]):
        can_apply_for_leave (Union[Unset, bool]):
    """

    leave_loading: Union[Unset, float] = UNSET
    leave_accrual_rule: Union[Unset, "AuLeaveAccrualRuleModel"] = UNSET
    leave_category_id: Union[Unset, str] = UNSET
    leave_category_name: Union[Unset, str] = UNSET
    units: Union[Unset, float] = UNSET
    unit_type: Union[Unset, str] = UNSET
    leave_unit_type: Union[Unset, str] = UNSET
    hours_per_year: Union[Unset, float] = UNSET
    automatically_accrues: Union[Unset, bool] = UNSET
    can_apply_for_leave: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        leave_loading = self.leave_loading

        leave_accrual_rule: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.leave_accrual_rule, Unset):
            leave_accrual_rule = self.leave_accrual_rule.to_dict()

        leave_category_id = self.leave_category_id

        leave_category_name = self.leave_category_name

        units = self.units

        unit_type = self.unit_type

        leave_unit_type = self.leave_unit_type

        hours_per_year = self.hours_per_year

        automatically_accrues = self.automatically_accrues

        can_apply_for_leave = self.can_apply_for_leave

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if leave_loading is not UNSET:
            field_dict["leaveLoading"] = leave_loading
        if leave_accrual_rule is not UNSET:
            field_dict["leaveAccrualRule"] = leave_accrual_rule
        if leave_category_id is not UNSET:
            field_dict["leaveCategoryId"] = leave_category_id
        if leave_category_name is not UNSET:
            field_dict["leaveCategoryName"] = leave_category_name
        if units is not UNSET:
            field_dict["units"] = units
        if unit_type is not UNSET:
            field_dict["unitType"] = unit_type
        if leave_unit_type is not UNSET:
            field_dict["leaveUnitType"] = leave_unit_type
        if hours_per_year is not UNSET:
            field_dict["hoursPerYear"] = hours_per_year
        if automatically_accrues is not UNSET:
            field_dict["automaticallyAccrues"] = automatically_accrues
        if can_apply_for_leave is not UNSET:
            field_dict["canApplyForLeave"] = can_apply_for_leave

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.au_leave_accrual_rule_model import AuLeaveAccrualRuleModel

        d = src_dict.copy()
        leave_loading = d.pop("leaveLoading", UNSET)

        _leave_accrual_rule = d.pop("leaveAccrualRule", UNSET)
        leave_accrual_rule: Union[Unset, AuLeaveAccrualRuleModel]
        if isinstance(_leave_accrual_rule, Unset):
            leave_accrual_rule = UNSET
        else:
            leave_accrual_rule = AuLeaveAccrualRuleModel.from_dict(_leave_accrual_rule)

        leave_category_id = d.pop("leaveCategoryId", UNSET)

        leave_category_name = d.pop("leaveCategoryName", UNSET)

        units = d.pop("units", UNSET)

        unit_type = d.pop("unitType", UNSET)

        leave_unit_type = d.pop("leaveUnitType", UNSET)

        hours_per_year = d.pop("hoursPerYear", UNSET)

        automatically_accrues = d.pop("automaticallyAccrues", UNSET)

        can_apply_for_leave = d.pop("canApplyForLeave", UNSET)

        au_leave_allowance_model = cls(
            leave_loading=leave_loading,
            leave_accrual_rule=leave_accrual_rule,
            leave_category_id=leave_category_id,
            leave_category_name=leave_category_name,
            units=units,
            unit_type=unit_type,
            leave_unit_type=leave_unit_type,
            hours_per_year=hours_per_year,
            automatically_accrues=automatically_accrues,
            can_apply_for_leave=can_apply_for_leave,
        )

        au_leave_allowance_model.additional_properties = d
        return au_leave_allowance_model

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
