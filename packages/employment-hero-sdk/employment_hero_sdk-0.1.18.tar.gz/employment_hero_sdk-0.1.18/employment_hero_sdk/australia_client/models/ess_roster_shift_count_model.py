from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="EssRosterShiftCountModel")


@_attrs_define
class EssRosterShiftCountModel:
    """
    Attributes:
        proposed_swap_count (Union[Unset, int]):
        pending_shift_count (Union[Unset, int]):
        biddable_shift_count (Union[Unset, int]):
        not_accepted_shifts_count (Union[Unset, int]):
    """

    proposed_swap_count: Union[Unset, int] = UNSET
    pending_shift_count: Union[Unset, int] = UNSET
    biddable_shift_count: Union[Unset, int] = UNSET
    not_accepted_shifts_count: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        proposed_swap_count = self.proposed_swap_count

        pending_shift_count = self.pending_shift_count

        biddable_shift_count = self.biddable_shift_count

        not_accepted_shifts_count = self.not_accepted_shifts_count

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if proposed_swap_count is not UNSET:
            field_dict["proposedSwapCount"] = proposed_swap_count
        if pending_shift_count is not UNSET:
            field_dict["pendingShiftCount"] = pending_shift_count
        if biddable_shift_count is not UNSET:
            field_dict["biddableShiftCount"] = biddable_shift_count
        if not_accepted_shifts_count is not UNSET:
            field_dict["notAcceptedShiftsCount"] = not_accepted_shifts_count

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        proposed_swap_count = d.pop("proposedSwapCount", UNSET)

        pending_shift_count = d.pop("pendingShiftCount", UNSET)

        biddable_shift_count = d.pop("biddableShiftCount", UNSET)

        not_accepted_shifts_count = d.pop("notAcceptedShiftsCount", UNSET)

        ess_roster_shift_count_model = cls(
            proposed_swap_count=proposed_swap_count,
            pending_shift_count=pending_shift_count,
            biddable_shift_count=biddable_shift_count,
            not_accepted_shifts_count=not_accepted_shifts_count,
        )

        ess_roster_shift_count_model.additional_properties = d
        return ess_roster_shift_count_model

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
