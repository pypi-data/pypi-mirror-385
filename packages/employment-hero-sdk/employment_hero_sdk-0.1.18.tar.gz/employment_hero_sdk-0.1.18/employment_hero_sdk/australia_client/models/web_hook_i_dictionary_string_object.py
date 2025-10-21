from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.web_hook_i_dictionary_string_object_object import WebHookIDictionaryStringObjectObject


T = TypeVar("T", bound="WebHookIDictionaryStringObject")


@_attrs_define
class WebHookIDictionaryStringObject:
    """ """

    additional_properties: Dict[str, "WebHookIDictionaryStringObjectObject"] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        field_dict: Dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = prop.to_dict()

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.web_hook_i_dictionary_string_object_object import WebHookIDictionaryStringObjectObject

        d = src_dict.copy()
        web_hook_i_dictionary_string_object = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = WebHookIDictionaryStringObjectObject.from_dict(prop_dict)

            additional_properties[prop_name] = additional_property

        web_hook_i_dictionary_string_object.additional_properties = additional_properties
        return web_hook_i_dictionary_string_object

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> "WebHookIDictionaryStringObjectObject":
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: "WebHookIDictionaryStringObjectObject") -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
