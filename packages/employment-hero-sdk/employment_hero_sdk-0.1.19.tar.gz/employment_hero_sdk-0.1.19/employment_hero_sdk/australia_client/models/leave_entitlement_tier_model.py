from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.leave_entitlement_tier_model_leave_entitlement_accrual_start_date_unit_type import (
    LeaveEntitlementTierModelLeaveEntitlementAccrualStartDateUnitType,
)
from ..models.leave_entitlement_tier_model_leave_entitlement_accrual_unit_type import (
    LeaveEntitlementTierModelLeaveEntitlementAccrualUnitType,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="LeaveEntitlementTierModel")


@_attrs_define
class LeaveEntitlementTierModel:
    """
    Attributes:
        id (Union[Unset, int]):
        accrual_start_after (Union[Unset, int]):
        accrual_start_after_unit_type (Union[Unset, LeaveEntitlementTierModelLeaveEntitlementAccrualStartDateUnitType]):
        accrual_amount (Union[Unset, float]):
        accrual_unit_type (Union[Unset, LeaveEntitlementTierModelLeaveEntitlementAccrualUnitType]):
        is_deleted (Union[Unset, bool]):
    """

    id: Union[Unset, int] = UNSET
    accrual_start_after: Union[Unset, int] = UNSET
    accrual_start_after_unit_type: Union[Unset, LeaveEntitlementTierModelLeaveEntitlementAccrualStartDateUnitType] = (
        UNSET
    )
    accrual_amount: Union[Unset, float] = UNSET
    accrual_unit_type: Union[Unset, LeaveEntitlementTierModelLeaveEntitlementAccrualUnitType] = UNSET
    is_deleted: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        accrual_start_after = self.accrual_start_after

        accrual_start_after_unit_type: Union[Unset, str] = UNSET
        if not isinstance(self.accrual_start_after_unit_type, Unset):
            accrual_start_after_unit_type = self.accrual_start_after_unit_type.value

        accrual_amount = self.accrual_amount

        accrual_unit_type: Union[Unset, str] = UNSET
        if not isinstance(self.accrual_unit_type, Unset):
            accrual_unit_type = self.accrual_unit_type.value

        is_deleted = self.is_deleted

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if accrual_start_after is not UNSET:
            field_dict["accrualStartAfter"] = accrual_start_after
        if accrual_start_after_unit_type is not UNSET:
            field_dict["accrualStartAfterUnitType"] = accrual_start_after_unit_type
        if accrual_amount is not UNSET:
            field_dict["accrualAmount"] = accrual_amount
        if accrual_unit_type is not UNSET:
            field_dict["accrualUnitType"] = accrual_unit_type
        if is_deleted is not UNSET:
            field_dict["isDeleted"] = is_deleted

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        accrual_start_after = d.pop("accrualStartAfter", UNSET)

        _accrual_start_after_unit_type = d.pop("accrualStartAfterUnitType", UNSET)
        accrual_start_after_unit_type: Union[Unset, LeaveEntitlementTierModelLeaveEntitlementAccrualStartDateUnitType]
        if isinstance(_accrual_start_after_unit_type, Unset):
            accrual_start_after_unit_type = UNSET
        else:
            accrual_start_after_unit_type = LeaveEntitlementTierModelLeaveEntitlementAccrualStartDateUnitType(
                _accrual_start_after_unit_type
            )

        accrual_amount = d.pop("accrualAmount", UNSET)

        _accrual_unit_type = d.pop("accrualUnitType", UNSET)
        accrual_unit_type: Union[Unset, LeaveEntitlementTierModelLeaveEntitlementAccrualUnitType]
        if isinstance(_accrual_unit_type, Unset):
            accrual_unit_type = UNSET
        else:
            accrual_unit_type = LeaveEntitlementTierModelLeaveEntitlementAccrualUnitType(_accrual_unit_type)

        is_deleted = d.pop("isDeleted", UNSET)

        leave_entitlement_tier_model = cls(
            id=id,
            accrual_start_after=accrual_start_after,
            accrual_start_after_unit_type=accrual_start_after_unit_type,
            accrual_amount=accrual_amount,
            accrual_unit_type=accrual_unit_type,
            is_deleted=is_deleted,
        )

        leave_entitlement_tier_model.additional_properties = d
        return leave_entitlement_tier_model

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
