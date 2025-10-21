from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.i_edm_type_reference import IEdmTypeReference


T = TypeVar("T", bound="RangeVariable")


@_attrs_define
class RangeVariable:
    """
    Attributes:
        name (Union[Unset, str]):
        type_reference (Union[Unset, IEdmTypeReference]):
        kind (Union[Unset, int]):
    """

    name: Union[Unset, str] = UNSET
    type_reference: Union[Unset, "IEdmTypeReference"] = UNSET
    kind: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name

        type_reference: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.type_reference, Unset):
            type_reference = self.type_reference.to_dict()

        kind = self.kind

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if type_reference is not UNSET:
            field_dict["typeReference"] = type_reference
        if kind is not UNSET:
            field_dict["kind"] = kind

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.i_edm_type_reference import IEdmTypeReference

        d = src_dict.copy()
        name = d.pop("name", UNSET)

        _type_reference = d.pop("typeReference", UNSET)
        type_reference: Union[Unset, IEdmTypeReference]
        if isinstance(_type_reference, Unset):
            type_reference = UNSET
        else:
            type_reference = IEdmTypeReference.from_dict(_type_reference)

        kind = d.pop("kind", UNSET)

        range_variable = cls(
            name=name,
            type_reference=type_reference,
            kind=kind,
        )

        range_variable.additional_properties = d
        return range_variable

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
