from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DocumentFile")


@_attrs_define
class DocumentFile:
    """
    Attributes:
        content_length (Union[Unset, int]):
        content_type (Union[Unset, str]):
        bytes_ (Union[Unset, str]):
        filename (Union[Unset, str]):
    """

    content_length: Union[Unset, int] = UNSET
    content_type: Union[Unset, str] = UNSET
    bytes_: Union[Unset, str] = UNSET
    filename: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        content_length = self.content_length

        content_type = self.content_type

        bytes_ = self.bytes_

        filename = self.filename

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if content_length is not UNSET:
            field_dict["contentLength"] = content_length
        if content_type is not UNSET:
            field_dict["contentType"] = content_type
        if bytes_ is not UNSET:
            field_dict["bytes"] = bytes_
        if filename is not UNSET:
            field_dict["filename"] = filename

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        content_length = d.pop("contentLength", UNSET)

        content_type = d.pop("contentType", UNSET)

        bytes_ = d.pop("bytes", UNSET)

        filename = d.pop("filename", UNSET)

        document_file = cls(
            content_length=content_length,
            content_type=content_type,
            bytes_=bytes_,
            filename=filename,
        )

        document_file.additional_properties = d
        return document_file

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
