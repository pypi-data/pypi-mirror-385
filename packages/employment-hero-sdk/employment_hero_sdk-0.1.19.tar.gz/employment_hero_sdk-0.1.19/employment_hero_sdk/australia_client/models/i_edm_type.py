from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.i_edm_type_edm_type_kind import IEdmTypeEdmTypeKind
from ..types import UNSET, Unset

T = TypeVar("T", bound="IEdmType")


@_attrs_define
class IEdmType:
    """
    Attributes:
        type_kind (Union[Unset, IEdmTypeEdmTypeKind]):
    """

    type_kind: Union[Unset, IEdmTypeEdmTypeKind] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        type_kind: Union[Unset, str] = UNSET
        if not isinstance(self.type_kind, Unset):
            type_kind = self.type_kind.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if type_kind is not UNSET:
            field_dict["typeKind"] = type_kind

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _type_kind = d.pop("typeKind", UNSET)
        type_kind: Union[Unset, IEdmTypeEdmTypeKind]
        if isinstance(_type_kind, Unset):
            type_kind = UNSET
        else:
            type_kind = IEdmTypeEdmTypeKind(_type_kind)

        i_edm_type = cls(
            type_kind=type_kind,
        )

        i_edm_type.additional_properties = d
        return i_edm_type

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
