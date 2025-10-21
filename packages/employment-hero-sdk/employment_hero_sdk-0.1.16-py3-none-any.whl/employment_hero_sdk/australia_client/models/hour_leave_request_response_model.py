import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="HourLeaveRequestResponseModel")


@_attrs_define
class HourLeaveRequestResponseModel:
    """
    Attributes:
        total_hours (Union[Unset, float]):
        hours_applied (Union[Unset, float]):
        id (Union[Unset, int]):
        employee_id (Union[Unset, int]):
        leave_category_id (Union[Unset, int]):
        employee (Union[Unset, str]):
        leave_category (Union[Unset, str]):
        from_date (Union[Unset, datetime.datetime]):
        to_date (Union[Unset, datetime.datetime]):
        notes (Union[Unset, str]):
        status (Union[Unset, str]):
        attachment_id (Union[Unset, int]):
    """

    total_hours: Union[Unset, float] = UNSET
    hours_applied: Union[Unset, float] = UNSET
    id: Union[Unset, int] = UNSET
    employee_id: Union[Unset, int] = UNSET
    leave_category_id: Union[Unset, int] = UNSET
    employee: Union[Unset, str] = UNSET
    leave_category: Union[Unset, str] = UNSET
    from_date: Union[Unset, datetime.datetime] = UNSET
    to_date: Union[Unset, datetime.datetime] = UNSET
    notes: Union[Unset, str] = UNSET
    status: Union[Unset, str] = UNSET
    attachment_id: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        total_hours = self.total_hours

        hours_applied = self.hours_applied

        id = self.id

        employee_id = self.employee_id

        leave_category_id = self.leave_category_id

        employee = self.employee

        leave_category = self.leave_category

        from_date: Union[Unset, str] = UNSET
        if not isinstance(self.from_date, Unset):
            from_date = self.from_date.isoformat()

        to_date: Union[Unset, str] = UNSET
        if not isinstance(self.to_date, Unset):
            to_date = self.to_date.isoformat()

        notes = self.notes

        status = self.status

        attachment_id = self.attachment_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if total_hours is not UNSET:
            field_dict["totalHours"] = total_hours
        if hours_applied is not UNSET:
            field_dict["hoursApplied"] = hours_applied
        if id is not UNSET:
            field_dict["id"] = id
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if leave_category_id is not UNSET:
            field_dict["leaveCategoryId"] = leave_category_id
        if employee is not UNSET:
            field_dict["employee"] = employee
        if leave_category is not UNSET:
            field_dict["leaveCategory"] = leave_category
        if from_date is not UNSET:
            field_dict["fromDate"] = from_date
        if to_date is not UNSET:
            field_dict["toDate"] = to_date
        if notes is not UNSET:
            field_dict["notes"] = notes
        if status is not UNSET:
            field_dict["status"] = status
        if attachment_id is not UNSET:
            field_dict["attachmentId"] = attachment_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        total_hours = d.pop("totalHours", UNSET)

        hours_applied = d.pop("hoursApplied", UNSET)

        id = d.pop("id", UNSET)

        employee_id = d.pop("employeeId", UNSET)

        leave_category_id = d.pop("leaveCategoryId", UNSET)

        employee = d.pop("employee", UNSET)

        leave_category = d.pop("leaveCategory", UNSET)

        _from_date = d.pop("fromDate", UNSET)
        from_date: Union[Unset, datetime.datetime]
        if isinstance(_from_date, Unset):
            from_date = UNSET
        else:
            from_date = isoparse(_from_date)

        _to_date = d.pop("toDate", UNSET)
        to_date: Union[Unset, datetime.datetime]
        if isinstance(_to_date, Unset):
            to_date = UNSET
        else:
            to_date = isoparse(_to_date)

        notes = d.pop("notes", UNSET)

        status = d.pop("status", UNSET)

        attachment_id = d.pop("attachmentId", UNSET)

        hour_leave_request_response_model = cls(
            total_hours=total_hours,
            hours_applied=hours_applied,
            id=id,
            employee_id=employee_id,
            leave_category_id=leave_category_id,
            employee=employee,
            leave_category=leave_category,
            from_date=from_date,
            to_date=to_date,
            notes=notes,
            status=status,
            attachment_id=attachment_id,
        )

        hour_leave_request_response_model.additional_properties = d
        return hour_leave_request_response_model

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
