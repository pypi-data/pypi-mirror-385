from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ILeaveBasedRosterShift")


@_attrs_define
class ILeaveBasedRosterShift:
    """
    Attributes:
        is_leave_based_roster_shift (Union[Unset, bool]):
    """

    is_leave_based_roster_shift: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        is_leave_based_roster_shift = self.is_leave_based_roster_shift

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if is_leave_based_roster_shift is not UNSET:
            field_dict["isLeaveBasedRosterShift"] = is_leave_based_roster_shift

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        is_leave_based_roster_shift = d.pop("isLeaveBasedRosterShift", UNSET)

        i_leave_based_roster_shift = cls(
            is_leave_based_roster_shift=is_leave_based_roster_shift,
        )

        i_leave_based_roster_shift.additional_properties = d
        return i_leave_based_roster_shift

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
