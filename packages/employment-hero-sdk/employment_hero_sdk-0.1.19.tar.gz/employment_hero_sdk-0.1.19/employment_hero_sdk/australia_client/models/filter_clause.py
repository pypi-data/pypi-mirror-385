from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.i_edm_type_reference import IEdmTypeReference
    from ..models.range_variable import RangeVariable
    from ..models.single_value_node import SingleValueNode


T = TypeVar("T", bound="FilterClause")


@_attrs_define
class FilterClause:
    """
    Attributes:
        expression (Union[Unset, SingleValueNode]):
        range_variable (Union[Unset, RangeVariable]):
        item_type (Union[Unset, IEdmTypeReference]):
    """

    expression: Union[Unset, "SingleValueNode"] = UNSET
    range_variable: Union[Unset, "RangeVariable"] = UNSET
    item_type: Union[Unset, "IEdmTypeReference"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        expression: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.expression, Unset):
            expression = self.expression.to_dict()

        range_variable: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.range_variable, Unset):
            range_variable = self.range_variable.to_dict()

        item_type: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.item_type, Unset):
            item_type = self.item_type.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if expression is not UNSET:
            field_dict["expression"] = expression
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
        _expression = d.pop("expression", UNSET)
        expression: Union[Unset, SingleValueNode]
        if isinstance(_expression, Unset):
            expression = UNSET
        else:
            expression = SingleValueNode.from_dict(_expression)

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

        filter_clause = cls(
            expression=expression,
            range_variable=range_variable,
            item_type=item_type,
        )

        filter_clause.additional_properties = d
        return filter_clause

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
