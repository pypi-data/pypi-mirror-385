from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.order_by_clause_order_by_direction import OrderByClauseOrderByDirection
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.i_edm_type_reference import IEdmTypeReference
    from ..models.range_variable import RangeVariable
    from ..models.single_value_node import SingleValueNode


T = TypeVar("T", bound="OrderByClause")


@_attrs_define
class OrderByClause:
    """
    Attributes:
        then_by (Union[Unset, OrderByClause]):
        expression (Union[Unset, SingleValueNode]):
        direction (Union[Unset, OrderByClauseOrderByDirection]):
        range_variable (Union[Unset, RangeVariable]):
        item_type (Union[Unset, IEdmTypeReference]):
    """

    then_by: Union[Unset, "OrderByClause"] = UNSET
    expression: Union[Unset, "SingleValueNode"] = UNSET
    direction: Union[Unset, OrderByClauseOrderByDirection] = UNSET
    range_variable: Union[Unset, "RangeVariable"] = UNSET
    item_type: Union[Unset, "IEdmTypeReference"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        then_by: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.then_by, Unset):
            then_by = self.then_by.to_dict()

        expression: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.expression, Unset):
            expression = self.expression.to_dict()

        direction: Union[Unset, str] = UNSET
        if not isinstance(self.direction, Unset):
            direction = self.direction.value

        range_variable: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.range_variable, Unset):
            range_variable = self.range_variable.to_dict()

        item_type: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.item_type, Unset):
            item_type = self.item_type.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if then_by is not UNSET:
            field_dict["thenBy"] = then_by
        if expression is not UNSET:
            field_dict["expression"] = expression
        if direction is not UNSET:
            field_dict["direction"] = direction
        if range_variable is not UNSET:
            field_dict["rangeVariable"] = range_variable
        if item_type is not UNSET:
            field_dict["itemType"] = item_type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.i_edm_type_reference import IEdmTypeReference
        from ..models.range_variable import RangeVariable
        from ..models.single_value_node import SingleValueNode

        d = src_dict.copy()
        _then_by = d.pop("thenBy", UNSET)
        then_by: Union[Unset, OrderByClause]
        if isinstance(_then_by, Unset):
            then_by = UNSET
        else:
            then_by = OrderByClause.from_dict(_then_by)

        _expression = d.pop("expression", UNSET)
        expression: Union[Unset, SingleValueNode]
        if isinstance(_expression, Unset):
            expression = UNSET
        else:
            expression = SingleValueNode.from_dict(_expression)

        _direction = d.pop("direction", UNSET)
        direction: Union[Unset, OrderByClauseOrderByDirection]
        if isinstance(_direction, Unset):
            direction = UNSET
        else:
            direction = OrderByClauseOrderByDirection(_direction)

        _range_variable = d.pop("rangeVariable", UNSET)
        range_variable: Union[Unset, RangeVariable]
        if isinstance(_range_variable, Unset):
            range_variable = UNSET
        else:
            range_variable = RangeVariable.from_dict(_range_variable)

        _item_type = d.pop("itemType", UNSET)
        item_type: Union[Unset, IEdmTypeReference]
        if isinstance(_item_type, Unset):
            item_type = UNSET
        else:
            item_type = IEdmTypeReference.from_dict(_item_type)

        order_by_clause = cls(
            then_by=then_by,
            expression=expression,
            direction=direction,
            range_variable=range_variable,
            item_type=item_type,
        )

        order_by_clause.additional_properties = d
        return order_by_clause

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
