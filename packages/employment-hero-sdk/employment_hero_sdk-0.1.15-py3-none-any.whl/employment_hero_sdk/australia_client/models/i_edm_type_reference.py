from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.i_edm_type import IEdmType


T = TypeVar("T", bound="IEdmTypeReference")


@_attrs_define
class IEdmTypeReference:
    """
    Attributes:
        is_nullable (Union[Unset, bool]):
        definition (Union[Unset, IEdmType]):
    """

    is_nullable: Union[Unset, bool] = UNSET
    definition: Union[Unset, "IEdmType"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        is_nullable = self.is_nullable

        definition: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.definition, Unset):
            definition = self.definition.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if is_nullable is not UNSET:
            field_dict["isNullable"] = is_nullable
        if definition is not UNSET:
            field_dict["definition"] = definition

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.i_edm_type import IEdmType

        d = src_dict.copy()
        is_nullable = d.pop("isNullable", UNSET)

        _definition = d.pop("definition", UNSET)
        definition: Union[Unset, IEdmType]
        if isinstance(_definition, Unset):
            definition = UNSET
        else:
            definition = IEdmType.from_dict(_definition)

        i_edm_type_reference = cls(
            is_nullable=is_nullable,
            definition=definition,
        )

        i_edm_type_reference.additional_properties = d
        return i_edm_type_reference

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
