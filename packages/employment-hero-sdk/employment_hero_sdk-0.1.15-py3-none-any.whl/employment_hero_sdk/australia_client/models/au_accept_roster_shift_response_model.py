from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.au_ess_roster_shift_model import AuEssRosterShiftModel


T = TypeVar("T", bound="AuAcceptRosterShiftResponseModel")


@_attrs_define
class AuAcceptRosterShiftResponseModel:
    """
    Attributes:
        shift (Union[Unset, AuEssRosterShiftModel]):
        proposed_swap_count (Union[Unset, int]):
        pending_shift_count (Union[Unset, int]):
        biddable_shift_count (Union[Unset, int]):
        not_accepted_shifts_count (Union[Unset, int]):
    """

    shift: Union[Unset, "AuEssRosterShiftModel"] = UNSET
    proposed_swap_count: Union[Unset, int] = UNSET
    pending_shift_count: Union[Unset, int] = UNSET
    biddable_shift_count: Union[Unset, int] = UNSET
    not_accepted_shifts_count: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        shift: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.shift, Unset):
            shift = self.shift.to_dict()

        proposed_swap_count = self.proposed_swap_count

        pending_shift_count = self.pending_shift_count

        biddable_shift_count = self.biddable_shift_count

        not_accepted_shifts_count = self.not_accepted_shifts_count

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if shift is not UNSET:
            field_dict["shift"] = shift
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
        from ..models.au_ess_roster_shift_model import AuEssRosterShiftModel

        d = src_dict.copy()
        _shift = d.pop("shift", UNSET)
        shift: Union[Unset, AuEssRosterShiftModel]
        if isinstance(_shift, Unset):
            shift = UNSET
        else:
            shift = AuEssRosterShiftModel.from_dict(_shift)

        proposed_swap_count = d.pop("proposedSwapCount", UNSET)

        pending_shift_count = d.pop("pendingShiftCount", UNSET)

        biddable_shift_count = d.pop("biddableShiftCount", UNSET)

        not_accepted_shifts_count = d.pop("notAcceptedShiftsCount", UNSET)

        au_accept_roster_shift_response_model = cls(
            shift=shift,
            proposed_swap_count=proposed_swap_count,
            pending_shift_count=pending_shift_count,
            biddable_shift_count=biddable_shift_count,
            not_accepted_shifts_count=not_accepted_shifts_count,
        )

        au_accept_roster_shift_response_model.additional_properties = d
        return au_accept_roster_shift_response_model

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
