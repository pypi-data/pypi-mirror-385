from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="EssBulkDeclineRosterShiftsModel")


@_attrs_define
class EssBulkDeclineRosterShiftsModel:
    """
    Attributes:
        reason (Union[Unset, str]):
        shifts (Union[Unset, List[int]]):
    """

    reason: Union[Unset, str] = UNSET
    shifts: Union[Unset, List[int]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        reason = self.reason

        shifts: Union[Unset, List[int]] = UNSET
        if not isinstance(self.shifts, Unset):
            shifts = self.shifts

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if reason is not UNSET:
            field_dict["reason"] = reason
        if shifts is not UNSET:
            field_dict["shifts"] = shifts

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        reason = d.pop("reason", UNSET)

        shifts = cast(List[int], d.pop("shifts", UNSET))

        ess_bulk_decline_roster_shifts_model = cls(
            reason=reason,
            shifts=shifts,
        )

        ess_bulk_decline_roster_shifts_model.additional_properties = d
        return ess_bulk_decline_roster_shifts_model

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
