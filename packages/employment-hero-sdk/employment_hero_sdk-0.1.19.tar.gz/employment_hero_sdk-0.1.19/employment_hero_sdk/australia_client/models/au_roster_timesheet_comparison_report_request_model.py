import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.au_roster_timesheet_comparison_report_request_model_roster_shift_status import (
    AuRosterTimesheetComparisonReportRequestModelRosterShiftStatus,
)
from ..models.au_roster_timesheet_comparison_report_request_model_timesheet_line_status_type import (
    AuRosterTimesheetComparisonReportRequestModelTimesheetLineStatusType,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="AuRosterTimesheetComparisonReportRequestModel")


@_attrs_define
class AuRosterTimesheetComparisonReportRequestModel:
    """
    Attributes:
        employment_type_id (Union[Unset, int]):
        employee_id (Union[Unset, int]):
        include_costs (Union[Unset, bool]):
        timesheet_statuses (Union[Unset, List[AuRosterTimesheetComparisonReportRequestModelTimesheetLineStatusType]]):
        work_type_id (Union[Unset, int]):
        roster_location_id (Union[Unset, int]):
        timesheet_location_id (Union[Unset, int]):
        roster_statuses (Union[Unset, List[AuRosterTimesheetComparisonReportRequestModelRosterShiftStatus]]):
        pay_schedule_id (Union[Unset, int]):
        include_post_tax_deductions (Union[Unset, bool]):
        from_date (Union[Unset, datetime.datetime]):
        to_date (Union[Unset, datetime.datetime]):
        location_id (Union[Unset, int]):
        employing_entity_id (Union[Unset, int]):
    """

    employment_type_id: Union[Unset, int] = UNSET
    employee_id: Union[Unset, int] = UNSET
    include_costs: Union[Unset, bool] = UNSET
    timesheet_statuses: Union[Unset, List[AuRosterTimesheetComparisonReportRequestModelTimesheetLineStatusType]] = UNSET
    work_type_id: Union[Unset, int] = UNSET
    roster_location_id: Union[Unset, int] = UNSET
    timesheet_location_id: Union[Unset, int] = UNSET
    roster_statuses: Union[Unset, List[AuRosterTimesheetComparisonReportRequestModelRosterShiftStatus]] = UNSET
    pay_schedule_id: Union[Unset, int] = UNSET
    include_post_tax_deductions: Union[Unset, bool] = UNSET
    from_date: Union[Unset, datetime.datetime] = UNSET
    to_date: Union[Unset, datetime.datetime] = UNSET
    location_id: Union[Unset, int] = UNSET
    employing_entity_id: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        employment_type_id = self.employment_type_id

        employee_id = self.employee_id

        include_costs = self.include_costs

        timesheet_statuses: Union[Unset, List[str]] = UNSET
        if not isinstance(self.timesheet_statuses, Unset):
            timesheet_statuses = []
            for timesheet_statuses_item_data in self.timesheet_statuses:
                timesheet_statuses_item = timesheet_statuses_item_data.value
                timesheet_statuses.append(timesheet_statuses_item)

        work_type_id = self.work_type_id

        roster_location_id = self.roster_location_id

        timesheet_location_id = self.timesheet_location_id

        roster_statuses: Union[Unset, List[str]] = UNSET
        if not isinstance(self.roster_statuses, Unset):
            roster_statuses = []
            for roster_statuses_item_data in self.roster_statuses:
                roster_statuses_item = roster_statuses_item_data.value
                roster_statuses.append(roster_statuses_item)

        pay_schedule_id = self.pay_schedule_id

        include_post_tax_deductions = self.include_post_tax_deductions

        from_date: Union[Unset, str] = UNSET
        if not isinstance(self.from_date, Unset):
            from_date = self.from_date.isoformat()

        to_date: Union[Unset, str] = UNSET
        if not isinstance(self.to_date, Unset):
            to_date = self.to_date.isoformat()

        location_id = self.location_id

        employing_entity_id = self.employing_entity_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if employment_type_id is not UNSET:
            field_dict["employmentTypeId"] = employment_type_id
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if include_costs is not UNSET:
            field_dict["includeCosts"] = include_costs
        if timesheet_statuses is not UNSET:
            field_dict["timesheetStatuses"] = timesheet_statuses
        if work_type_id is not UNSET:
            field_dict["workTypeId"] = work_type_id
        if roster_location_id is not UNSET:
            field_dict["rosterLocationId"] = roster_location_id
        if timesheet_location_id is not UNSET:
            field_dict["timesheetLocationId"] = timesheet_location_id
        if roster_statuses is not UNSET:
            field_dict["rosterStatuses"] = roster_statuses
        if pay_schedule_id is not UNSET:
            field_dict["payScheduleId"] = pay_schedule_id
        if include_post_tax_deductions is not UNSET:
            field_dict["includePostTaxDeductions"] = include_post_tax_deductions
        if from_date is not UNSET:
            field_dict["fromDate"] = from_date
        if to_date is not UNSET:
            field_dict["toDate"] = to_date
        if location_id is not UNSET:
            field_dict["locationId"] = location_id
        if employing_entity_id is not UNSET:
            field_dict["employingEntityId"] = employing_entity_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        employment_type_id = d.pop("employmentTypeId", UNSET)

        employee_id = d.pop("employeeId", UNSET)

        include_costs = d.pop("includeCosts", UNSET)

        timesheet_statuses = []
        _timesheet_statuses = d.pop("timesheetStatuses", UNSET)
        for timesheet_statuses_item_data in _timesheet_statuses or []:
            timesheet_statuses_item = AuRosterTimesheetComparisonReportRequestModelTimesheetLineStatusType(
                timesheet_statuses_item_data
            )

            timesheet_statuses.append(timesheet_statuses_item)

        work_type_id = d.pop("workTypeId", UNSET)

        roster_location_id = d.pop("rosterLocationId", UNSET)

        timesheet_location_id = d.pop("timesheetLocationId", UNSET)

        roster_statuses = []
        _roster_statuses = d.pop("rosterStatuses", UNSET)
        for roster_statuses_item_data in _roster_statuses or []:
            roster_statuses_item = AuRosterTimesheetComparisonReportRequestModelRosterShiftStatus(
                roster_statuses_item_data
            )

            roster_statuses.append(roster_statuses_item)

        pay_schedule_id = d.pop("payScheduleId", UNSET)

        include_post_tax_deductions = d.pop("includePostTaxDeductions", UNSET)

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

        location_id = d.pop("locationId", UNSET)

        employing_entity_id = d.pop("employingEntityId", UNSET)

        au_roster_timesheet_comparison_report_request_model = cls(
            employment_type_id=employment_type_id,
            employee_id=employee_id,
            include_costs=include_costs,
            timesheet_statuses=timesheet_statuses,
            work_type_id=work_type_id,
            roster_location_id=roster_location_id,
            timesheet_location_id=timesheet_location_id,
            roster_statuses=roster_statuses,
            pay_schedule_id=pay_schedule_id,
            include_post_tax_deductions=include_post_tax_deductions,
            from_date=from_date,
            to_date=to_date,
            location_id=location_id,
            employing_entity_id=employing_entity_id,
        )

        au_roster_timesheet_comparison_report_request_model.additional_properties = d
        return au_roster_timesheet_comparison_report_request_model

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
