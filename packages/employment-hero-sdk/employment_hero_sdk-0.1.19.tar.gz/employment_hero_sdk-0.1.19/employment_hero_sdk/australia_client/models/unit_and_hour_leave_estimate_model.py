from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UnitAndHourLeaveEstimateModel")


@_attrs_define
class UnitAndHourLeaveEstimateModel:
    """
    Attributes:
        hours (Union[Unset, float]):
        units (Union[Unset, float]):
        employee_id (Union[Unset, int]):
        details (Union[Unset, List[str]]):
    """

    hours: Union[Unset, float] = UNSET
    units: Union[Unset, float] = UNSET
    employee_id: Union[Unset, int] = UNSET
    details: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        hours = self.hours

        units = self.units

        employee_id = self.employee_id

        details: Union[Unset, List[str]] = UNSET
        if not isinstance(self.details, Unset):
            details = self.details

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if hours is not UNSET:
            field_dict["hours"] = hours
        if units is not UNSET:
            field_dict["units"] = units
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if details is not UNSET:
            field_dict["details"] = details

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        hours = d.pop("hours", UNSET)

        units = d.pop("units", UNSET)

        employee_id = d.pop("employeeId", UNSET)

        details = cast(List[str], d.pop("details", UNSET))

        unit_and_hour_leave_estimate_model = cls(
            hours=hours,
            units=units,
            employee_id=employee_id,
            details=details,
        )

        unit_and_hour_leave_estimate_model.additional_properties = d
        return unit_and_hour_leave_estimate_model

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
