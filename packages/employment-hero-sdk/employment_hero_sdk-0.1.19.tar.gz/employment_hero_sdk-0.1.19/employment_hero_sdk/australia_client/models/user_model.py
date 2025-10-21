from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UserModel")


@_attrs_define
class UserModel:
    """
    Attributes:
        id (Union[Unset, int]):
        email (Union[Unset, str]):
        display_name (Union[Unset, str]):
        time_zone (Union[Unset, str]):
    """

    id: Union[Unset, int] = UNSET
    email: Union[Unset, str] = UNSET
    display_name: Union[Unset, str] = UNSET
    time_zone: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        email = self.email

        display_name = self.display_name

        time_zone = self.time_zone

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if email is not UNSET:
            field_dict["email"] = email
        if display_name is not UNSET:
            field_dict["displayName"] = display_name
        if time_zone is not UNSET:
            field_dict["timeZone"] = time_zone

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        email = d.pop("email", UNSET)

        display_name = d.pop("displayName", UNSET)

        time_zone = d.pop("timeZone", UNSET)

        user_model = cls(
            id=id,
            email=email,
            display_name=display_name,
            time_zone=time_zone,
        )

        user_model.additional_properties = d
        return user_model

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
