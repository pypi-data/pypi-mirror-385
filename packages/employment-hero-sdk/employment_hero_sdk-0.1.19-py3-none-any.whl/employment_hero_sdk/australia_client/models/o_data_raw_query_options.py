from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ODataRawQueryOptions")


@_attrs_define
class ODataRawQueryOptions:
    """
    Attributes:
        filter_ (Union[Unset, str]):
        order_by (Union[Unset, str]):
        top (Union[Unset, str]):
        skip (Union[Unset, str]):
        select (Union[Unset, str]):
        expand (Union[Unset, str]):
        inline_count (Union[Unset, str]):
        format_ (Union[Unset, str]):
        skip_token (Union[Unset, str]):
    """

    filter_: Union[Unset, str] = UNSET
    order_by: Union[Unset, str] = UNSET
    top: Union[Unset, str] = UNSET
    skip: Union[Unset, str] = UNSET
    select: Union[Unset, str] = UNSET
    expand: Union[Unset, str] = UNSET
    inline_count: Union[Unset, str] = UNSET
    format_: Union[Unset, str] = UNSET
    skip_token: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        filter_ = self.filter_

        order_by = self.order_by

        top = self.top

        skip = self.skip

        select = self.select

        expand = self.expand

        inline_count = self.inline_count

        format_ = self.format_

        skip_token = self.skip_token

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if filter_ is not UNSET:
            field_dict["filter"] = filter_
        if order_by is not UNSET:
            field_dict["orderBy"] = order_by
        if top is not UNSET:
            field_dict["top"] = top
        if skip is not UNSET:
            field_dict["skip"] = skip
        if select is not UNSET:
            field_dict["select"] = select
        if expand is not UNSET:
            field_dict["expand"] = expand
        if inline_count is not UNSET:
            field_dict["inlineCount"] = inline_count
        if format_ is not UNSET:
            field_dict["format"] = format_
        if skip_token is not UNSET:
            field_dict["skipToken"] = skip_token

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        filter_ = d.pop("filter", UNSET)

        order_by = d.pop("orderBy", UNSET)

        top = d.pop("top", UNSET)

        skip = d.pop("skip", UNSET)

        select = d.pop("select", UNSET)

        expand = d.pop("expand", UNSET)

        inline_count = d.pop("inlineCount", UNSET)

        format_ = d.pop("format", UNSET)

        skip_token = d.pop("skipToken", UNSET)

        o_data_raw_query_options = cls(
            filter_=filter_,
            order_by=order_by,
            top=top,
            skip=skip,
            select=select,
            expand=expand,
            inline_count=inline_count,
            format_=format_,
            skip_token=skip_token,
        )

        o_data_raw_query_options.additional_properties = d
        return o_data_raw_query_options

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
