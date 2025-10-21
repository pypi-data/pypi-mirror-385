from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.i_future_value_int_32 import IFutureValueInt32
    from ..models.manager_timesheet_line_model import ManagerTimesheetLineModel


T = TypeVar("T", bound="PagedResultModelManagerTimesheetLineModel")


@_attrs_define
class PagedResultModelManagerTimesheetLineModel:
    """
    Attributes:
        item_count_future (Union[Unset, IFutureValueInt32]):
        item_count (Union[Unset, int]):
        items (Union[Unset, List['ManagerTimesheetLineModel']]):
        current_page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        page_count (Union[Unset, int]):
    """

    item_count_future: Union[Unset, "IFutureValueInt32"] = UNSET
    item_count: Union[Unset, int] = UNSET
    items: Union[Unset, List["ManagerTimesheetLineModel"]] = UNSET
    current_page: Union[Unset, int] = UNSET
    page_size: Union[Unset, int] = UNSET
    page_count: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        item_count_future: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.item_count_future, Unset):
            item_count_future = self.item_count_future.to_dict()

        item_count = self.item_count

        items: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.items, Unset):
            items = []
            for items_item_data in self.items:
                items_item = items_item_data.to_dict()
                items.append(items_item)

        current_page = self.current_page

        page_size = self.page_size

        page_count = self.page_count

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if item_count_future is not UNSET:
            field_dict["itemCountFuture"] = item_count_future
        if item_count is not UNSET:
            field_dict["itemCount"] = item_count
        if items is not UNSET:
            field_dict["items"] = items
        if current_page is not UNSET:
            field_dict["currentPage"] = current_page
        if page_size is not UNSET:
            field_dict["pageSize"] = page_size
        if page_count is not UNSET:
            field_dict["pageCount"] = page_count

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.i_future_value_int_32 import IFutureValueInt32
        from ..models.manager_timesheet_line_model import ManagerTimesheetLineModel

        d = src_dict.copy()
        _item_count_future = d.pop("itemCountFuture", UNSET)
        item_count_future: Union[Unset, IFutureValueInt32]
        if isinstance(_item_count_future, Unset):
            item_count_future = UNSET
        else:
            item_count_future = IFutureValueInt32.from_dict(_item_count_future)

        item_count = d.pop("itemCount", UNSET)

        items = []
        _items = d.pop("items", UNSET)
        for items_item_data in _items or []:
            items_item = ManagerTimesheetLineModel.from_dict(items_item_data)

            items.append(items_item)

        current_page = d.pop("currentPage", UNSET)

        page_size = d.pop("pageSize", UNSET)

        page_count = d.pop("pageCount", UNSET)

        paged_result_model_manager_timesheet_line_model = cls(
            item_count_future=item_count_future,
            item_count=item_count,
            items=items,
            current_page=current_page,
            page_size=page_size,
            page_count=page_count,
        )

        paged_result_model_manager_timesheet_line_model.additional_properties = d
        return paged_result_model_manager_timesheet_line_model

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
