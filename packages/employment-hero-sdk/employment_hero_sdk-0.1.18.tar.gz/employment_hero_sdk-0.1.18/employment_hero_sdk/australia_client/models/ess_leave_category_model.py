from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.ess_leave_category_model_leave_unit_type_enum import EssLeaveCategoryModelLeaveUnitTypeEnum
from ..types import UNSET, Unset

T = TypeVar("T", bound="EssLeaveCategoryModel")


@_attrs_define
class EssLeaveCategoryModel:
    """
    Attributes:
        unit_type (Union[Unset, EssLeaveCategoryModelLeaveUnitTypeEnum]):
        id (Union[Unset, int]):
        name (Union[Unset, str]):
    """

    unit_type: Union[Unset, EssLeaveCategoryModelLeaveUnitTypeEnum] = UNSET
    id: Union[Unset, int] = UNSET
    name: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        unit_type: Union[Unset, str] = UNSET
        if not isinstance(self.unit_type, Unset):
            unit_type = self.unit_type.value

        id = self.id

        name = self.name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if unit_type is not UNSET:
            field_dict["unitType"] = unit_type
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _unit_type = d.pop("unitType", UNSET)
        unit_type: Union[Unset, EssLeaveCategoryModelLeaveUnitTypeEnum]
        if isinstance(_unit_type, Unset):
            unit_type = UNSET
        else:
            unit_type = EssLeaveCategoryModelLeaveUnitTypeEnum(_unit_type)

        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        ess_leave_category_model = cls(
            unit_type=unit_type,
            id=id,
            name=name,
        )

        ess_leave_category_model.additional_properties = d
        return ess_leave_category_model

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
