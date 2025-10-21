import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.timesheet_request_filter_model_nullable_timesheet_grouping import (
    TimesheetRequestFilterModelNullableTimesheetGrouping,
)
from ..models.timesheet_request_filter_model_nullable_timesheet_line_filter_status import (
    TimesheetRequestFilterModelNullableTimesheetLineFilterStatus,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="TimesheetRequestFilterModel")


@_attrs_define
class TimesheetRequestFilterModel:
    """
    Attributes:
        from_date (Union[Unset, datetime.datetime]):
        to_date (Union[Unset, datetime.datetime]):
        status (Union[Unset, TimesheetRequestFilterModelNullableTimesheetLineFilterStatus]):
        employee_id (Union[Unset, int]):
        employee_group_id (Union[Unset, int]):
        location_id (Union[Unset, int]):
        include_costs (Union[Unset, bool]):
        current_page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        order_by (Union[Unset, TimesheetRequestFilterModelNullableTimesheetGrouping]):
    """

    from_date: Union[Unset, datetime.datetime] = UNSET
    to_date: Union[Unset, datetime.datetime] = UNSET
    status: Union[Unset, TimesheetRequestFilterModelNullableTimesheetLineFilterStatus] = UNSET
    employee_id: Union[Unset, int] = UNSET
    employee_group_id: Union[Unset, int] = UNSET
    location_id: Union[Unset, int] = UNSET
    include_costs: Union[Unset, bool] = UNSET
    current_page: Union[Unset, int] = UNSET
    page_size: Union[Unset, int] = UNSET
    order_by: Union[Unset, TimesheetRequestFilterModelNullableTimesheetGrouping] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from_date: Union[Unset, str] = UNSET
        if not isinstance(self.from_date, Unset):
            from_date = self.from_date.isoformat()

        to_date: Union[Unset, str] = UNSET
        if not isinstance(self.to_date, Unset):
            to_date = self.to_date.isoformat()

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        employee_id = self.employee_id

        employee_group_id = self.employee_group_id

        location_id = self.location_id

        include_costs = self.include_costs

        current_page = self.current_page

        page_size = self.page_size

        order_by: Union[Unset, str] = UNSET
        if not isinstance(self.order_by, Unset):
            order_by = self.order_by.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if from_date is not UNSET:
            field_dict["fromDate"] = from_date
        if to_date is not UNSET:
            field_dict["toDate"] = to_date
        if status is not UNSET:
            field_dict["status"] = status
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if employee_group_id is not UNSET:
            field_dict["employeeGroupId"] = employee_group_id
        if location_id is not UNSET:
            field_dict["locationId"] = location_id
        if include_costs is not UNSET:
            field_dict["includeCosts"] = include_costs
        if current_page is not UNSET:
            field_dict["currentPage"] = current_page
        if page_size is not UNSET:
            field_dict["pageSize"] = page_size
        if order_by is not UNSET:
            field_dict["orderBy"] = order_by

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
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

        _status = d.pop("status", UNSET)
        status: Union[Unset, TimesheetRequestFilterModelNullableTimesheetLineFilterStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = TimesheetRequestFilterModelNullableTimesheetLineFilterStatus(_status)

        employee_id = d.pop("employeeId", UNSET)

        employee_group_id = d.pop("employeeGroupId", UNSET)

        location_id = d.pop("locationId", UNSET)

        include_costs = d.pop("includeCosts", UNSET)

        current_page = d.pop("currentPage", UNSET)

        page_size = d.pop("pageSize", UNSET)

        _order_by = d.pop("orderBy", UNSET)
        order_by: Union[Unset, TimesheetRequestFilterModelNullableTimesheetGrouping]
        if isinstance(_order_by, Unset):
            order_by = UNSET
        else:
            order_by = TimesheetRequestFilterModelNullableTimesheetGrouping(_order_by)

        timesheet_request_filter_model = cls(
            from_date=from_date,
            to_date=to_date,
            status=status,
            employee_id=employee_id,
            employee_group_id=employee_group_id,
            location_id=location_id,
            include_costs=include_costs,
            current_page=current_page,
            page_size=page_size,
            order_by=order_by,
        )

        timesheet_request_filter_model.additional_properties = d
        return timesheet_request_filter_model

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
