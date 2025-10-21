from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.o_data_query_context import ODataQueryContext
    from ..models.top_query_validator import TopQueryValidator


T = TypeVar("T", bound="TopQueryOption")


@_attrs_define
class TopQueryOption:
    """
    Attributes:
        context (Union[Unset, ODataQueryContext]):
        raw_value (Union[Unset, str]):
        value (Union[Unset, int]):
        validator (Union[Unset, TopQueryValidator]):
    """

    context: Union[Unset, "ODataQueryContext"] = UNSET
    raw_value: Union[Unset, str] = UNSET
    value: Union[Unset, int] = UNSET
    validator: Union[Unset, "TopQueryValidator"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        context: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.context, Unset):
            context = self.context.to_dict()

        raw_value = self.raw_value

        value = self.value

        validator: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.validator, Unset):
            validator = self.validator.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if context is not UNSET:
            field_dict["context"] = context
        if raw_value is not UNSET:
            field_dict["rawValue"] = raw_value
        if value is not UNSET:
            field_dict["value"] = value
        if validator is not UNSET:
            field_dict["validator"] = validator

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.o_data_query_context import ODataQueryContext
        from ..models.top_query_validator import TopQueryValidator

        d = src_dict.copy()
        _context = d.pop("context", UNSET)
        context: Union[Unset, ODataQueryContext]
        if isinstance(_context, Unset):
            context = UNSET
        else:
            context = ODataQueryContext.from_dict(_context)

        raw_value = d.pop("rawValue", UNSET)

        value = d.pop("value", UNSET)

        _validator = d.pop("validator", UNSET)
        validator: Union[Unset, TopQueryValidator]
        if isinstance(_validator, Unset):
            validator = UNSET
        else:
            validator = TopQueryValidator.from_dict(_validator)

        top_query_option = cls(
            context=context,
            raw_value=raw_value,
            value=value,
            validator=validator,
        )

        top_query_option.additional_properties = d
        return top_query_option

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
