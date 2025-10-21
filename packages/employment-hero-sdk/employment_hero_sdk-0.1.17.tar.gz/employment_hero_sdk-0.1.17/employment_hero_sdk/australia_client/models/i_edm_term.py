from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.i_edm_term_edm_schema_element_kind import IEdmTermEdmSchemaElementKind
from ..models.i_edm_term_edm_term_kind import IEdmTermEdmTermKind
from ..types import UNSET, Unset

T = TypeVar("T", bound="IEdmTerm")


@_attrs_define
class IEdmTerm:
    """
    Attributes:
        term_kind (Union[Unset, IEdmTermEdmTermKind]):
        schema_element_kind (Union[Unset, IEdmTermEdmSchemaElementKind]):
        namespace (Union[Unset, str]):
        name (Union[Unset, str]):
    """

    term_kind: Union[Unset, IEdmTermEdmTermKind] = UNSET
    schema_element_kind: Union[Unset, IEdmTermEdmSchemaElementKind] = UNSET
    namespace: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        term_kind: Union[Unset, str] = UNSET
        if not isinstance(self.term_kind, Unset):
            term_kind = self.term_kind.value

        schema_element_kind: Union[Unset, str] = UNSET
        if not isinstance(self.schema_element_kind, Unset):
            schema_element_kind = self.schema_element_kind.value

        namespace = self.namespace

        name = self.name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if term_kind is not UNSET:
            field_dict["termKind"] = term_kind
        if schema_element_kind is not UNSET:
            field_dict["schemaElementKind"] = schema_element_kind
        if namespace is not UNSET:
            field_dict["namespace"] = namespace
        if name is not UNSET:
            field_dict["name"] = name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _term_kind = d.pop("termKind", UNSET)
        term_kind: Union[Unset, IEdmTermEdmTermKind]
        if isinstance(_term_kind, Unset):
            term_kind = UNSET
        else:
            term_kind = IEdmTermEdmTermKind(_term_kind)

        _schema_element_kind = d.pop("schemaElementKind", UNSET)
        schema_element_kind: Union[Unset, IEdmTermEdmSchemaElementKind]
        if isinstance(_schema_element_kind, Unset):
            schema_element_kind = UNSET
        else:
            schema_element_kind = IEdmTermEdmSchemaElementKind(_schema_element_kind)

        namespace = d.pop("namespace", UNSET)

        name = d.pop("name", UNSET)

        i_edm_term = cls(
            term_kind=term_kind,
            schema_element_kind=schema_element_kind,
            namespace=namespace,
            name=name,
        )

        i_edm_term.additional_properties = d
        return i_edm_term

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
