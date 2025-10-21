from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.i_edm_schema_element_edm_schema_element_kind import IEdmSchemaElementEdmSchemaElementKind
from ..types import UNSET, Unset

T = TypeVar("T", bound="IEdmSchemaElement")


@_attrs_define
class IEdmSchemaElement:
    """
    Attributes:
        schema_element_kind (Union[Unset, IEdmSchemaElementEdmSchemaElementKind]):
        namespace (Union[Unset, str]):
        name (Union[Unset, str]):
    """

    schema_element_kind: Union[Unset, IEdmSchemaElementEdmSchemaElementKind] = UNSET
    namespace: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        schema_element_kind: Union[Unset, str] = UNSET
        if not isinstance(self.schema_element_kind, Unset):
            schema_element_kind = self.schema_element_kind.value

        namespace = self.namespace

        name = self.name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
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
        _schema_element_kind = d.pop("schemaElementKind", UNSET)
        schema_element_kind: Union[Unset, IEdmSchemaElementEdmSchemaElementKind]
        if isinstance(_schema_element_kind, Unset):
            schema_element_kind = UNSET
        else:
            schema_element_kind = IEdmSchemaElementEdmSchemaElementKind(_schema_element_kind)

        namespace = d.pop("namespace", UNSET)

        name = d.pop("name", UNSET)

        i_edm_schema_element = cls(
            schema_element_kind=schema_element_kind,
            namespace=namespace,
            name=name,
        )

        i_edm_schema_element.additional_properties = d
        return i_edm_schema_element

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
