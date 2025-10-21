import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="TerminateEmployeeRequest")


@_attrs_define
class TerminateEmployeeRequest:
    """
    Attributes:
        employee_id (Union[Unset, int]):
        termination_reason (Union[Unset, str]):
        termination_date (Union[Unset, datetime.datetime]):
    """

    employee_id: Union[Unset, int] = UNSET
    termination_reason: Union[Unset, str] = UNSET
    termination_date: Union[Unset, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        employee_id = self.employee_id

        termination_reason = self.termination_reason

        termination_date: Union[Unset, str] = UNSET
        if not isinstance(self.termination_date, Unset):
            termination_date = self.termination_date.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if termination_reason is not UNSET:
            field_dict["terminationReason"] = termination_reason
        if termination_date is not UNSET:
            field_dict["terminationDate"] = termination_date

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        employee_id = d.pop("employeeId", UNSET)

        termination_reason = d.pop("terminationReason", UNSET)

        _termination_date = d.pop("terminationDate", UNSET)
        termination_date: Union[Unset, datetime.datetime]
        if isinstance(_termination_date, Unset):
            termination_date = UNSET
        else:
            termination_date = isoparse(_termination_date)

        terminate_employee_request = cls(
            employee_id=employee_id,
            termination_reason=termination_reason,
            termination_date=termination_date,
        )

        terminate_employee_request.additional_properties = d
        return terminate_employee_request

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
