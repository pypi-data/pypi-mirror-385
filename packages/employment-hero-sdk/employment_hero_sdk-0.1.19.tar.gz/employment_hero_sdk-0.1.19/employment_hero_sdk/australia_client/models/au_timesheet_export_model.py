import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.timesheet_break_model import TimesheetBreakModel


T = TypeVar("T", bound="AuTimesheetExportModel")


@_attrs_define
class AuTimesheetExportModel:
    """
    Attributes:
        super_ (Union[Unset, float]):
        payg (Union[Unset, float]):
        classification (Union[Unset, str]):
        employee_id (Union[Unset, int]):
        first_name (Union[Unset, str]):
        surname (Union[Unset, str]):
        employee_external_id (Union[Unset, str]):
        id (Union[Unset, int]):
        status (Union[Unset, str]):
        location (Union[Unset, str]):
        start (Union[Unset, datetime.datetime]):
        start_time (Union[Unset, str]):
        end (Union[Unset, datetime.datetime]):
        end_time (Union[Unset, str]):
        actual_start (Union[Unset, datetime.datetime]):
        actual_start_time (Union[Unset, str]):
        actual_end (Union[Unset, datetime.datetime]):
        actual_end_time (Union[Unset, str]):
        time_variance (Union[Unset, str]):
        formatted_time_variance (Union[Unset, str]):
        duration_excluding_breaks (Union[Unset, str]):
        duration (Union[Unset, str]):
        units (Union[Unset, float]):
        unit_type (Union[Unset, str]):
        work_type (Union[Unset, str]):
        shift_conditions (Union[Unset, str]):
        number_of_breaks (Union[Unset, int]):
        break_duration (Union[Unset, str]):
        comments (Union[Unset, str]):
        consolidated_with_timesheet_line_id (Union[Unset, int]):
        reviewed_by (Union[Unset, str]):
        gross (Union[Unset, float]):
        net_earnings (Union[Unset, float]):
        employer_liabilities (Union[Unset, float]):
        total_cost (Union[Unset, float]):
        total_cost_variance (Union[Unset, float]):
        date_created (Union[Unset, datetime.datetime]):
        date_reviewed (Union[Unset, datetime.datetime]):
        shift_condition_short_codes (Union[Unset, List[str]]):
        breaks (Union[Unset, List['TimesheetBreakModel']]):
    """

    super_: Union[Unset, float] = UNSET
    payg: Union[Unset, float] = UNSET
    classification: Union[Unset, str] = UNSET
    employee_id: Union[Unset, int] = UNSET
    first_name: Union[Unset, str] = UNSET
    surname: Union[Unset, str] = UNSET
    employee_external_id: Union[Unset, str] = UNSET
    id: Union[Unset, int] = UNSET
    status: Union[Unset, str] = UNSET
    location: Union[Unset, str] = UNSET
    start: Union[Unset, datetime.datetime] = UNSET
    start_time: Union[Unset, str] = UNSET
    end: Union[Unset, datetime.datetime] = UNSET
    end_time: Union[Unset, str] = UNSET
    actual_start: Union[Unset, datetime.datetime] = UNSET
    actual_start_time: Union[Unset, str] = UNSET
    actual_end: Union[Unset, datetime.datetime] = UNSET
    actual_end_time: Union[Unset, str] = UNSET
    time_variance: Union[Unset, str] = UNSET
    formatted_time_variance: Union[Unset, str] = UNSET
    duration_excluding_breaks: Union[Unset, str] = UNSET
    duration: Union[Unset, str] = UNSET
    units: Union[Unset, float] = UNSET
    unit_type: Union[Unset, str] = UNSET
    work_type: Union[Unset, str] = UNSET
    shift_conditions: Union[Unset, str] = UNSET
    number_of_breaks: Union[Unset, int] = UNSET
    break_duration: Union[Unset, str] = UNSET
    comments: Union[Unset, str] = UNSET
    consolidated_with_timesheet_line_id: Union[Unset, int] = UNSET
    reviewed_by: Union[Unset, str] = UNSET
    gross: Union[Unset, float] = UNSET
    net_earnings: Union[Unset, float] = UNSET
    employer_liabilities: Union[Unset, float] = UNSET
    total_cost: Union[Unset, float] = UNSET
    total_cost_variance: Union[Unset, float] = UNSET
    date_created: Union[Unset, datetime.datetime] = UNSET
    date_reviewed: Union[Unset, datetime.datetime] = UNSET
    shift_condition_short_codes: Union[Unset, List[str]] = UNSET
    breaks: Union[Unset, List["TimesheetBreakModel"]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        super_ = self.super_

        payg = self.payg

        classification = self.classification

        employee_id = self.employee_id

        first_name = self.first_name

        surname = self.surname

        employee_external_id = self.employee_external_id

        id = self.id

        status = self.status

        location = self.location

        start: Union[Unset, str] = UNSET
        if not isinstance(self.start, Unset):
            start = self.start.isoformat()

        start_time = self.start_time

        end: Union[Unset, str] = UNSET
        if not isinstance(self.end, Unset):
            end = self.end.isoformat()

        end_time = self.end_time

        actual_start: Union[Unset, str] = UNSET
        if not isinstance(self.actual_start, Unset):
            actual_start = self.actual_start.isoformat()

        actual_start_time = self.actual_start_time

        actual_end: Union[Unset, str] = UNSET
        if not isinstance(self.actual_end, Unset):
            actual_end = self.actual_end.isoformat()

        actual_end_time = self.actual_end_time

        time_variance = self.time_variance

        formatted_time_variance = self.formatted_time_variance

        duration_excluding_breaks = self.duration_excluding_breaks

        duration = self.duration

        units = self.units

        unit_type = self.unit_type

        work_type = self.work_type

        shift_conditions = self.shift_conditions

        number_of_breaks = self.number_of_breaks

        break_duration = self.break_duration

        comments = self.comments

        consolidated_with_timesheet_line_id = self.consolidated_with_timesheet_line_id

        reviewed_by = self.reviewed_by

        gross = self.gross

        net_earnings = self.net_earnings

        employer_liabilities = self.employer_liabilities

        total_cost = self.total_cost

        total_cost_variance = self.total_cost_variance

        date_created: Union[Unset, str] = UNSET
        if not isinstance(self.date_created, Unset):
            date_created = self.date_created.isoformat()

        date_reviewed: Union[Unset, str] = UNSET
        if not isinstance(self.date_reviewed, Unset):
            date_reviewed = self.date_reviewed.isoformat()

        shift_condition_short_codes: Union[Unset, List[str]] = UNSET
        if not isinstance(self.shift_condition_short_codes, Unset):
            shift_condition_short_codes = self.shift_condition_short_codes

        breaks: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.breaks, Unset):
            breaks = []
            for breaks_item_data in self.breaks:
                breaks_item = breaks_item_data.to_dict()
                breaks.append(breaks_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if super_ is not UNSET:
            field_dict["super"] = super_
        if payg is not UNSET:
            field_dict["payg"] = payg
        if classification is not UNSET:
            field_dict["classification"] = classification
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if first_name is not UNSET:
            field_dict["firstName"] = first_name
        if surname is not UNSET:
            field_dict["surname"] = surname
        if employee_external_id is not UNSET:
            field_dict["employeeExternalId"] = employee_external_id
        if id is not UNSET:
            field_dict["id"] = id
        if status is not UNSET:
            field_dict["status"] = status
        if location is not UNSET:
            field_dict["location"] = location
        if start is not UNSET:
            field_dict["start"] = start
        if start_time is not UNSET:
            field_dict["startTime"] = start_time
        if end is not UNSET:
            field_dict["end"] = end
        if end_time is not UNSET:
            field_dict["endTime"] = end_time
        if actual_start is not UNSET:
            field_dict["actualStart"] = actual_start
        if actual_start_time is not UNSET:
            field_dict["actualStartTime"] = actual_start_time
        if actual_end is not UNSET:
            field_dict["actualEnd"] = actual_end
        if actual_end_time is not UNSET:
            field_dict["actualEndTime"] = actual_end_time
        if time_variance is not UNSET:
            field_dict["timeVariance"] = time_variance
        if formatted_time_variance is not UNSET:
            field_dict["formattedTimeVariance"] = formatted_time_variance
        if duration_excluding_breaks is not UNSET:
            field_dict["durationExcludingBreaks"] = duration_excluding_breaks
        if duration is not UNSET:
            field_dict["duration"] = duration
        if units is not UNSET:
            field_dict["units"] = units
        if unit_type is not UNSET:
            field_dict["unitType"] = unit_type
        if work_type is not UNSET:
            field_dict["workType"] = work_type
        if shift_conditions is not UNSET:
            field_dict["shiftConditions"] = shift_conditions
        if number_of_breaks is not UNSET:
            field_dict["numberOfBreaks"] = number_of_breaks
        if break_duration is not UNSET:
            field_dict["breakDuration"] = break_duration
        if comments is not UNSET:
            field_dict["comments"] = comments
        if consolidated_with_timesheet_line_id is not UNSET:
            field_dict["consolidatedWithTimesheetLineId"] = consolidated_with_timesheet_line_id
        if reviewed_by is not UNSET:
            field_dict["reviewedBy"] = reviewed_by
        if gross is not UNSET:
            field_dict["gross"] = gross
        if net_earnings is not UNSET:
            field_dict["netEarnings"] = net_earnings
        if employer_liabilities is not UNSET:
            field_dict["employerLiabilities"] = employer_liabilities
        if total_cost is not UNSET:
            field_dict["totalCost"] = total_cost
        if total_cost_variance is not UNSET:
            field_dict["totalCostVariance"] = total_cost_variance
        if date_created is not UNSET:
            field_dict["dateCreated"] = date_created
        if date_reviewed is not UNSET:
            field_dict["dateReviewed"] = date_reviewed
        if shift_condition_short_codes is not UNSET:
            field_dict["shiftConditionShortCodes"] = shift_condition_short_codes
        if breaks is not UNSET:
            field_dict["breaks"] = breaks

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.timesheet_break_model import TimesheetBreakModel

        d = src_dict.copy()
        super_ = d.pop("super", UNSET)

        payg = d.pop("payg", UNSET)

        classification = d.pop("classification", UNSET)

        employee_id = d.pop("employeeId", UNSET)

        first_name = d.pop("firstName", UNSET)

        surname = d.pop("surname", UNSET)

        employee_external_id = d.pop("employeeExternalId", UNSET)

        id = d.pop("id", UNSET)

        status = d.pop("status", UNSET)

        location = d.pop("location", UNSET)

        _start = d.pop("start", UNSET)
        start: Union[Unset, datetime.datetime]
        if isinstance(_start, Unset):
            start = UNSET
        else:
            start = isoparse(_start)

        start_time = d.pop("startTime", UNSET)

        _end = d.pop("end", UNSET)
        end: Union[Unset, datetime.datetime]
        if isinstance(_end, Unset):
            end = UNSET
        else:
            end = isoparse(_end)

        end_time = d.pop("endTime", UNSET)

        _actual_start = d.pop("actualStart", UNSET)
        actual_start: Union[Unset, datetime.datetime]
        if isinstance(_actual_start, Unset):
            actual_start = UNSET
        else:
            actual_start = isoparse(_actual_start)

        actual_start_time = d.pop("actualStartTime", UNSET)

        _actual_end = d.pop("actualEnd", UNSET)
        actual_end: Union[Unset, datetime.datetime]
        if isinstance(_actual_end, Unset):
            actual_end = UNSET
        else:
            actual_end = isoparse(_actual_end)

        actual_end_time = d.pop("actualEndTime", UNSET)

        time_variance = d.pop("timeVariance", UNSET)

        formatted_time_variance = d.pop("formattedTimeVariance", UNSET)

        duration_excluding_breaks = d.pop("durationExcludingBreaks", UNSET)

        duration = d.pop("duration", UNSET)

        units = d.pop("units", UNSET)

        unit_type = d.pop("unitType", UNSET)

        work_type = d.pop("workType", UNSET)

        shift_conditions = d.pop("shiftConditions", UNSET)

        number_of_breaks = d.pop("numberOfBreaks", UNSET)

        break_duration = d.pop("breakDuration", UNSET)

        comments = d.pop("comments", UNSET)

        consolidated_with_timesheet_line_id = d.pop("consolidatedWithTimesheetLineId", UNSET)

        reviewed_by = d.pop("reviewedBy", UNSET)

        gross = d.pop("gross", UNSET)

        net_earnings = d.pop("netEarnings", UNSET)

        employer_liabilities = d.pop("employerLiabilities", UNSET)

        total_cost = d.pop("totalCost", UNSET)

        total_cost_variance = d.pop("totalCostVariance", UNSET)

        _date_created = d.pop("dateCreated", UNSET)
        date_created: Union[Unset, datetime.datetime]
        if isinstance(_date_created, Unset):
            date_created = UNSET
        else:
            date_created = isoparse(_date_created)

        _date_reviewed = d.pop("dateReviewed", UNSET)
        date_reviewed: Union[Unset, datetime.datetime]
        if isinstance(_date_reviewed, Unset):
            date_reviewed = UNSET
        else:
            date_reviewed = isoparse(_date_reviewed)

        shift_condition_short_codes = cast(List[str], d.pop("shiftConditionShortCodes", UNSET))

        breaks = []
        _breaks = d.pop("breaks", UNSET)
        for breaks_item_data in _breaks or []:
            breaks_item = TimesheetBreakModel.from_dict(breaks_item_data)

            breaks.append(breaks_item)

        au_timesheet_export_model = cls(
            super_=super_,
            payg=payg,
            classification=classification,
            employee_id=employee_id,
            first_name=first_name,
            surname=surname,
            employee_external_id=employee_external_id,
            id=id,
            status=status,
            location=location,
            start=start,
            start_time=start_time,
            end=end,
            end_time=end_time,
            actual_start=actual_start,
            actual_start_time=actual_start_time,
            actual_end=actual_end,
            actual_end_time=actual_end_time,
            time_variance=time_variance,
            formatted_time_variance=formatted_time_variance,
            duration_excluding_breaks=duration_excluding_breaks,
            duration=duration,
            units=units,
            unit_type=unit_type,
            work_type=work_type,
            shift_conditions=shift_conditions,
            number_of_breaks=number_of_breaks,
            break_duration=break_duration,
            comments=comments,
            consolidated_with_timesheet_line_id=consolidated_with_timesheet_line_id,
            reviewed_by=reviewed_by,
            gross=gross,
            net_earnings=net_earnings,
            employer_liabilities=employer_liabilities,
            total_cost=total_cost,
            total_cost_variance=total_cost_variance,
            date_created=date_created,
            date_reviewed=date_reviewed,
            shift_condition_short_codes=shift_condition_short_codes,
            breaks=breaks,
        )

        au_timesheet_export_model.additional_properties = d
        return au_timesheet_export_model

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
