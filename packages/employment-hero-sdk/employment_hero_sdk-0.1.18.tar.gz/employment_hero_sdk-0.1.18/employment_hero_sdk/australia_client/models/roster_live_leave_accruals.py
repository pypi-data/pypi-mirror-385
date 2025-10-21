from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="RosterLiveLeaveAccruals")


@_attrs_define
class RosterLiveLeaveAccruals:
    """
    Attributes:
        reference_number (Union[Unset, str]):
        leave_code (Union[Unset, str]):
        balance (Union[Unset, float]):
    """

    reference_number: Union[Unset, str] = UNSET
    leave_code: Union[Unset, str] = UNSET
    balance: Union[Unset, float] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        reference_number = self.reference_number

        leave_code = self.leave_code

        balance = self.balance

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if reference_number is not UNSET:
            field_dict["referenceNumber"] = reference_number
        if leave_code is not UNSET:
            field_dict["leaveCode"] = leave_code
        if balance is not UNSET:
            field_dict["balance"] = balance

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        reference_number = d.pop("referenceNumber", UNSET)

        leave_code = d.pop("leaveCode", UNSET)

        balance = d.pop("balance", UNSET)

        roster_live_leave_accruals = cls(
            reference_number=reference_number,
            leave_code=leave_code,
            balance=balance,
        )

        roster_live_leave_accruals.additional_properties = d
        return roster_live_leave_accruals

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
