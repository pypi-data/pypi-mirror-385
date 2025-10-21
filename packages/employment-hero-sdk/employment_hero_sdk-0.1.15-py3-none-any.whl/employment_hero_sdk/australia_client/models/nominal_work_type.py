from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.nominal_work_type_work_type_link_type_restriction import NominalWorkTypeWorkTypeLinkTypeRestriction
from ..types import UNSET, Unset

T = TypeVar("T", bound="NominalWorkType")


@_attrs_define
class NominalWorkType:
    """
    Attributes:
        id (Union[Unset, int]):
        name (Union[Unset, str]):
        link_type (Union[Unset, NominalWorkTypeWorkTypeLinkTypeRestriction]):
    """

    id: Union[Unset, int] = UNSET
    name: Union[Unset, str] = UNSET
    link_type: Union[Unset, NominalWorkTypeWorkTypeLinkTypeRestriction] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        name = self.name

        link_type: Union[Unset, str] = UNSET
        if not isinstance(self.link_type, Unset):
            link_type = self.link_type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if link_type is not UNSET:
            field_dict["linkType"] = link_type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        _link_type = d.pop("linkType", UNSET)
        link_type: Union[Unset, NominalWorkTypeWorkTypeLinkTypeRestriction]
        if isinstance(_link_type, Unset):
            link_type = UNSET
        else:
            link_type = NominalWorkTypeWorkTypeLinkTypeRestriction(_link_type)

        nominal_work_type = cls(
            id=id,
            name=name,
            link_type=link_type,
        )

        nominal_work_type.additional_properties = d
        return nominal_work_type

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
