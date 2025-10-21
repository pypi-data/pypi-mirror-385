from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.au_ess_roster_shift_model import AuEssRosterShiftModel


T = TypeVar("T", bound="AuRosterShiftMatchingResultModel")


@_attrs_define
class AuRosterShiftMatchingResultModel:
    """
    Attributes:
        shift (Union[Unset, AuEssRosterShiftModel]):
    """

    shift: Union[Unset, "AuEssRosterShiftModel"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        shift: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.shift, Unset):
            shift = self.shift.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if shift is not UNSET:
            field_dict["shift"] = shift

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

        au_roster_shift_matching_result_model = cls(
            shift=shift,
        )

        au_roster_shift_matching_result_model.additional_properties = d
        return au_roster_shift_matching_result_model

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
