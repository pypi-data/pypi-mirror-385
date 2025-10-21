from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ShiftConditionSelectModel")


@_attrs_define
class ShiftConditionSelectModel:
    """
    Attributes:
        short_code (Union[Unset, str]):
        business_award_package_id (Union[Unset, int]):
        id (Union[Unset, int]):
        description (Union[Unset, str]):
    """

    short_code: Union[Unset, str] = UNSET
    business_award_package_id: Union[Unset, int] = UNSET
    id: Union[Unset, int] = UNSET
    description: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        short_code = self.short_code

        business_award_package_id = self.business_award_package_id

        id = self.id

        description = self.description

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if short_code is not UNSET:
            field_dict["shortCode"] = short_code
        if business_award_package_id is not UNSET:
            field_dict["businessAwardPackageId"] = business_award_package_id
        if id is not UNSET:
            field_dict["id"] = id
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        short_code = d.pop("shortCode", UNSET)

        business_award_package_id = d.pop("businessAwardPackageId", UNSET)

        id = d.pop("id", UNSET)

        description = d.pop("description", UNSET)

        shift_condition_select_model = cls(
            short_code=short_code,
            business_award_package_id=business_award_package_id,
            id=id,
            description=description,
        )

        shift_condition_select_model.additional_properties = d
        return shift_condition_select_model

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
