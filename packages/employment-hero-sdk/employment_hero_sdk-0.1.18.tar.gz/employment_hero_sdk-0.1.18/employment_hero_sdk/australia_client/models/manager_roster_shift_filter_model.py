import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="ManagerRosterShiftFilterModel")


@_attrs_define
class ManagerRosterShiftFilterModel:
    """
    Attributes:
        date (Union[Unset, datetime.datetime]):
        employee_id (Union[Unset, int]):
        location_id (Union[Unset, int]):
        role_id (Union[Unset, int]):
        include_costs (Union[Unset, bool]):
        include_sub_locations (Union[Unset, bool]):
    """

    date: Union[Unset, datetime.datetime] = UNSET
    employee_id: Union[Unset, int] = UNSET
    location_id: Union[Unset, int] = UNSET
    role_id: Union[Unset, int] = UNSET
    include_costs: Union[Unset, bool] = UNSET
    include_sub_locations: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        date: Union[Unset, str] = UNSET
        if not isinstance(self.date, Unset):
            date = self.date.isoformat()

        employee_id = self.employee_id

        location_id = self.location_id

        role_id = self.role_id

        include_costs = self.include_costs

        include_sub_locations = self.include_sub_locations

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if date is not UNSET:
            field_dict["date"] = date
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if location_id is not UNSET:
            field_dict["locationId"] = location_id
        if role_id is not UNSET:
            field_dict["roleId"] = role_id
        if include_costs is not UNSET:
            field_dict["includeCosts"] = include_costs
        if include_sub_locations is not UNSET:
            field_dict["includeSubLocations"] = include_sub_locations

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _date = d.pop("date", UNSET)
        date: Union[Unset, datetime.datetime]
        if isinstance(_date, Unset):
            date = UNSET
        else:
            date = isoparse(_date)

        employee_id = d.pop("employeeId", UNSET)

        location_id = d.pop("locationId", UNSET)

        role_id = d.pop("roleId", UNSET)

        include_costs = d.pop("includeCosts", UNSET)

        include_sub_locations = d.pop("includeSubLocations", UNSET)

        manager_roster_shift_filter_model = cls(
            date=date,
            employee_id=employee_id,
            location_id=location_id,
            role_id=role_id,
            include_costs=include_costs,
            include_sub_locations=include_sub_locations,
        )

        manager_roster_shift_filter_model.additional_properties = d
        return manager_roster_shift_filter_model

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
