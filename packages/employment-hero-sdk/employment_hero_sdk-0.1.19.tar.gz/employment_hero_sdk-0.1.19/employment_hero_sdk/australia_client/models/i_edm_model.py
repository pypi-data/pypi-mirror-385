from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.i_edm_direct_value_annotations_manager import IEdmDirectValueAnnotationsManager
    from ..models.i_edm_schema_element import IEdmSchemaElement
    from ..models.i_edm_vocabulary_annotation import IEdmVocabularyAnnotation


T = TypeVar("T", bound="IEdmModel")


@_attrs_define
class IEdmModel:
    """
    Attributes:
        schema_elements (Union[Unset, List['IEdmSchemaElement']]):
        vocabulary_annotations (Union[Unset, List['IEdmVocabularyAnnotation']]):
        referenced_models (Union[Unset, List['IEdmModel']]):
        direct_value_annotations_manager (Union[Unset, IEdmDirectValueAnnotationsManager]):
    """

    schema_elements: Union[Unset, List["IEdmSchemaElement"]] = UNSET
    vocabulary_annotations: Union[Unset, List["IEdmVocabularyAnnotation"]] = UNSET
    referenced_models: Union[Unset, List["IEdmModel"]] = UNSET
    direct_value_annotations_manager: Union[Unset, "IEdmDirectValueAnnotationsManager"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        schema_elements: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.schema_elements, Unset):
            schema_elements = []
            for schema_elements_item_data in self.schema_elements:
                schema_elements_item = schema_elements_item_data.to_dict()
                schema_elements.append(schema_elements_item)

        vocabulary_annotations: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.vocabulary_annotations, Unset):
            vocabulary_annotations = []
            for vocabulary_annotations_item_data in self.vocabulary_annotations:
                vocabulary_annotations_item = vocabulary_annotations_item_data.to_dict()
                vocabulary_annotations.append(vocabulary_annotations_item)

        referenced_models: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.referenced_models, Unset):
            referenced_models = []
            for referenced_models_item_data in self.referenced_models:
                referenced_models_item = referenced_models_item_data.to_dict()
                referenced_models.append(referenced_models_item)

        direct_value_annotations_manager: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.direct_value_annotations_manager, Unset):
            direct_value_annotations_manager = self.direct_value_annotations_manager.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if schema_elements is not UNSET:
            field_dict["schemaElements"] = schema_elements
        if vocabulary_annotations is not UNSET:
            field_dict["vocabularyAnnotations"] = vocabulary_annotations
        if referenced_models is not UNSET:
            field_dict["referencedModels"] = referenced_models
        if direct_value_annotations_manager is not UNSET:
            field_dict["directValueAnnotationsManager"] = direct_value_annotations_manager

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.i_edm_direct_value_annotations_manager import IEdmDirectValueAnnotationsManager
        from ..models.i_edm_schema_element import IEdmSchemaElement
        from ..models.i_edm_vocabulary_annotation import IEdmVocabularyAnnotation

        d = src_dict.copy()
        schema_elements = []
        _schema_elements = d.pop("schemaElements", UNSET)
        for schema_elements_item_data in _schema_elements or []:
            schema_elements_item = IEdmSchemaElement.from_dict(schema_elements_item_data)

            schema_elements.append(schema_elements_item)

        vocabulary_annotations = []
        _vocabulary_annotations = d.pop("vocabularyAnnotations", UNSET)
        for vocabulary_annotations_item_data in _vocabulary_annotations or []:
            vocabulary_annotations_item = IEdmVocabularyAnnotation.from_dict(vocabulary_annotations_item_data)

            vocabulary_annotations.append(vocabulary_annotations_item)

        referenced_models = []
        _referenced_models = d.pop("referencedModels", UNSET)
        for referenced_models_item_data in _referenced_models or []:
            referenced_models_item = IEdmModel.from_dict(referenced_models_item_data)

            referenced_models.append(referenced_models_item)

        _direct_value_annotations_manager = d.pop("directValueAnnotationsManager", UNSET)
        direct_value_annotations_manager: Union[Unset, IEdmDirectValueAnnotationsManager]
        if isinstance(_direct_value_annotations_manager, Unset):
            direct_value_annotations_manager = UNSET
        else:
            direct_value_annotations_manager = IEdmDirectValueAnnotationsManager.from_dict(
                _direct_value_annotations_manager
            )

        i_edm_model = cls(
            schema_elements=schema_elements,
            vocabulary_annotations=vocabulary_annotations,
            referenced_models=referenced_models,
            direct_value_annotations_manager=direct_value_annotations_manager,
        )

        i_edm_model.additional_properties = d
        return i_edm_model

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
