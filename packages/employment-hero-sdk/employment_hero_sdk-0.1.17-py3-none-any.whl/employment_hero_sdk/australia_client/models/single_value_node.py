from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.single_value_node_query_node_kind import SingleValueNodeQueryNodeKind
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.i_edm_type_reference import IEdmTypeReference


T = TypeVar("T", bound="SingleValueNode")


@_attrs_define
class SingleValueNode:
    """
    Attributes:
        type_reference (Union[Unset, IEdmTypeReference]):
        kind (Union[Unset, SingleValueNodeQueryNodeKind]):
    """

    type_reference: Union[Unset, "IEdmTypeReference"] = UNSET
    kind: Union[Unset, SingleValueNodeQueryNodeKind] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        type_reference: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.type_reference, Unset):
            type_reference = self.type_reference.to_dict()

        kind: Union[Unset, str] = UNSET
        if not isinstance(self.kind, Unset):
            kind = self.kind.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if type_reference is not UNSET:
            field_dict["typeReference"] = type_reference
        if kind is not UNSET:
            field_dict["kind"] = kind

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.i_edm_type_reference import IEdmTypeReference

        d = src_dict.copy()
        _type_reference = d.pop("typeReference", UNSET)
        type_reference: Union[Unset, IEdmTypeReference]
        if isinstance(_type_reference, Unset):
            type_reference = UNSET
        else:
            type_reference = IEdmTypeReference.from_dict(_type_reference)

        _kind = d.pop("kind", UNSET)
        kind: Union[Unset, SingleValueNodeQueryNodeKind]
        if isinstance(_kind, Unset):
            kind = UNSET
        else:
            kind = SingleValueNodeQueryNodeKind(_kind)

        single_value_node = cls(
            type_reference=type_reference,
            kind=kind,
        )

        single_value_node.additional_properties = d
        return single_value_node

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
