from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.device_token_model_mobile_platform import DeviceTokenModelMobilePlatform
from ..types import UNSET, Unset

T = TypeVar("T", bound="DeviceTokenModel")


@_attrs_define
class DeviceTokenModel:
    """
    Attributes:
        token (Union[Unset, str]):
        platform (Union[Unset, DeviceTokenModelMobilePlatform]):
    """

    token: Union[Unset, str] = UNSET
    platform: Union[Unset, DeviceTokenModelMobilePlatform] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        token = self.token

        platform: Union[Unset, str] = UNSET
        if not isinstance(self.platform, Unset):
            platform = self.platform.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if token is not UNSET:
            field_dict["token"] = token
        if platform is not UNSET:
            field_dict["platform"] = platform

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        token = d.pop("token", UNSET)

        _platform = d.pop("platform", UNSET)
        platform: Union[Unset, DeviceTokenModelMobilePlatform]
        if isinstance(_platform, Unset):
            platform = UNSET
        else:
            platform = DeviceTokenModelMobilePlatform(_platform)

        device_token_model = cls(
            token=token,
            platform=platform,
        )

        device_token_model.additional_properties = d
        return device_token_model

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
