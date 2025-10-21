from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.employee_item_count_model import EmployeeItemCountModel


T = TypeVar("T", bound="ManagerItemCountModel")


@_attrs_define
class ManagerItemCountModel:
    """
    Attributes:
        item_count (Union[Unset, int]):
        item_count_by_employee_id (Union[Unset, List['EmployeeItemCountModel']]):
    """

    item_count: Union[Unset, int] = UNSET
    item_count_by_employee_id: Union[Unset, List["EmployeeItemCountModel"]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        item_count = self.item_count

        item_count_by_employee_id: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.item_count_by_employee_id, Unset):
            item_count_by_employee_id = []
            for item_count_by_employee_id_item_data in self.item_count_by_employee_id:
                item_count_by_employee_id_item = item_count_by_employee_id_item_data.to_dict()
                item_count_by_employee_id.append(item_count_by_employee_id_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if item_count is not UNSET:
            field_dict["itemCount"] = item_count
        if item_count_by_employee_id is not UNSET:
            field_dict["itemCountByEmployeeId"] = item_count_by_employee_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.employee_item_count_model import EmployeeItemCountModel

        d = src_dict.copy()
        item_count = d.pop("itemCount", UNSET)

        item_count_by_employee_id = []
        _item_count_by_employee_id = d.pop("itemCountByEmployeeId", UNSET)
        for item_count_by_employee_id_item_data in _item_count_by_employee_id or []:
            item_count_by_employee_id_item = EmployeeItemCountModel.from_dict(item_count_by_employee_id_item_data)

            item_count_by_employee_id.append(item_count_by_employee_id_item)

        manager_item_count_model = cls(
            item_count=item_count,
            item_count_by_employee_id=item_count_by_employee_id,
        )

        manager_item_count_model.additional_properties = d
        return manager_item_count_model

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
