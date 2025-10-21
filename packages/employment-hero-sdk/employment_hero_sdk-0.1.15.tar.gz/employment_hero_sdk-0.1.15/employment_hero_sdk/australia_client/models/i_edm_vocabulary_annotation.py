from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.i_edm_term import IEdmTerm
    from ..models.i_edm_vocabulary_annotatable import IEdmVocabularyAnnotatable


T = TypeVar("T", bound="IEdmVocabularyAnnotation")


@_attrs_define
class IEdmVocabularyAnnotation:
    """
    Attributes:
        qualifier (Union[Unset, str]):
        term (Union[Unset, IEdmTerm]):
        target (Union[Unset, IEdmVocabularyAnnotatable]):
    """

    qualifier: Union[Unset, str] = UNSET
    term: Union[Unset, "IEdmTerm"] = UNSET
    target: Union[Unset, "IEdmVocabularyAnnotatable"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        qualifier = self.qualifier

        term: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.term, Unset):
            term = self.term.to_dict()

        target: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.target, Unset):
            target = self.target.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if qualifier is not UNSET:
            field_dict["qualifier"] = qualifier
        if term is not UNSET:
            field_dict["term"] = term
        if target is not UNSET:
            field_dict["target"] = target

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.i_edm_term import IEdmTerm
        from ..models.i_edm_vocabulary_annotatable import IEdmVocabularyAnnotatable

        d = src_dict.copy()
        qualifier = d.pop("qualifier", UNSET)

        _term = d.pop("term", UNSET)
        term: Union[Unset, IEdmTerm]
        if isinstance(_term, Unset):
            term = UNSET
        else:
            term = IEdmTerm.from_dict(_term)

        _target = d.pop("target", UNSET)
        target: Union[Unset, IEdmVocabularyAnnotatable]
        if isinstance(_target, Unset):
            target = UNSET
        else:
            target = IEdmVocabularyAnnotatable.from_dict(_target)

        i_edm_vocabulary_annotation = cls(
            qualifier=qualifier,
            term=term,
            target=target,
        )

        i_edm_vocabulary_annotation.additional_properties = d
        return i_edm_vocabulary_annotation

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
