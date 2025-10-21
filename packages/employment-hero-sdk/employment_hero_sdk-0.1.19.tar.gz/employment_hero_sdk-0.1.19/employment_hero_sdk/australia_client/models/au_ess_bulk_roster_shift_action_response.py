from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.au_ess_roster_shift_model import AuEssRosterShiftModel


T = TypeVar("T", bound="AuEssBulkRosterShiftActionResponse")


@_attrs_define
class AuEssBulkRosterShiftActionResponse:
    """
    Attributes:
        shifts (Union[Unset, List['AuEssRosterShiftModel']]):
        pending_shift_count (Union[Unset, int]):
        proposed_swap_count (Union[Unset, int]):
        not_accepted_shifts_count (Union[Unset, int]):
    """

    shifts: Union[Unset, List["AuEssRosterShiftModel"]] = UNSET
    pending_shift_count: Union[Unset, int] = UNSET
    proposed_swap_count: Union[Unset, int] = UNSET
    not_accepted_shifts_count: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        shifts: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.shifts, Unset):
            shifts = []
            for shifts_item_data in self.shifts:
                shifts_item = shifts_item_data.to_dict()
                shifts.append(shifts_item)

        pending_shift_count = self.pending_shift_count

        proposed_swap_count = self.proposed_swap_count

        not_accepted_shifts_count = self.not_accepted_shifts_count

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if shifts is not UNSET:
            field_dict["shifts"] = shifts
        if pending_shift_count is not UNSET:
            field_dict["pendingShiftCount"] = pending_shift_count
        if proposed_swap_count is not UNSET:
            field_dict["proposedSwapCount"] = proposed_swap_count
        if not_accepted_shifts_count is not UNSET:
            field_dict["notAcceptedShiftsCount"] = not_accepted_shifts_count

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.au_ess_roster_shift_model import AuEssRosterShiftModel

        d = src_dict.copy()
        shifts = []
        _shifts = d.pop("shifts", UNSET)
        for shifts_item_data in _shifts or []:
            shifts_item = AuEssRosterShiftModel.from_dict(shifts_item_data)

            shifts.append(shifts_item)

        pending_shift_count = d.pop("pendingShiftCount", UNSET)

        proposed_swap_count = d.pop("proposedSwapCount", UNSET)

        not_accepted_shifts_count = d.pop("notAcceptedShiftsCount", UNSET)

        au_ess_bulk_roster_shift_action_response = cls(
            shifts=shifts,
            pending_shift_count=pending_shift_count,
            proposed_swap_count=proposed_swap_count,
            not_accepted_shifts_count=not_accepted_shifts_count,
        )

        au_ess_bulk_roster_shift_action_response.additional_properties = d
        return au_ess_bulk_roster_shift_action_response

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
