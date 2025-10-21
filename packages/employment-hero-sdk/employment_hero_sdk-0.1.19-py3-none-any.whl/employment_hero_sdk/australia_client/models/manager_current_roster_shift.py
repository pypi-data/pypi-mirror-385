from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.manager_current_roster_shift_time_attendance_status import ManagerCurrentRosterShiftTimeAttendanceStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="ManagerCurrentRosterShift")


@_attrs_define
class ManagerCurrentRosterShift:
    """
    Attributes:
        status (Union[Unset, ManagerCurrentRosterShiftTimeAttendanceStatus]):
        is_late (Union[Unset, bool]):
        is_not_clocked_off (Union[Unset, bool]):
    """

    status: Union[Unset, ManagerCurrentRosterShiftTimeAttendanceStatus] = UNSET
    is_late: Union[Unset, bool] = UNSET
    is_not_clocked_off: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        is_late = self.is_late

        is_not_clocked_off = self.is_not_clocked_off

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if status is not UNSET:
            field_dict["status"] = status
        if is_late is not UNSET:
            field_dict["isLate"] = is_late
        if is_not_clocked_off is not UNSET:
            field_dict["isNotClockedOff"] = is_not_clocked_off

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _status = d.pop("status", UNSET)
        status: Union[Unset, ManagerCurrentRosterShiftTimeAttendanceStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = ManagerCurrentRosterShiftTimeAttendanceStatus(_status)

        is_late = d.pop("isLate", UNSET)

        is_not_clocked_off = d.pop("isNotClockedOff", UNSET)

        manager_current_roster_shift = cls(
            status=status,
            is_late=is_late,
            is_not_clocked_off=is_not_clocked_off,
        )

        manager_current_roster_shift.additional_properties = d
        return manager_current_roster_shift

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
