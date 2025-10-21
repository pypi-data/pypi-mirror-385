from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="NewUserModel")


@_attrs_define
class NewUserModel:
    """
    Attributes:
        username (str): Required
        display_name (str): Required
        time_zone (Union[Unset, str]):
        api_only (Union[Unset, bool]):
        email (Union[Unset, str]):
        email_confirmed (Union[Unset, bool]):
    """

    username: str
    display_name: str
    time_zone: Union[Unset, str] = UNSET
    api_only: Union[Unset, bool] = UNSET
    email: Union[Unset, str] = UNSET
    email_confirmed: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        username = self.username

        display_name = self.display_name

        time_zone = self.time_zone

        api_only = self.api_only

        email = self.email

        email_confirmed = self.email_confirmed

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "username": username,
                "displayName": display_name,
            }
        )
        if time_zone is not UNSET:
            field_dict["timeZone"] = time_zone
        if api_only is not UNSET:
            field_dict["apiOnly"] = api_only
        if email is not UNSET:
            field_dict["email"] = email
        if email_confirmed is not UNSET:
            field_dict["emailConfirmed"] = email_confirmed

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        username = d.pop("username")

        display_name = d.pop("displayName")

        time_zone = d.pop("timeZone", UNSET)

        api_only = d.pop("apiOnly", UNSET)

        email = d.pop("email", UNSET)

        email_confirmed = d.pop("emailConfirmed", UNSET)

        new_user_model = cls(
            username=username,
            display_name=display_name,
            time_zone=time_zone,
            api_only=api_only,
            email=email,
            email_confirmed=email_confirmed,
        )

        new_user_model.additional_properties = d
        return new_user_model

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
