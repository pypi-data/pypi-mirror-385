from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.o_data_query_context import ODataQueryContext
    from ..models.select_expand_clause import SelectExpandClause
    from ..models.select_expand_query_validator import SelectExpandQueryValidator


T = TypeVar("T", bound="SelectExpandQueryOption")


@_attrs_define
class SelectExpandQueryOption:
    """
    Attributes:
        context (Union[Unset, ODataQueryContext]):
        raw_select (Union[Unset, str]):
        raw_expand (Union[Unset, str]):
        validator (Union[Unset, SelectExpandQueryValidator]):
        select_expand_clause (Union[Unset, SelectExpandClause]):
    """

    context: Union[Unset, "ODataQueryContext"] = UNSET
    raw_select: Union[Unset, str] = UNSET
    raw_expand: Union[Unset, str] = UNSET
    validator: Union[Unset, "SelectExpandQueryValidator"] = UNSET
    select_expand_clause: Union[Unset, "SelectExpandClause"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        context: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.context, Unset):
            context = self.context.to_dict()

        raw_select = self.raw_select

        raw_expand = self.raw_expand

        validator: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.validator, Unset):
            validator = self.validator.to_dict()

        select_expand_clause: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.select_expand_clause, Unset):
            select_expand_clause = self.select_expand_clause.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if context is not UNSET:
            field_dict["context"] = context
        if raw_select is not UNSET:
            field_dict["rawSelect"] = raw_select
        if raw_expand is not UNSET:
            field_dict["rawExpand"] = raw_expand
        if validator is not UNSET:
            field_dict["validator"] = validator
        if select_expand_clause is not UNSET:
            field_dict["selectExpandClause"] = select_expand_clause

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.o_data_query_context import ODataQueryContext
        from ..models.select_expand_clause import SelectExpandClause
        from ..models.select_expand_query_validator import SelectExpandQueryValidator

        d = src_dict.copy()
        _context = d.pop("context", UNSET)
        context: Union[Unset, ODataQueryContext]
        if isinstance(_context, Unset):
            context = UNSET
        else:
            context = ODataQueryContext.from_dict(_context)

        raw_select = d.pop("rawSelect", UNSET)

        raw_expand = d.pop("rawExpand", UNSET)

        _validator = d.pop("validator", UNSET)
        validator: Union[Unset, SelectExpandQueryValidator]
        if isinstance(_validator, Unset):
            validator = UNSET
        else:
            validator = SelectExpandQueryValidator.from_dict(_validator)

        _select_expand_clause = d.pop("selectExpandClause", UNSET)
        select_expand_clause: Union[Unset, SelectExpandClause]
        if isinstance(_select_expand_clause, Unset):
            select_expand_clause = UNSET
        else:
            select_expand_clause = SelectExpandClause.from_dict(_select_expand_clause)

        select_expand_query_option = cls(
            context=context,
            raw_select=raw_select,
            raw_expand=raw_expand,
            validator=validator,
            select_expand_clause=select_expand_clause,
        )

        select_expand_query_option.additional_properties = d
        return select_expand_query_option

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
