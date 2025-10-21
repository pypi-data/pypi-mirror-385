from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.recover_password_model_message_type_enum import RecoverPasswordModelMessageTypeEnum
from ..types import UNSET, Unset

T = TypeVar("T", bound="RecoverPasswordModel")


@_attrs_define
class RecoverPasswordModel:
    """
    Attributes:
        username (str): Required
        message_type (Union[Unset, RecoverPasswordModelMessageTypeEnum]):
    """

    username: str
    message_type: Union[Unset, RecoverPasswordModelMessageTypeEnum] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        username = self.username

        message_type: Union[Unset, str] = UNSET
        if not isinstance(self.message_type, Unset):
            message_type = self.message_type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "username": username,
            }
        )
        if message_type is not UNSET:
            field_dict["messageType"] = message_type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        username = d.pop("username")

        _message_type = d.pop("messageType", UNSET)
        message_type: Union[Unset, RecoverPasswordModelMessageTypeEnum]
        if isinstance(_message_type, Unset):
            message_type = UNSET
        else:
            message_type = RecoverPasswordModelMessageTypeEnum(_message_type)

        recover_password_model = cls(
            username=username,
            message_type=message_type,
        )

        recover_password_model.additional_properties = d
        return recover_password_model

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
