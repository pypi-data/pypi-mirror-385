import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="AuRosterTimesheetComparisonReportExportModel")


@_attrs_define
class AuRosterTimesheetComparisonReportExportModel:
    """
    Attributes:
        employment_type (Union[Unset, str]):
        employee_id (Union[Unset, int]):
        employee_first_name (Union[Unset, str]):
        employee_surname (Union[Unset, str]):
        employee_external_id (Union[Unset, str]):
        employee_default_location (Union[Unset, str]):
        pay_schedule_name (Union[Unset, str]):
        rostered_id (Union[Unset, int]):
        rostered_status (Union[Unset, str]):
        rostered_location (Union[Unset, str]):
        rostered_work_type (Union[Unset, str]):
        rostered_start (Union[Unset, datetime.datetime]):
        rostered_start_time (Union[Unset, str]):
        rostered_end (Union[Unset, datetime.datetime]):
        rostered_end_time (Union[Unset, str]):
        rostered_duration (Union[Unset, str]):
        rostered_breaks (Union[Unset, str]):
        rostered_cost (Union[Unset, float]):
        timesheet_id (Union[Unset, int]):
        timesheet_status (Union[Unset, str]):
        timesheet_location (Union[Unset, str]):
        timesheet_work_type (Union[Unset, str]):
        timesheet_start (Union[Unset, datetime.datetime]):
        timesheet_start_time (Union[Unset, str]):
        timesheet_end (Union[Unset, datetime.datetime]):
        timesheet_end_time (Union[Unset, str]):
        timesheet_duration (Union[Unset, str]):
        timesheet_breaks (Union[Unset, str]):
        timesheet_units (Union[Unset, float]):
        timesheet_unit_type (Union[Unset, str]):
        timesheet_cost (Union[Unset, float]):
        time_variance (Union[Unset, str]):
        cost_variance (Union[Unset, float]):
    """

    employment_type: Union[Unset, str] = UNSET
    employee_id: Union[Unset, int] = UNSET
    employee_first_name: Union[Unset, str] = UNSET
    employee_surname: Union[Unset, str] = UNSET
    employee_external_id: Union[Unset, str] = UNSET
    employee_default_location: Union[Unset, str] = UNSET
    pay_schedule_name: Union[Unset, str] = UNSET
    rostered_id: Union[Unset, int] = UNSET
    rostered_status: Union[Unset, str] = UNSET
    rostered_location: Union[Unset, str] = UNSET
    rostered_work_type: Union[Unset, str] = UNSET
    rostered_start: Union[Unset, datetime.datetime] = UNSET
    rostered_start_time: Union[Unset, str] = UNSET
    rostered_end: Union[Unset, datetime.datetime] = UNSET
    rostered_end_time: Union[Unset, str] = UNSET
    rostered_duration: Union[Unset, str] = UNSET
    rostered_breaks: Union[Unset, str] = UNSET
    rostered_cost: Union[Unset, float] = UNSET
    timesheet_id: Union[Unset, int] = UNSET
    timesheet_status: Union[Unset, str] = UNSET
    timesheet_location: Union[Unset, str] = UNSET
    timesheet_work_type: Union[Unset, str] = UNSET
    timesheet_start: Union[Unset, datetime.datetime] = UNSET
    timesheet_start_time: Union[Unset, str] = UNSET
    timesheet_end: Union[Unset, datetime.datetime] = UNSET
    timesheet_end_time: Union[Unset, str] = UNSET
    timesheet_duration: Union[Unset, str] = UNSET
    timesheet_breaks: Union[Unset, str] = UNSET
    timesheet_units: Union[Unset, float] = UNSET
    timesheet_unit_type: Union[Unset, str] = UNSET
    timesheet_cost: Union[Unset, float] = UNSET
    time_variance: Union[Unset, str] = UNSET
    cost_variance: Union[Unset, float] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        employment_type = self.employment_type

        employee_id = self.employee_id

        employee_first_name = self.employee_first_name

        employee_surname = self.employee_surname

        employee_external_id = self.employee_external_id

        employee_default_location = self.employee_default_location

        pay_schedule_name = self.pay_schedule_name

        rostered_id = self.rostered_id

        rostered_status = self.rostered_status

        rostered_location = self.rostered_location

        rostered_work_type = self.rostered_work_type

        rostered_start: Union[Unset, str] = UNSET
        if not isinstance(self.rostered_start, Unset):
            rostered_start = self.rostered_start.isoformat()

        rostered_start_time = self.rostered_start_time

        rostered_end: Union[Unset, str] = UNSET
        if not isinstance(self.rostered_end, Unset):
            rostered_end = self.rostered_end.isoformat()

        rostered_end_time = self.rostered_end_time

        rostered_duration = self.rostered_duration

        rostered_breaks = self.rostered_breaks

        rostered_cost = self.rostered_cost

        timesheet_id = self.timesheet_id

        timesheet_status = self.timesheet_status

        timesheet_location = self.timesheet_location

        timesheet_work_type = self.timesheet_work_type

        timesheet_start: Union[Unset, str] = UNSET
        if not isinstance(self.timesheet_start, Unset):
            timesheet_start = self.timesheet_start.isoformat()

        timesheet_start_time = self.timesheet_start_time

        timesheet_end: Union[Unset, str] = UNSET
        if not isinstance(self.timesheet_end, Unset):
            timesheet_end = self.timesheet_end.isoformat()

        timesheet_end_time = self.timesheet_end_time

        timesheet_duration = self.timesheet_duration

        timesheet_breaks = self.timesheet_breaks

        timesheet_units = self.timesheet_units

        timesheet_unit_type = self.timesheet_unit_type

        timesheet_cost = self.timesheet_cost

        time_variance = self.time_variance

        cost_variance = self.cost_variance

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if employment_type is not UNSET:
            field_dict["employmentType"] = employment_type
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if employee_first_name is not UNSET:
            field_dict["employeeFirstName"] = employee_first_name
        if employee_surname is not UNSET:
            field_dict["employeeSurname"] = employee_surname
        if employee_external_id is not UNSET:
            field_dict["employeeExternalId"] = employee_external_id
        if employee_default_location is not UNSET:
            field_dict["employeeDefaultLocation"] = employee_default_location
        if pay_schedule_name is not UNSET:
            field_dict["payScheduleName"] = pay_schedule_name
        if rostered_id is not UNSET:
            field_dict["rosteredId"] = rostered_id
        if rostered_status is not UNSET:
            field_dict["rosteredStatus"] = rostered_status
        if rostered_location is not UNSET:
            field_dict["rosteredLocation"] = rostered_location
        if rostered_work_type is not UNSET:
            field_dict["rosteredWorkType"] = rostered_work_type
        if rostered_start is not UNSET:
            field_dict["rosteredStart"] = rostered_start
        if rostered_start_time is not UNSET:
            field_dict["rosteredStartTime"] = rostered_start_time
        if rostered_end is not UNSET:
            field_dict["rosteredEnd"] = rostered_end
        if rostered_end_time is not UNSET:
            field_dict["rosteredEndTime"] = rostered_end_time
        if rostered_duration is not UNSET:
            field_dict["rosteredDuration"] = rostered_duration
        if rostered_breaks is not UNSET:
            field_dict["rosteredBreaks"] = rostered_breaks
        if rostered_cost is not UNSET:
            field_dict["rosteredCost"] = rostered_cost
        if timesheet_id is not UNSET:
            field_dict["timesheetId"] = timesheet_id
        if timesheet_status is not UNSET:
            field_dict["timesheetStatus"] = timesheet_status
        if timesheet_location is not UNSET:
            field_dict["timesheetLocation"] = timesheet_location
        if timesheet_work_type is not UNSET:
            field_dict["timesheetWorkType"] = timesheet_work_type
        if timesheet_start is not UNSET:
            field_dict["timesheetStart"] = timesheet_start
        if timesheet_start_time is not UNSET:
            field_dict["timesheetStartTime"] = timesheet_start_time
        if timesheet_end is not UNSET:
            field_dict["timesheetEnd"] = timesheet_end
        if timesheet_end_time is not UNSET:
            field_dict["timesheetEndTime"] = timesheet_end_time
        if timesheet_duration is not UNSET:
            field_dict["timesheetDuration"] = timesheet_duration
        if timesheet_breaks is not UNSET:
            field_dict["timesheetBreaks"] = timesheet_breaks
        if timesheet_units is not UNSET:
            field_dict["timesheetUnits"] = timesheet_units
        if timesheet_unit_type is not UNSET:
            field_dict["timesheetUnitType"] = timesheet_unit_type
        if timesheet_cost is not UNSET:
            field_dict["timesheetCost"] = timesheet_cost
        if time_variance is not UNSET:
            field_dict["timeVariance"] = time_variance
        if cost_variance is not UNSET:
            field_dict["costVariance"] = cost_variance

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        employment_type = d.pop("employmentType", UNSET)

        employee_id = d.pop("employeeId", UNSET)

        employee_first_name = d.pop("employeeFirstName", UNSET)

        employee_surname = d.pop("employeeSurname", UNSET)

        employee_external_id = d.pop("employeeExternalId", UNSET)

        employee_default_location = d.pop("employeeDefaultLocation", UNSET)

        pay_schedule_name = d.pop("payScheduleName", UNSET)

        rostered_id = d.pop("rosteredId", UNSET)

        rostered_status = d.pop("rosteredStatus", UNSET)

        rostered_location = d.pop("rosteredLocation", UNSET)

        rostered_work_type = d.pop("rosteredWorkType", UNSET)

        _rostered_start = d.pop("rosteredStart", UNSET)
        rostered_start: Union[Unset, datetime.datetime]
        if isinstance(_rostered_start, Unset):
            rostered_start = UNSET
        else:
            rostered_start = isoparse(_rostered_start)

        rostered_start_time = d.pop("rosteredStartTime", UNSET)

        _rostered_end = d.pop("rosteredEnd", UNSET)
        rostered_end: Union[Unset, datetime.datetime]
        if isinstance(_rostered_end, Unset):
            rostered_end = UNSET
        else:
            rostered_end = isoparse(_rostered_end)

        rostered_end_time = d.pop("rosteredEndTime", UNSET)

        rostered_duration = d.pop("rosteredDuration", UNSET)

        rostered_breaks = d.pop("rosteredBreaks", UNSET)

        rostered_cost = d.pop("rosteredCost", UNSET)

        timesheet_id = d.pop("timesheetId", UNSET)

        timesheet_status = d.pop("timesheetStatus", UNSET)

        timesheet_location = d.pop("timesheetLocation", UNSET)

        timesheet_work_type = d.pop("timesheetWorkType", UNSET)

        _timesheet_start = d.pop("timesheetStart", UNSET)
        timesheet_start: Union[Unset, datetime.datetime]
        if isinstance(_timesheet_start, Unset):
            timesheet_start = UNSET
        else:
            timesheet_start = isoparse(_timesheet_start)

        timesheet_start_time = d.pop("timesheetStartTime", UNSET)

        _timesheet_end = d.pop("timesheetEnd", UNSET)
        timesheet_end: Union[Unset, datetime.datetime]
        if isinstance(_timesheet_end, Unset):
            timesheet_end = UNSET
        else:
            timesheet_end = isoparse(_timesheet_end)

        timesheet_end_time = d.pop("timesheetEndTime", UNSET)

        timesheet_duration = d.pop("timesheetDuration", UNSET)

        timesheet_breaks = d.pop("timesheetBreaks", UNSET)

        timesheet_units = d.pop("timesheetUnits", UNSET)

        timesheet_unit_type = d.pop("timesheetUnitType", UNSET)

        timesheet_cost = d.pop("timesheetCost", UNSET)

        time_variance = d.pop("timeVariance", UNSET)

        cost_variance = d.pop("costVariance", UNSET)

        au_roster_timesheet_comparison_report_export_model = cls(
            employment_type=employment_type,
            employee_id=employee_id,
            employee_first_name=employee_first_name,
            employee_surname=employee_surname,
            employee_external_id=employee_external_id,
            employee_default_location=employee_default_location,
            pay_schedule_name=pay_schedule_name,
            rostered_id=rostered_id,
            rostered_status=rostered_status,
            rostered_location=rostered_location,
            rostered_work_type=rostered_work_type,
            rostered_start=rostered_start,
            rostered_start_time=rostered_start_time,
            rostered_end=rostered_end,
            rostered_end_time=rostered_end_time,
            rostered_duration=rostered_duration,
            rostered_breaks=rostered_breaks,
            rostered_cost=rostered_cost,
            timesheet_id=timesheet_id,
            timesheet_status=timesheet_status,
            timesheet_location=timesheet_location,
            timesheet_work_type=timesheet_work_type,
            timesheet_start=timesheet_start,
            timesheet_start_time=timesheet_start_time,
            timesheet_end=timesheet_end,
            timesheet_end_time=timesheet_end_time,
            timesheet_duration=timesheet_duration,
            timesheet_breaks=timesheet_breaks,
            timesheet_units=timesheet_units,
            timesheet_unit_type=timesheet_unit_type,
            timesheet_cost=timesheet_cost,
            time_variance=time_variance,
            cost_variance=cost_variance,
        )

        au_roster_timesheet_comparison_report_export_model.additional_properties = d
        return au_roster_timesheet_comparison_report_export_model

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
