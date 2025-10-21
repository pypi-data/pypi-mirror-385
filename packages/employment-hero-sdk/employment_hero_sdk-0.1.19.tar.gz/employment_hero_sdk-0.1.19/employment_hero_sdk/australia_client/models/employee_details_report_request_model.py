from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="EmployeeDetailsReportRequestModel")


@_attrs_define
class EmployeeDetailsReportRequestModel:
    """
    Attributes:
        selected_columns (Union[Unset, List[str]]):
        location_id (Union[Unset, int]):
        employing_entity_id (Union[Unset, int]):
        include_active (Union[Unset, bool]):
        include_inactive (Union[Unset, bool]):
    """

    selected_columns: Union[Unset, List[str]] = UNSET
    location_id: Union[Unset, int] = UNSET
    employing_entity_id: Union[Unset, int] = UNSET
    include_active: Union[Unset, bool] = UNSET
    include_inactive: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        selected_columns: Union[Unset, List[str]] = UNSET
        if not isinstance(self.selected_columns, Unset):
            selected_columns = self.selected_columns

        location_id = self.location_id

        employing_entity_id = self.employing_entity_id

        include_active = self.include_active

        include_inactive = self.include_inactive

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if selected_columns is not UNSET:
            field_dict["selectedColumns"] = selected_columns
        if location_id is not UNSET:
            field_dict["locationId"] = location_id
        if employing_entity_id is not UNSET:
            field_dict["employingEntityId"] = employing_entity_id
        if include_active is not UNSET:
            field_dict["includeActive"] = include_active
        if include_inactive is not UNSET:
            field_dict["includeInactive"] = include_inactive

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        selected_columns = cast(List[str], d.pop("selectedColumns", UNSET))

        location_id = d.pop("locationId", UNSET)

        employing_entity_id = d.pop("employingEntityId", UNSET)

        include_active = d.pop("includeActive", UNSET)

        include_inactive = d.pop("includeInactive", UNSET)

        employee_details_report_request_model = cls(
            selected_columns=selected_columns,
            location_id=location_id,
            employing_entity_id=employing_entity_id,
            include_active=include_active,
            include_inactive=include_inactive,
        )

        employee_details_report_request_model.additional_properties = d
        return employee_details_report_request_model

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
