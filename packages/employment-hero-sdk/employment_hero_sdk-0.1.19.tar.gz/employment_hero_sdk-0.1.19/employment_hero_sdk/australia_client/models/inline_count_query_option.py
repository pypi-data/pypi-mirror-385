from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.inline_count_query_option_inline_count_value import InlineCountQueryOptionInlineCountValue
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.o_data_query_context import ODataQueryContext


T = TypeVar("T", bound="InlineCountQueryOption")


@_attrs_define
class InlineCountQueryOption:
    """
    Attributes:
        context (Union[Unset, ODataQueryContext]):
        raw_value (Union[Unset, str]):
        value (Union[Unset, InlineCountQueryOptionInlineCountValue]):
    """

    context: Union[Unset, "ODataQueryContext"] = UNSET
    raw_value: Union[Unset, str] = UNSET
    value: Union[Unset, InlineCountQueryOptionInlineCountValue] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        context: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.context, Unset):
            context = self.context.to_dict()

        raw_value = self.raw_value

        value: Union[Unset, str] = UNSET
        if not isinstance(self.value, Unset):
            value = self.value.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if context is not UNSET:
            field_dict["context"] = context
        if raw_value is not UNSET:
            field_dict["rawValue"] = raw_value
        if value is not UNSET:
            field_dict["value"] = value

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.o_data_query_context import ODataQueryContext

        d = src_dict.copy()
        _context = d.pop("context", UNSET)
        context: Union[Unset, ODataQueryContext]
        if isinstance(_context, Unset):
            context = UNSET
        else:
            context = ODataQueryContext.from_dict(_context)

        raw_value = d.pop("rawValue", UNSET)

        _value = d.pop("value", UNSET)
        value: Union[Unset, InlineCountQueryOptionInlineCountValue]
        if isinstance(_value, Unset):
            value = UNSET
        else:
            value = InlineCountQueryOptionInlineCountValue(_value)

        inline_count_query_option = cls(
            context=context,
            raw_value=raw_value,
            value=value,
        )

        inline_count_query_option.additional_properties = d
        return inline_count_query_option

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
