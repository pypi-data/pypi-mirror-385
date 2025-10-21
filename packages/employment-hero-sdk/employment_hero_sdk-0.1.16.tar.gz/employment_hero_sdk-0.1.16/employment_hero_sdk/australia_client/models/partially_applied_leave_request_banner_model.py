from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PartiallyAppliedLeaveRequestBannerModel")


@_attrs_define
class PartiallyAppliedLeaveRequestBannerModel:
    """
    Attributes:
        header (Union[Unset, str]):
        items (Union[Unset, List[str]]):
    """

    header: Union[Unset, str] = UNSET
    items: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        header = self.header

        items: Union[Unset, List[str]] = UNSET
        if not isinstance(self.items, Unset):
            items = self.items

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if header is not UNSET:
            field_dict["header"] = header
        if items is not UNSET:
            field_dict["items"] = items

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        header = d.pop("header", UNSET)

        items = cast(List[str], d.pop("items", UNSET))

        partially_applied_leave_request_banner_model = cls(
            header=header,
            items=items,
        )

        partially_applied_leave_request_banner_model.additional_properties = d
        return partially_applied_leave_request_banner_model

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
