from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ProfileImageMetadata")


@_attrs_define
class ProfileImageMetadata:
    """
    Attributes:
        content_type (Union[Unset, str]):
        extension (Union[Unset, str]):
        width (Union[Unset, int]):
        height (Union[Unset, int]):
    """

    content_type: Union[Unset, str] = UNSET
    extension: Union[Unset, str] = UNSET
    width: Union[Unset, int] = UNSET
    height: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        content_type = self.content_type

        extension = self.extension

        width = self.width

        height = self.height

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if content_type is not UNSET:
            field_dict["contentType"] = content_type
        if extension is not UNSET:
            field_dict["extension"] = extension
        if width is not UNSET:
            field_dict["width"] = width
        if height is not UNSET:
            field_dict["height"] = height

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        content_type = d.pop("contentType", UNSET)

        extension = d.pop("extension", UNSET)

        width = d.pop("width", UNSET)

        height = d.pop("height", UNSET)

        profile_image_metadata = cls(
            content_type=content_type,
            extension=extension,
            width=width,
            height=height,
        )

        profile_image_metadata.additional_properties = d
        return profile_image_metadata

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
