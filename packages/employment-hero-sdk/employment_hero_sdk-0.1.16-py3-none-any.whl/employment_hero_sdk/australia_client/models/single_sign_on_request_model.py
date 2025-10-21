from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.single_sign_on_request_model_navigation_display_enum import SingleSignOnRequestModelNavigationDisplayEnum
from ..types import UNSET, Unset

T = TypeVar("T", bound="SingleSignOnRequestModel")


@_attrs_define
class SingleSignOnRequestModel:
    """
    Attributes:
        business_id (Union[Unset, int]):
        user_name (Union[Unset, str]):
        url (Union[Unset, str]):
        navigation (Union[Unset, SingleSignOnRequestModelNavigationDisplayEnum]):
        host_name (Union[Unset, str]):
    """

    business_id: Union[Unset, int] = UNSET
    user_name: Union[Unset, str] = UNSET
    url: Union[Unset, str] = UNSET
    navigation: Union[Unset, SingleSignOnRequestModelNavigationDisplayEnum] = UNSET
    host_name: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        business_id = self.business_id

        user_name = self.user_name

        url = self.url

        navigation: Union[Unset, str] = UNSET
        if not isinstance(self.navigation, Unset):
            navigation = self.navigation.value

        host_name = self.host_name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if business_id is not UNSET:
            field_dict["businessId"] = business_id
        if user_name is not UNSET:
            field_dict["userName"] = user_name
        if url is not UNSET:
            field_dict["url"] = url
        if navigation is not UNSET:
            field_dict["navigation"] = navigation
        if host_name is not UNSET:
            field_dict["hostName"] = host_name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        business_id = d.pop("businessId", UNSET)

        user_name = d.pop("userName", UNSET)

        url = d.pop("url", UNSET)

        _navigation = d.pop("navigation", UNSET)
        navigation: Union[Unset, SingleSignOnRequestModelNavigationDisplayEnum]
        if isinstance(_navigation, Unset):
            navigation = UNSET
        else:
            navigation = SingleSignOnRequestModelNavigationDisplayEnum(_navigation)

        host_name = d.pop("hostName", UNSET)

        single_sign_on_request_model = cls(
            business_id=business_id,
            user_name=user_name,
            url=url,
            navigation=navigation,
            host_name=host_name,
        )

        single_sign_on_request_model.additional_properties = d
        return single_sign_on_request_model

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
