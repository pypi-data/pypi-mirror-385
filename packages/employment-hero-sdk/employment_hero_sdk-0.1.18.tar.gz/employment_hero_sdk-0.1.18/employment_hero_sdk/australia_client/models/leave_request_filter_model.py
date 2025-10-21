import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.leave_request_filter_model_leave_request_group_by import LeaveRequestFilterModelLeaveRequestGroupBy
from ..models.leave_request_filter_model_nullable_leave_request_status import (
    LeaveRequestFilterModelNullableLeaveRequestStatus,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="LeaveRequestFilterModel")


@_attrs_define
class LeaveRequestFilterModel:
    """
    Attributes:
        status (Union[Unset, LeaveRequestFilterModelNullableLeaveRequestStatus]):
        from_date (Union[Unset, datetime.datetime]):
        to_date (Union[Unset, datetime.datetime]):
        leave_category_id (Union[Unset, int]):
        location_id (Union[Unset, int]):
        employee_id (Union[Unset, int]):
        group_by (Union[Unset, LeaveRequestFilterModelLeaveRequestGroupBy]):
        restrict_overlapping_leave (Union[Unset, bool]):
    """

    status: Union[Unset, LeaveRequestFilterModelNullableLeaveRequestStatus] = UNSET
    from_date: Union[Unset, datetime.datetime] = UNSET
    to_date: Union[Unset, datetime.datetime] = UNSET
    leave_category_id: Union[Unset, int] = UNSET
    location_id: Union[Unset, int] = UNSET
    employee_id: Union[Unset, int] = UNSET
    group_by: Union[Unset, LeaveRequestFilterModelLeaveRequestGroupBy] = UNSET
    restrict_overlapping_leave: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        from_date: Union[Unset, str] = UNSET
        if not isinstance(self.from_date, Unset):
            from_date = self.from_date.isoformat()

        to_date: Union[Unset, str] = UNSET
        if not isinstance(self.to_date, Unset):
            to_date = self.to_date.isoformat()

        leave_category_id = self.leave_category_id

        location_id = self.location_id

        employee_id = self.employee_id

        group_by: Union[Unset, str] = UNSET
        if not isinstance(self.group_by, Unset):
            group_by = self.group_by.value

        restrict_overlapping_leave = self.restrict_overlapping_leave

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if status is not UNSET:
            field_dict["status"] = status
        if from_date is not UNSET:
            field_dict["fromDate"] = from_date
        if to_date is not UNSET:
            field_dict["toDate"] = to_date
        if leave_category_id is not UNSET:
            field_dict["leaveCategoryId"] = leave_category_id
        if location_id is not UNSET:
            field_dict["locationId"] = location_id
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if group_by is not UNSET:
            field_dict["groupBy"] = group_by
        if restrict_overlapping_leave is not UNSET:
            field_dict["restrictOverlappingLeave"] = restrict_overlapping_leave

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _status = d.pop("status", UNSET)
        status: Union[Unset, LeaveRequestFilterModelNullableLeaveRequestStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = LeaveRequestFilterModelNullableLeaveRequestStatus(_status)

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

        leave_category_id = d.pop("leaveCategoryId", UNSET)

        location_id = d.pop("locationId", UNSET)

        employee_id = d.pop("employeeId", UNSET)

        _group_by = d.pop("groupBy", UNSET)
        group_by: Union[Unset, LeaveRequestFilterModelLeaveRequestGroupBy]
        if isinstance(_group_by, Unset):
            group_by = UNSET
        else:
            group_by = LeaveRequestFilterModelLeaveRequestGroupBy(_group_by)

        restrict_overlapping_leave = d.pop("restrictOverlappingLeave", UNSET)

        leave_request_filter_model = cls(
            status=status,
            from_date=from_date,
            to_date=to_date,
            leave_category_id=leave_category_id,
            location_id=location_id,
            employee_id=employee_id,
            group_by=group_by,
            restrict_overlapping_leave=restrict_overlapping_leave,
        )

        leave_request_filter_model.additional_properties = d
        return leave_request_filter_model

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
