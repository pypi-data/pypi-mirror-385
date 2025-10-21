from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.order_by_node_order_by_direction import OrderByNodeOrderByDirection
from ..types import UNSET, Unset

T = TypeVar("T", bound="OrderByNode")


@_attrs_define
class OrderByNode:
    """
    Attributes:
        direction (Union[Unset, OrderByNodeOrderByDirection]):
    """

    direction: Union[Unset, OrderByNodeOrderByDirection] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        direction: Union[Unset, str] = UNSET
        if not isinstance(self.direction, Unset):
            direction = self.direction.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if direction is not UNSET:
            field_dict["direction"] = direction

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _direction = d.pop("direction", UNSET)
        direction: Union[Unset, OrderByNodeOrderByDirection]
        if isinstance(_direction, Unset):
            direction = UNSET
        else:
            direction = OrderByNodeOrderByDirection(_direction)

        order_by_node = cls(
            direction=direction,
        )

        order_by_node.additional_properties = d
        return order_by_node

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
