from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.leave_entitlement_model_leave_entitlement_accrual_unit_type import (
    LeaveEntitlementModelLeaveEntitlementAccrualUnitType,
)
from ..models.leave_entitlement_model_leave_entitlement_carry_over_type import (
    LeaveEntitlementModelLeaveEntitlementCarryOverType,
)
from ..models.leave_entitlement_model_leave_entitlement_forfeiture_type import (
    LeaveEntitlementModelLeaveEntitlementForfeitureType,
)
from ..models.leave_entitlement_model_leave_entitlement_leave_balance_type import (
    LeaveEntitlementModelLeaveEntitlementLeaveBalanceType,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.leave_entitlement_tier_model import LeaveEntitlementTierModel


T = TypeVar("T", bound="LeaveEntitlementModel")


@_attrs_define
class LeaveEntitlementModel:
    """
    Attributes:
        id (Union[Unset, int]):
        carry_over_type (Union[Unset, LeaveEntitlementModelLeaveEntitlementCarryOverType]):
        carry_over_amount (Union[Unset, float]):
        is_pro_rata (Union[Unset, bool]):
        leave_balance_type (Union[Unset, LeaveEntitlementModelLeaveEntitlementLeaveBalanceType]):
        leave_entitlement_tiers (Union[Unset, List['LeaveEntitlementTierModel']]):
        forfeiture_type (Union[Unset, LeaveEntitlementModelLeaveEntitlementForfeitureType]):
        forfeiture_amount (Union[Unset, float]):
        forfeiture_months_start_after (Union[Unset, int]):
        standard_allowance_unit_type_amount (Union[Unset, float]):
        standard_allowance_unit_type (Union[Unset, LeaveEntitlementModelLeaveEntitlementAccrualUnitType]):
    """

    id: Union[Unset, int] = UNSET
    carry_over_type: Union[Unset, LeaveEntitlementModelLeaveEntitlementCarryOverType] = UNSET
    carry_over_amount: Union[Unset, float] = UNSET
    is_pro_rata: Union[Unset, bool] = UNSET
    leave_balance_type: Union[Unset, LeaveEntitlementModelLeaveEntitlementLeaveBalanceType] = UNSET
    leave_entitlement_tiers: Union[Unset, List["LeaveEntitlementTierModel"]] = UNSET
    forfeiture_type: Union[Unset, LeaveEntitlementModelLeaveEntitlementForfeitureType] = UNSET
    forfeiture_amount: Union[Unset, float] = UNSET
    forfeiture_months_start_after: Union[Unset, int] = UNSET
    standard_allowance_unit_type_amount: Union[Unset, float] = UNSET
    standard_allowance_unit_type: Union[Unset, LeaveEntitlementModelLeaveEntitlementAccrualUnitType] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        carry_over_type: Union[Unset, str] = UNSET
        if not isinstance(self.carry_over_type, Unset):
            carry_over_type = self.carry_over_type.value

        carry_over_amount = self.carry_over_amount

        is_pro_rata = self.is_pro_rata

        leave_balance_type: Union[Unset, str] = UNSET
        if not isinstance(self.leave_balance_type, Unset):
            leave_balance_type = self.leave_balance_type.value

        leave_entitlement_tiers: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.leave_entitlement_tiers, Unset):
            leave_entitlement_tiers = []
            for leave_entitlement_tiers_item_data in self.leave_entitlement_tiers:
                leave_entitlement_tiers_item = leave_entitlement_tiers_item_data.to_dict()
                leave_entitlement_tiers.append(leave_entitlement_tiers_item)

        forfeiture_type: Union[Unset, str] = UNSET
        if not isinstance(self.forfeiture_type, Unset):
            forfeiture_type = self.forfeiture_type.value

        forfeiture_amount = self.forfeiture_amount

        forfeiture_months_start_after = self.forfeiture_months_start_after

        standard_allowance_unit_type_amount = self.standard_allowance_unit_type_amount

        standard_allowance_unit_type: Union[Unset, str] = UNSET
        if not isinstance(self.standard_allowance_unit_type, Unset):
            standard_allowance_unit_type = self.standard_allowance_unit_type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if carry_over_type is not UNSET:
            field_dict["carryOverType"] = carry_over_type
        if carry_over_amount is not UNSET:
            field_dict["carryOverAmount"] = carry_over_amount
        if is_pro_rata is not UNSET:
            field_dict["isProRata"] = is_pro_rata
        if leave_balance_type is not UNSET:
            field_dict["leaveBalanceType"] = leave_balance_type
        if leave_entitlement_tiers is not UNSET:
            field_dict["leaveEntitlementTiers"] = leave_entitlement_tiers
        if forfeiture_type is not UNSET:
            field_dict["forfeitureType"] = forfeiture_type
        if forfeiture_amount is not UNSET:
            field_dict["forfeitureAmount"] = forfeiture_amount
        if forfeiture_months_start_after is not UNSET:
            field_dict["forfeitureMonthsStartAfter"] = forfeiture_months_start_after
        if standard_allowance_unit_type_amount is not UNSET:
            field_dict["standardAllowanceUnitTypeAmount"] = standard_allowance_unit_type_amount
        if standard_allowance_unit_type is not UNSET:
            field_dict["standardAllowanceUnitType"] = standard_allowance_unit_type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.leave_entitlement_tier_model import LeaveEntitlementTierModel

        d = src_dict.copy()
        id = d.pop("id", UNSET)

        _carry_over_type = d.pop("carryOverType", UNSET)
        carry_over_type: Union[Unset, LeaveEntitlementModelLeaveEntitlementCarryOverType]
        if isinstance(_carry_over_type, Unset):
            carry_over_type = UNSET
        else:
            carry_over_type = LeaveEntitlementModelLeaveEntitlementCarryOverType(_carry_over_type)

        carry_over_amount = d.pop("carryOverAmount", UNSET)

        is_pro_rata = d.pop("isProRata", UNSET)

        _leave_balance_type = d.pop("leaveBalanceType", UNSET)
        leave_balance_type: Union[Unset, LeaveEntitlementModelLeaveEntitlementLeaveBalanceType]
        if isinstance(_leave_balance_type, Unset):
            leave_balance_type = UNSET
        else:
            leave_balance_type = LeaveEntitlementModelLeaveEntitlementLeaveBalanceType(_leave_balance_type)

        leave_entitlement_tiers = []
        _leave_entitlement_tiers = d.pop("leaveEntitlementTiers", UNSET)
        for leave_entitlement_tiers_item_data in _leave_entitlement_tiers or []:
            leave_entitlement_tiers_item = LeaveEntitlementTierModel.from_dict(leave_entitlement_tiers_item_data)

            leave_entitlement_tiers.append(leave_entitlement_tiers_item)

        _forfeiture_type = d.pop("forfeitureType", UNSET)
        forfeiture_type: Union[Unset, LeaveEntitlementModelLeaveEntitlementForfeitureType]
        if isinstance(_forfeiture_type, Unset):
            forfeiture_type = UNSET
        else:
            forfeiture_type = LeaveEntitlementModelLeaveEntitlementForfeitureType(_forfeiture_type)

        forfeiture_amount = d.pop("forfeitureAmount", UNSET)

        forfeiture_months_start_after = d.pop("forfeitureMonthsStartAfter", UNSET)

        standard_allowance_unit_type_amount = d.pop("standardAllowanceUnitTypeAmount", UNSET)

        _standard_allowance_unit_type = d.pop("standardAllowanceUnitType", UNSET)
        standard_allowance_unit_type: Union[Unset, LeaveEntitlementModelLeaveEntitlementAccrualUnitType]
        if isinstance(_standard_allowance_unit_type, Unset):
            standard_allowance_unit_type = UNSET
        else:
            standard_allowance_unit_type = LeaveEntitlementModelLeaveEntitlementAccrualUnitType(
                _standard_allowance_unit_type
            )

        leave_entitlement_model = cls(
            id=id,
            carry_over_type=carry_over_type,
            carry_over_amount=carry_over_amount,
            is_pro_rata=is_pro_rata,
            leave_balance_type=leave_balance_type,
            leave_entitlement_tiers=leave_entitlement_tiers,
            forfeiture_type=forfeiture_type,
            forfeiture_amount=forfeiture_amount,
            forfeiture_months_start_after=forfeiture_months_start_after,
            standard_allowance_unit_type_amount=standard_allowance_unit_type_amount,
            standard_allowance_unit_type=standard_allowance_unit_type,
        )

        leave_entitlement_model.additional_properties = d
        return leave_entitlement_model

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
