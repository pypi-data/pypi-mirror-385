from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.o_data_query_context import ODataQueryContext
    from ..models.order_by_clause import OrderByClause
    from ..models.order_by_node import OrderByNode
    from ..models.order_by_query_validator import OrderByQueryValidator


T = TypeVar("T", bound="OrderByQueryOption")


@_attrs_define
class OrderByQueryOption:
    """
    Attributes:
        context (Union[Unset, ODataQueryContext]):
        order_by_nodes (Union[Unset, List['OrderByNode']]):
        raw_value (Union[Unset, str]):
        validator (Union[Unset, OrderByQueryValidator]):
        order_by_clause (Union[Unset, OrderByClause]):
    """

    context: Union[Unset, "ODataQueryContext"] = UNSET
    order_by_nodes: Union[Unset, List["OrderByNode"]] = UNSET
    raw_value: Union[Unset, str] = UNSET
    validator: Union[Unset, "OrderByQueryValidator"] = UNSET
    order_by_clause: Union[Unset, "OrderByClause"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        context: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.context, Unset):
            context = self.context.to_dict()

        order_by_nodes: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.order_by_nodes, Unset):
            order_by_nodes = []
            for order_by_nodes_item_data in self.order_by_nodes:
                order_by_nodes_item = order_by_nodes_item_data.to_dict()
                order_by_nodes.append(order_by_nodes_item)

        raw_value = self.raw_value

        validator: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.validator, Unset):
            validator = self.validator.to_dict()

        order_by_clause: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.order_by_clause, Unset):
            order_by_clause = self.order_by_clause.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if context is not UNSET:
            field_dict["context"] = context
        if order_by_nodes is not UNSET:
            field_dict["orderByNodes"] = order_by_nodes
        if raw_value is not UNSET:
            field_dict["rawValue"] = raw_value
        if validator is not UNSET:
            field_dict["validator"] = validator
        if order_by_clause is not UNSET:
            field_dict["orderByClause"] = order_by_clause

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.o_data_query_context import ODataQueryContext
        from ..models.order_by_clause import OrderByClause
        from ..models.order_by_node import OrderByNode
        from ..models.order_by_query_validator import OrderByQueryValidator

        d = src_dict.copy()
        _context = d.pop("context", UNSET)
        context: Union[Unset, ODataQueryContext]
        if isinstance(_context, Unset):
            context = UNSET
        else:
            context = ODataQueryContext.from_dict(_context)

        order_by_nodes = []
        _order_by_nodes = d.pop("orderByNodes", UNSET)
        for order_by_nodes_item_data in _order_by_nodes or []:
            order_by_nodes_item = OrderByNode.from_dict(order_by_nodes_item_data)

            order_by_nodes.append(order_by_nodes_item)

        raw_value = d.pop("rawValue", UNSET)

        _validator = d.pop("validator", UNSET)
        validator: Union[Unset, OrderByQueryValidator]
        if isinstance(_validator, Unset):
            validator = UNSET
        else:
            validator = OrderByQueryValidator.from_dict(_validator)

        _order_by_clause = d.pop("orderByClause", UNSET)
        order_by_clause: Union[Unset, OrderByClause]
        if isinstance(_order_by_clause, Unset):
            order_by_clause = UNSET
        else:
            order_by_clause = OrderByClause.from_dict(_order_by_clause)

        order_by_query_option = cls(
            context=context,
            order_by_nodes=order_by_nodes,
            raw_value=raw_value,
            validator=validator,
            order_by_clause=order_by_clause,
        )

        order_by_query_option.additional_properties = d
        return order_by_query_option

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
