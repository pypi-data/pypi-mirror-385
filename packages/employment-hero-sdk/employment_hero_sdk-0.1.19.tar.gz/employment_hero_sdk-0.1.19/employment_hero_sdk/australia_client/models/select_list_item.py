from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.select_list_group import SelectListGroup


T = TypeVar("T", bound="SelectListItem")


@_attrs_define
class SelectListItem:
    """
    Attributes:
        text (Union[Unset, str]):
        value (Union[Unset, str]):
        group (Union[Unset, SelectListGroup]):
        disabled (Union[Unset, bool]):
        selected (Union[Unset, bool]):
    """

    text: Union[Unset, str] = UNSET
    value: Union[Unset, str] = UNSET
    group: Union[Unset, "SelectListGroup"] = UNSET
    disabled: Union[Unset, bool] = UNSET
    selected: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        text = self.text

        value = self.value

        group: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.group, Unset):
            group = self.group.to_dict()

        disabled = self.disabled

        selected = self.selected

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if text is not UNSET:
            field_dict["text"] = text
        if value is not UNSET:
            field_dict["value"] = value
        if group is not UNSET:
            field_dict["group"] = group
        if disabled is not UNSET:
            field_dict["disabled"] = disabled
        if selected is not UNSET:
            field_dict["selected"] = selected

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.select_list_group import SelectListGroup

        d = src_dict.copy()
        text = d.pop("text", UNSET)

        value = d.pop("value", UNSET)

        _group = d.pop("group", UNSET)
        group: Union[Unset, SelectListGroup]
        if isinstance(_group, Unset):
            group = UNSET
        else:
            group = SelectListGroup.from_dict(_group)

        disabled = d.pop("disabled", UNSET)

        selected = d.pop("selected", UNSET)

        select_list_item = cls(
            text=text,
            value=value,
            group=group,
            disabled=disabled,
            selected=selected,
        )

        select_list_item.additional_properties = d
        return select_list_item

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
