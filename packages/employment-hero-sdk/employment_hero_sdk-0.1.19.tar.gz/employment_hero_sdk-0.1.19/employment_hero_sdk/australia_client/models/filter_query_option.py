from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.filter_clause import FilterClause
    from ..models.filter_query_validator import FilterQueryValidator
    from ..models.o_data_query_context import ODataQueryContext


T = TypeVar("T", bound="FilterQueryOption")


@_attrs_define
class FilterQueryOption:
    """
    Attributes:
        context (Union[Unset, ODataQueryContext]):
        validator (Union[Unset, FilterQueryValidator]):
        filter_clause (Union[Unset, FilterClause]):
        raw_value (Union[Unset, str]):
    """

    context: Union[Unset, "ODataQueryContext"] = UNSET
    validator: Union[Unset, "FilterQueryValidator"] = UNSET
    filter_clause: Union[Unset, "FilterClause"] = UNSET
    raw_value: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        context: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.context, Unset):
            context = self.context.to_dict()

        validator: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.validator, Unset):
            validator = self.validator.to_dict()

        filter_clause: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.filter_clause, Unset):
            filter_clause = self.filter_clause.to_dict()

        raw_value = self.raw_value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if context is not UNSET:
            field_dict["context"] = context
        if validator is not UNSET:
            field_dict["validator"] = validator
        if filter_clause is not UNSET:
            field_dict["filterClause"] = filter_clause
        if raw_value is not UNSET:
            field_dict["rawValue"] = raw_value

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.filter_clause import FilterClause
        from ..models.filter_query_validator import FilterQueryValidator
        from ..models.o_data_query_context import ODataQueryContext

        d = src_dict.copy()
        _context = d.pop("context", UNSET)
        context: Union[Unset, ODataQueryContext]
        if isinstance(_context, Unset):
            context = UNSET
        else:
            context = ODataQueryContext.from_dict(_context)

        _validator = d.pop("validator", UNSET)
        validator: Union[Unset, FilterQueryValidator]
        if isinstance(_validator, Unset):
            validator = UNSET
        else:
            validator = FilterQueryValidator.from_dict(_validator)

        _filter_clause = d.pop("filterClause", UNSET)
        filter_clause: Union[Unset, FilterClause]
        if isinstance(_filter_clause, Unset):
            filter_clause = UNSET
        else:
            filter_clause = FilterClause.from_dict(_filter_clause)

        raw_value = d.pop("rawValue", UNSET)

        filter_query_option = cls(
            context=context,
            validator=validator,
            filter_clause=filter_clause,
            raw_value=raw_value,
        )

        filter_query_option.additional_properties = d
        return filter_query_option

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
