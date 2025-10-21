from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.business_access_list_model_related_user_type import BusinessAccessListModelRelatedUserType
from ..types import UNSET, Unset

T = TypeVar("T", bound="BusinessAccessListModel")


@_attrs_define
class BusinessAccessListModel:
    """
    Attributes:
        user_id (Union[Unset, int]):
        username (Union[Unset, str]):
        display_name (Union[Unset, str]):
        email (Union[Unset, str]):
        is_active (Union[Unset, bool]):
        user_type (Union[Unset, BusinessAccessListModelRelatedUserType]):
        two_factor_enabled (Union[Unset, bool]):
    """

    user_id: Union[Unset, int] = UNSET
    username: Union[Unset, str] = UNSET
    display_name: Union[Unset, str] = UNSET
    email: Union[Unset, str] = UNSET
    is_active: Union[Unset, bool] = UNSET
    user_type: Union[Unset, BusinessAccessListModelRelatedUserType] = UNSET
    two_factor_enabled: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        user_id = self.user_id

        username = self.username

        display_name = self.display_name

        email = self.email

        is_active = self.is_active

        user_type: Union[Unset, str] = UNSET
        if not isinstance(self.user_type, Unset):
            user_type = self.user_type.value

        two_factor_enabled = self.two_factor_enabled

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if user_id is not UNSET:
            field_dict["userId"] = user_id
        if username is not UNSET:
            field_dict["username"] = username
        if display_name is not UNSET:
            field_dict["displayName"] = display_name
        if email is not UNSET:
            field_dict["email"] = email
        if is_active is not UNSET:
            field_dict["isActive"] = is_active
        if user_type is not UNSET:
            field_dict["userType"] = user_type
        if two_factor_enabled is not UNSET:
            field_dict["twoFactorEnabled"] = two_factor_enabled

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        user_id = d.pop("userId", UNSET)

        username = d.pop("username", UNSET)

        display_name = d.pop("displayName", UNSET)

        email = d.pop("email", UNSET)

        is_active = d.pop("isActive", UNSET)

        _user_type = d.pop("userType", UNSET)
        user_type: Union[Unset, BusinessAccessListModelRelatedUserType]
        if isinstance(_user_type, Unset):
            user_type = UNSET
        else:
            user_type = BusinessAccessListModelRelatedUserType(_user_type)

        two_factor_enabled = d.pop("twoFactorEnabled", UNSET)

        business_access_list_model = cls(
            user_id=user_id,
            username=username,
            display_name=display_name,
            email=email,
            is_active=is_active,
            user_type=user_type,
            two_factor_enabled=two_factor_enabled,
        )

        business_access_list_model.additional_properties = d
        return business_access_list_model

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
