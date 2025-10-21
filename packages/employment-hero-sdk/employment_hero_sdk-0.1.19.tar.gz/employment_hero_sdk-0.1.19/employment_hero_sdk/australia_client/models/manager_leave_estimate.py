from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.unit_and_hour_leave_estimate_model import UnitAndHourLeaveEstimateModel


T = TypeVar("T", bound="ManagerLeaveEstimate")


@_attrs_define
class ManagerLeaveEstimate:
    """
    Attributes:
        leave_balance (Union[Unset, float]):
        approved_leave (Union[Unset, float]):
        available_balance (Union[Unset, float]):
        leave_required (Union[Unset, UnitAndHourLeaveEstimateModel]):
    """

    leave_balance: Union[Unset, float] = UNSET
    approved_leave: Union[Unset, float] = UNSET
    available_balance: Union[Unset, float] = UNSET
    leave_required: Union[Unset, "UnitAndHourLeaveEstimateModel"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        leave_balance = self.leave_balance

        approved_leave = self.approved_leave

        available_balance = self.available_balance

        leave_required: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.leave_required, Unset):
            leave_required = self.leave_required.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if leave_balance is not UNSET:
            field_dict["leaveBalance"] = leave_balance
        if approved_leave is not UNSET:
            field_dict["approvedLeave"] = approved_leave
        if available_balance is not UNSET:
            field_dict["availableBalance"] = available_balance
        if leave_required is not UNSET:
            field_dict["leaveRequired"] = leave_required

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.unit_and_hour_leave_estimate_model import UnitAndHourLeaveEstimateModel

        d = src_dict.copy()
        leave_balance = d.pop("leaveBalance", UNSET)

        approved_leave = d.pop("approvedLeave", UNSET)

        available_balance = d.pop("availableBalance", UNSET)

        _leave_required = d.pop("leaveRequired", UNSET)
        leave_required: Union[Unset, UnitAndHourLeaveEstimateModel]
        if isinstance(_leave_required, Unset):
            leave_required = UNSET
        else:
            leave_required = UnitAndHourLeaveEstimateModel.from_dict(_leave_required)

        manager_leave_estimate = cls(
            leave_balance=leave_balance,
            approved_leave=approved_leave,
            available_balance=available_balance,
            leave_required=leave_required,
        )

        manager_leave_estimate.additional_properties = d
        return manager_leave_estimate

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
