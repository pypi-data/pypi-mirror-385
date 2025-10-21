from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="LocationShiftConditionsModel")


@_attrs_define
class LocationShiftConditionsModel:
    """
    Attributes:
        location_id (Union[Unset, int]):
        shift_condition_ids (Union[Unset, List[int]]):
    """

    location_id: Union[Unset, int] = UNSET
    shift_condition_ids: Union[Unset, List[int]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        location_id = self.location_id

        shift_condition_ids: Union[Unset, List[int]] = UNSET
        if not isinstance(self.shift_condition_ids, Unset):
            shift_condition_ids = self.shift_condition_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if location_id is not UNSET:
            field_dict["locationId"] = location_id
        if shift_condition_ids is not UNSET:
            field_dict["shiftConditionIds"] = shift_condition_ids

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        location_id = d.pop("locationId", UNSET)

        shift_condition_ids = cast(List[int], d.pop("shiftConditionIds", UNSET))

        location_shift_conditions_model = cls(
            location_id=location_id,
            shift_condition_ids=shift_condition_ids,
        )

        location_shift_conditions_model.additional_properties = d
        return location_shift_conditions_model

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
