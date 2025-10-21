from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkTypeSelectModel")


@_attrs_define
class WorkTypeSelectModel:
    """
    Attributes:
        is_unit_based (Union[Unset, bool]):
        is_leave_type (Union[Unset, bool]):
        unit_type (Union[Unset, str]):
        business_award_package_id (Union[Unset, int]):
        id (Union[Unset, int]):
        description (Union[Unset, str]):
    """

    is_unit_based: Union[Unset, bool] = UNSET
    is_leave_type: Union[Unset, bool] = UNSET
    unit_type: Union[Unset, str] = UNSET
    business_award_package_id: Union[Unset, int] = UNSET
    id: Union[Unset, int] = UNSET
    description: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        is_unit_based = self.is_unit_based

        is_leave_type = self.is_leave_type

        unit_type = self.unit_type

        business_award_package_id = self.business_award_package_id

        id = self.id

        description = self.description

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if is_unit_based is not UNSET:
            field_dict["isUnitBased"] = is_unit_based
        if is_leave_type is not UNSET:
            field_dict["isLeaveType"] = is_leave_type
        if unit_type is not UNSET:
            field_dict["unitType"] = unit_type
        if business_award_package_id is not UNSET:
            field_dict["businessAwardPackageId"] = business_award_package_id
        if id is not UNSET:
            field_dict["id"] = id
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        is_unit_based = d.pop("isUnitBased", UNSET)

        is_leave_type = d.pop("isLeaveType", UNSET)

        unit_type = d.pop("unitType", UNSET)

        business_award_package_id = d.pop("businessAwardPackageId", UNSET)

        id = d.pop("id", UNSET)

        description = d.pop("description", UNSET)

        work_type_select_model = cls(
            is_unit_based=is_unit_based,
            is_leave_type=is_leave_type,
            unit_type=unit_type,
            business_award_package_id=business_award_package_id,
            id=id,
            description=description,
        )

        work_type_select_model.additional_properties = d
        return work_type_select_model

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
