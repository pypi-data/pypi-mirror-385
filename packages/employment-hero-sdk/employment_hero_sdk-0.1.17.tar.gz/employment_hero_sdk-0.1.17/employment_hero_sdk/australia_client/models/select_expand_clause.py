from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.select_item import SelectItem


T = TypeVar("T", bound="SelectExpandClause")


@_attrs_define
class SelectExpandClause:
    """
    Attributes:
        selected_items (Union[Unset, List['SelectItem']]):
        all_selected (Union[Unset, bool]):
    """

    selected_items: Union[Unset, List["SelectItem"]] = UNSET
    all_selected: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        selected_items: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.selected_items, Unset):
            selected_items = []
            for selected_items_item_data in self.selected_items:
                selected_items_item = selected_items_item_data.to_dict()
                selected_items.append(selected_items_item)

        all_selected = self.all_selected

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if selected_items is not UNSET:
            field_dict["selectedItems"] = selected_items
        if all_selected is not UNSET:
            field_dict["allSelected"] = all_selected

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.select_item import SelectItem

        d = src_dict.copy()
        selected_items = []
        _selected_items = d.pop("selectedItems", UNSET)
        for selected_items_item_data in _selected_items or []:
            selected_items_item = SelectItem.from_dict(selected_items_item_data)

            selected_items.append(selected_items_item)

        all_selected = d.pop("allSelected", UNSET)

        select_expand_clause = cls(
            selected_items=selected_items,
            all_selected=all_selected,
        )

        select_expand_clause.additional_properties = d
        return select_expand_clause

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
