from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CommunicationMessageAttachmentModel")


@_attrs_define
class CommunicationMessageAttachmentModel:
    """
    Attributes:
        value (Union[Unset, str]):
        type (Union[Unset, str]):
        title (Union[Unset, str]):
        record_id (Union[Unset, str]):
    """

    value: Union[Unset, str] = UNSET
    type: Union[Unset, str] = UNSET
    title: Union[Unset, str] = UNSET
    record_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        value = self.value

        type = self.type

        title = self.title

        record_id = self.record_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if value is not UNSET:
            field_dict["value"] = value
        if type is not UNSET:
            field_dict["type"] = type
        if title is not UNSET:
            field_dict["title"] = title
        if record_id is not UNSET:
            field_dict["recordId"] = record_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        value = d.pop("value", UNSET)

        type = d.pop("type", UNSET)

        title = d.pop("title", UNSET)

        record_id = d.pop("recordId", UNSET)

        communication_message_attachment_model = cls(
            value=value,
            type=type,
            title=title,
            record_id=record_id,
        )

        communication_message_attachment_model.additional_properties = d
        return communication_message_attachment_model

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
