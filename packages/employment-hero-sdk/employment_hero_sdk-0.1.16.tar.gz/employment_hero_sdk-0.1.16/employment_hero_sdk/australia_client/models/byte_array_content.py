from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.key_value_pair_string_i_enumerable_1 import KeyValuePairStringIEnumerable1


T = TypeVar("T", bound="ByteArrayContent")


@_attrs_define
class ByteArrayContent:
    """
    Attributes:
        headers (Union[Unset, List['KeyValuePairStringIEnumerable1']]):
    """

    headers: Union[Unset, List["KeyValuePairStringIEnumerable1"]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        headers: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.headers, Unset):
            headers = []
            for headers_item_data in self.headers:
                headers_item = headers_item_data.to_dict()
                headers.append(headers_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if headers is not UNSET:
            field_dict["headers"] = headers

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.key_value_pair_string_i_enumerable_1 import KeyValuePairStringIEnumerable1

        d = src_dict.copy()
        headers = []
        _headers = d.pop("headers", UNSET)
        for headers_item_data in _headers or []:
            headers_item = KeyValuePairStringIEnumerable1.from_dict(headers_item_data)

            headers.append(headers_item)

        byte_array_content = cls(
            headers=headers,
        )

        byte_array_content.additional_properties = d
        return byte_array_content

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
