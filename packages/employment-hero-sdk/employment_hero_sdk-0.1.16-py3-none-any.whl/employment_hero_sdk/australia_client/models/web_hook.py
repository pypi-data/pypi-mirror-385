from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.web_hook_i_dictionary_string_object import WebHookIDictionaryStringObject
    from ..models.web_hook_i_dictionary_string_string import WebHookIDictionaryStringString


T = TypeVar("T", bound="WebHook")


@_attrs_define
class WebHook:
    """
    Attributes:
        id (Union[Unset, str]):
        web_hook_uri (Union[Unset, str]):
        secret (Union[Unset, str]):
        description (Union[Unset, str]):
        is_paused (Union[Unset, bool]):
        filters (Union[Unset, List[str]]):
        headers (Union[Unset, WebHookIDictionaryStringString]):
        properties (Union[Unset, WebHookIDictionaryStringObject]):
    """

    id: Union[Unset, str] = UNSET
    web_hook_uri: Union[Unset, str] = UNSET
    secret: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    is_paused: Union[Unset, bool] = UNSET
    filters: Union[Unset, List[str]] = UNSET
    headers: Union[Unset, "WebHookIDictionaryStringString"] = UNSET
    properties: Union[Unset, "WebHookIDictionaryStringObject"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        web_hook_uri = self.web_hook_uri

        secret = self.secret

        description = self.description

        is_paused = self.is_paused

        filters: Union[Unset, List[str]] = UNSET
        if not isinstance(self.filters, Unset):
            filters = self.filters

        headers: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.headers, Unset):
            headers = self.headers.to_dict()

        properties: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.properties, Unset):
            properties = self.properties.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if web_hook_uri is not UNSET:
            field_dict["webHookUri"] = web_hook_uri
        if secret is not UNSET:
            field_dict["secret"] = secret
        if description is not UNSET:
            field_dict["description"] = description
        if is_paused is not UNSET:
            field_dict["isPaused"] = is_paused
        if filters is not UNSET:
            field_dict["filters"] = filters
        if headers is not UNSET:
            field_dict["headers"] = headers
        if properties is not UNSET:
            field_dict["properties"] = properties

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.web_hook_i_dictionary_string_object import WebHookIDictionaryStringObject
        from ..models.web_hook_i_dictionary_string_string import WebHookIDictionaryStringString

        d = src_dict.copy()
        id = d.pop("id", UNSET)

        web_hook_uri = d.pop("webHookUri", UNSET)

        secret = d.pop("secret", UNSET)

        description = d.pop("description", UNSET)

        is_paused = d.pop("isPaused", UNSET)

        filters = cast(List[str], d.pop("filters", UNSET))

        _headers = d.pop("headers", UNSET)
        headers: Union[Unset, WebHookIDictionaryStringString]
        if isinstance(_headers, Unset):
            headers = UNSET
        else:
            headers = WebHookIDictionaryStringString.from_dict(_headers)

        _properties = d.pop("properties", UNSET)
        properties: Union[Unset, WebHookIDictionaryStringObject]
        if isinstance(_properties, Unset):
            properties = UNSET
        else:
            properties = WebHookIDictionaryStringObject.from_dict(_properties)

        web_hook = cls(
            id=id,
            web_hook_uri=web_hook_uri,
            secret=secret,
            description=description,
            is_paused=is_paused,
            filters=filters,
            headers=headers,
            properties=properties,
        )

        web_hook.additional_properties = d
        return web_hook

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
