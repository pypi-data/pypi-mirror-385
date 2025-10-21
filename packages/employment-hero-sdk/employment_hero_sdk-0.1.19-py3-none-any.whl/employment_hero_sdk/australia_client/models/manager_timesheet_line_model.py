import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.manager_timesheet_line_model_external_service import ManagerTimesheetLineModelExternalService
from ..models.manager_timesheet_line_model_timesheet_line_status_type import (
    ManagerTimesheetLineModelTimesheetLineStatusType,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.attachment_model import AttachmentModel
    from ..models.classification_selection import ClassificationSelection
    from ..models.manager_employee_group import ManagerEmployeeGroup
    from ..models.reporting_dimension_value_base_api_model import ReportingDimensionValueBaseApiModel
    from ..models.shift_condition import ShiftCondition
    from ..models.timesheet_break_manager_model import TimesheetBreakManagerModel


T = TypeVar("T", bound="ManagerTimesheetLineModel")


@_attrs_define
class ManagerTimesheetLineModel:
    """
    Attributes:
        default_location_id (Union[Unset, int]):
        default_location_name (Union[Unset, str]):
        pay_schedule_id (Union[Unset, int]):
        pay_schedule_name (Union[Unset, str]):
        employee_groups (Union[Unset, List['ManagerEmployeeGroup']]):
        shift_conditions (Union[Unset, List['ShiftCondition']]):
        cost_formatted (Union[Unset, str]):
        can_delete (Union[Unset, bool]):
        can_edit (Union[Unset, bool]):
        can_edit_notes_only (Union[Unset, bool]):
        can_view_costs (Union[Unset, bool]):
        can_approve (Union[Unset, bool]):
        termination_date (Union[Unset, datetime.datetime]):
        employee_start_date (Union[Unset, datetime.datetime]):
        dimension_values (Union[Unset, List['ReportingDimensionValueBaseApiModel']]):
        classification (Union[Unset, ClassificationSelection]):
        employee_name (Union[Unset, str]):
        id (Union[Unset, int]):
        employee_id (Union[Unset, int]):
        location_id (Union[Unset, int]):
        work_type_id (Union[Unset, int]):
        work_type_name (Union[Unset, str]):
        location_name (Union[Unset, str]):
        unit_type (Union[Unset, str]):
        is_unit_based_work_type (Union[Unset, bool]):
        pay_run_id (Union[Unset, int]):
        start (Union[Unset, datetime.datetime]):
        end (Union[Unset, datetime.datetime]):
        submitted_start (Union[Unset, datetime.datetime]):
        submitted_end (Union[Unset, datetime.datetime]):
        units (Union[Unset, float]):
        status (Union[Unset, ManagerTimesheetLineModelTimesheetLineStatusType]):
        pay_slip_url (Union[Unset, str]):
        breaks (Union[Unset, List['TimesheetBreakManagerModel']]):
        comments (Union[Unset, str]):
        rate (Union[Unset, float]):
        external_reference_id (Union[Unset, str]):
        source (Union[Unset, ManagerTimesheetLineModelExternalService]):
        pay_category_id (Union[Unset, int]):
        leave_category_id (Union[Unset, int]):
        leave_request_id (Union[Unset, int]):
        is_locked (Union[Unset, bool]):
        cost (Union[Unset, float]):
        discard (Union[Unset, bool]):
        attachment (Union[Unset, AttachmentModel]):
        is_overlapping (Union[Unset, bool]):
        overdraws_leave (Union[Unset, bool]):
        reviewed_by (Union[Unset, str]):
        duration_override (Union[Unset, str]):
        auto_approved_by_roster_shift_id (Union[Unset, int]):
        work_duration_in_minutes (Union[Unset, float]):
        breaks_duration_in_minutes (Union[Unset, float]):
        total_duration_in_minutes (Union[Unset, float]):
        hidden_comments (Union[Unset, str]):
        read_only (Union[Unset, bool]):
        ignore_rounding (Union[Unset, bool]):
    """

    default_location_id: Union[Unset, int] = UNSET
    default_location_name: Union[Unset, str] = UNSET
    pay_schedule_id: Union[Unset, int] = UNSET
    pay_schedule_name: Union[Unset, str] = UNSET
    employee_groups: Union[Unset, List["ManagerEmployeeGroup"]] = UNSET
    shift_conditions: Union[Unset, List["ShiftCondition"]] = UNSET
    cost_formatted: Union[Unset, str] = UNSET
    can_delete: Union[Unset, bool] = UNSET
    can_edit: Union[Unset, bool] = UNSET
    can_edit_notes_only: Union[Unset, bool] = UNSET
    can_view_costs: Union[Unset, bool] = UNSET
    can_approve: Union[Unset, bool] = UNSET
    termination_date: Union[Unset, datetime.datetime] = UNSET
    employee_start_date: Union[Unset, datetime.datetime] = UNSET
    dimension_values: Union[Unset, List["ReportingDimensionValueBaseApiModel"]] = UNSET
    classification: Union[Unset, "ClassificationSelection"] = UNSET
    employee_name: Union[Unset, str] = UNSET
    id: Union[Unset, int] = UNSET
    employee_id: Union[Unset, int] = UNSET
    location_id: Union[Unset, int] = UNSET
    work_type_id: Union[Unset, int] = UNSET
    work_type_name: Union[Unset, str] = UNSET
    location_name: Union[Unset, str] = UNSET
    unit_type: Union[Unset, str] = UNSET
    is_unit_based_work_type: Union[Unset, bool] = UNSET
    pay_run_id: Union[Unset, int] = UNSET
    start: Union[Unset, datetime.datetime] = UNSET
    end: Union[Unset, datetime.datetime] = UNSET
    submitted_start: Union[Unset, datetime.datetime] = UNSET
    submitted_end: Union[Unset, datetime.datetime] = UNSET
    units: Union[Unset, float] = UNSET
    status: Union[Unset, ManagerTimesheetLineModelTimesheetLineStatusType] = UNSET
    pay_slip_url: Union[Unset, str] = UNSET
    breaks: Union[Unset, List["TimesheetBreakManagerModel"]] = UNSET
    comments: Union[Unset, str] = UNSET
    rate: Union[Unset, float] = UNSET
    external_reference_id: Union[Unset, str] = UNSET
    source: Union[Unset, ManagerTimesheetLineModelExternalService] = UNSET
    pay_category_id: Union[Unset, int] = UNSET
    leave_category_id: Union[Unset, int] = UNSET
    leave_request_id: Union[Unset, int] = UNSET
    is_locked: Union[Unset, bool] = UNSET
    cost: Union[Unset, float] = UNSET
    discard: Union[Unset, bool] = UNSET
    attachment: Union[Unset, "AttachmentModel"] = UNSET
    is_overlapping: Union[Unset, bool] = UNSET
    overdraws_leave: Union[Unset, bool] = UNSET
    reviewed_by: Union[Unset, str] = UNSET
    duration_override: Union[Unset, str] = UNSET
    auto_approved_by_roster_shift_id: Union[Unset, int] = UNSET
    work_duration_in_minutes: Union[Unset, float] = UNSET
    breaks_duration_in_minutes: Union[Unset, float] = UNSET
    total_duration_in_minutes: Union[Unset, float] = UNSET
    hidden_comments: Union[Unset, str] = UNSET
    read_only: Union[Unset, bool] = UNSET
    ignore_rounding: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        default_location_id = self.default_location_id

        default_location_name = self.default_location_name

        pay_schedule_id = self.pay_schedule_id

        pay_schedule_name = self.pay_schedule_name

        employee_groups: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.employee_groups, Unset):
            employee_groups = []
            for employee_groups_item_data in self.employee_groups:
                employee_groups_item = employee_groups_item_data.to_dict()
                employee_groups.append(employee_groups_item)

        shift_conditions: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.shift_conditions, Unset):
            shift_conditions = []
            for shift_conditions_item_data in self.shift_conditions:
                shift_conditions_item = shift_conditions_item_data.to_dict()
                shift_conditions.append(shift_conditions_item)

        cost_formatted = self.cost_formatted

        can_delete = self.can_delete

        can_edit = self.can_edit

        can_edit_notes_only = self.can_edit_notes_only

        can_view_costs = self.can_view_costs

        can_approve = self.can_approve

        termination_date: Union[Unset, str] = UNSET
        if not isinstance(self.termination_date, Unset):
            termination_date = self.termination_date.isoformat()

        employee_start_date: Union[Unset, str] = UNSET
        if not isinstance(self.employee_start_date, Unset):
            employee_start_date = self.employee_start_date.isoformat()

        dimension_values: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.dimension_values, Unset):
            dimension_values = []
            for dimension_values_item_data in self.dimension_values:
                dimension_values_item = dimension_values_item_data.to_dict()
                dimension_values.append(dimension_values_item)

        classification: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.classification, Unset):
            classification = self.classification.to_dict()

        employee_name = self.employee_name

        id = self.id

        employee_id = self.employee_id

        location_id = self.location_id

        work_type_id = self.work_type_id

        work_type_name = self.work_type_name

        location_name = self.location_name

        unit_type = self.unit_type

        is_unit_based_work_type = self.is_unit_based_work_type

        pay_run_id = self.pay_run_id

        start: Union[Unset, str] = UNSET
        if not isinstance(self.start, Unset):
            start = self.start.isoformat()

        end: Union[Unset, str] = UNSET
        if not isinstance(self.end, Unset):
            end = self.end.isoformat()

        submitted_start: Union[Unset, str] = UNSET
        if not isinstance(self.submitted_start, Unset):
            submitted_start = self.submitted_start.isoformat()

        submitted_end: Union[Unset, str] = UNSET
        if not isinstance(self.submitted_end, Unset):
            submitted_end = self.submitted_end.isoformat()

        units = self.units

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        pay_slip_url = self.pay_slip_url

        breaks: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.breaks, Unset):
            breaks = []
            for breaks_item_data in self.breaks:
                breaks_item = breaks_item_data.to_dict()
                breaks.append(breaks_item)

        comments = self.comments

        rate = self.rate

        external_reference_id = self.external_reference_id

        source: Union[Unset, str] = UNSET
        if not isinstance(self.source, Unset):
            source = self.source.value

        pay_category_id = self.pay_category_id

        leave_category_id = self.leave_category_id

        leave_request_id = self.leave_request_id

        is_locked = self.is_locked

        cost = self.cost

        discard = self.discard

        attachment: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.attachment, Unset):
            attachment = self.attachment.to_dict()

        is_overlapping = self.is_overlapping

        overdraws_leave = self.overdraws_leave

        reviewed_by = self.reviewed_by

        duration_override = self.duration_override

        auto_approved_by_roster_shift_id = self.auto_approved_by_roster_shift_id

        work_duration_in_minutes = self.work_duration_in_minutes

        breaks_duration_in_minutes = self.breaks_duration_in_minutes

        total_duration_in_minutes = self.total_duration_in_minutes

        hidden_comments = self.hidden_comments

        read_only = self.read_only

        ignore_rounding = self.ignore_rounding

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if default_location_id is not UNSET:
            field_dict["defaultLocationId"] = default_location_id
        if default_location_name is not UNSET:
            field_dict["defaultLocationName"] = default_location_name
        if pay_schedule_id is not UNSET:
            field_dict["payScheduleId"] = pay_schedule_id
        if pay_schedule_name is not UNSET:
            field_dict["payScheduleName"] = pay_schedule_name
        if employee_groups is not UNSET:
            field_dict["employeeGroups"] = employee_groups
        if shift_conditions is not UNSET:
            field_dict["shiftConditions"] = shift_conditions
        if cost_formatted is not UNSET:
            field_dict["costFormatted"] = cost_formatted
        if can_delete is not UNSET:
            field_dict["canDelete"] = can_delete
        if can_edit is not UNSET:
            field_dict["canEdit"] = can_edit
        if can_edit_notes_only is not UNSET:
            field_dict["canEditNotesOnly"] = can_edit_notes_only
        if can_view_costs is not UNSET:
            field_dict["canViewCosts"] = can_view_costs
        if can_approve is not UNSET:
            field_dict["canApprove"] = can_approve
        if termination_date is not UNSET:
            field_dict["terminationDate"] = termination_date
        if employee_start_date is not UNSET:
            field_dict["employeeStartDate"] = employee_start_date
        if dimension_values is not UNSET:
            field_dict["dimensionValues"] = dimension_values
        if classification is not UNSET:
            field_dict["classification"] = classification
        if employee_name is not UNSET:
            field_dict["employeeName"] = employee_name
        if id is not UNSET:
            field_dict["id"] = id
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if location_id is not UNSET:
            field_dict["locationId"] = location_id
        if work_type_id is not UNSET:
            field_dict["workTypeId"] = work_type_id
        if work_type_name is not UNSET:
            field_dict["workTypeName"] = work_type_name
        if location_name is not UNSET:
            field_dict["locationName"] = location_name
        if unit_type is not UNSET:
            field_dict["unitType"] = unit_type
        if is_unit_based_work_type is not UNSET:
            field_dict["isUnitBasedWorkType"] = is_unit_based_work_type
        if pay_run_id is not UNSET:
            field_dict["payRunId"] = pay_run_id
        if start is not UNSET:
            field_dict["start"] = start
        if end is not UNSET:
            field_dict["end"] = end
        if submitted_start is not UNSET:
            field_dict["submittedStart"] = submitted_start
        if submitted_end is not UNSET:
            field_dict["submittedEnd"] = submitted_end
        if units is not UNSET:
            field_dict["units"] = units
        if status is not UNSET:
            field_dict["status"] = status
        if pay_slip_url is not UNSET:
            field_dict["paySlipUrl"] = pay_slip_url
        if breaks is not UNSET:
            field_dict["breaks"] = breaks
        if comments is not UNSET:
            field_dict["comments"] = comments
        if rate is not UNSET:
            field_dict["rate"] = rate
        if external_reference_id is not UNSET:
            field_dict["externalReferenceId"] = external_reference_id
        if source is not UNSET:
            field_dict["source"] = source
        if pay_category_id is not UNSET:
            field_dict["payCategoryId"] = pay_category_id
        if leave_category_id is not UNSET:
            field_dict["leaveCategoryId"] = leave_category_id
        if leave_request_id is not UNSET:
            field_dict["leaveRequestId"] = leave_request_id
        if is_locked is not UNSET:
            field_dict["isLocked"] = is_locked
        if cost is not UNSET:
            field_dict["cost"] = cost
        if discard is not UNSET:
            field_dict["discard"] = discard
        if attachment is not UNSET:
            field_dict["attachment"] = attachment
        if is_overlapping is not UNSET:
            field_dict["isOverlapping"] = is_overlapping
        if overdraws_leave is not UNSET:
            field_dict["overdrawsLeave"] = overdraws_leave
        if reviewed_by is not UNSET:
            field_dict["reviewedBy"] = reviewed_by
        if duration_override is not UNSET:
            field_dict["durationOverride"] = duration_override
        if auto_approved_by_roster_shift_id is not UNSET:
            field_dict["autoApprovedByRosterShiftId"] = auto_approved_by_roster_shift_id
        if work_duration_in_minutes is not UNSET:
            field_dict["workDurationInMinutes"] = work_duration_in_minutes
        if breaks_duration_in_minutes is not UNSET:
            field_dict["breaksDurationInMinutes"] = breaks_duration_in_minutes
        if total_duration_in_minutes is not UNSET:
            field_dict["totalDurationInMinutes"] = total_duration_in_minutes
        if hidden_comments is not UNSET:
            field_dict["hiddenComments"] = hidden_comments
        if read_only is not UNSET:
            field_dict["readOnly"] = read_only
        if ignore_rounding is not UNSET:
            field_dict["ignoreRounding"] = ignore_rounding

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.attachment_model import AttachmentModel
        from ..models.classification_selection import ClassificationSelection
        from ..models.manager_employee_group import ManagerEmployeeGroup
        from ..models.reporting_dimension_value_base_api_model import ReportingDimensionValueBaseApiModel
        from ..models.shift_condition import ShiftCondition
        from ..models.timesheet_break_manager_model import TimesheetBreakManagerModel

        d = src_dict.copy()
        default_location_id = d.pop("defaultLocationId", UNSET)

        default_location_name = d.pop("defaultLocationName", UNSET)

        pay_schedule_id = d.pop("payScheduleId", UNSET)

        pay_schedule_name = d.pop("payScheduleName", UNSET)

        employee_groups = []
        _employee_groups = d.pop("employeeGroups", UNSET)
        for employee_groups_item_data in _employee_groups or []:
            employee_groups_item = ManagerEmployeeGroup.from_dict(employee_groups_item_data)

            employee_groups.append(employee_groups_item)

        shift_conditions = []
        _shift_conditions = d.pop("shiftConditions", UNSET)
        for shift_conditions_item_data in _shift_conditions or []:
            shift_conditions_item = ShiftCondition.from_dict(shift_conditions_item_data)

            shift_conditions.append(shift_conditions_item)

        cost_formatted = d.pop("costFormatted", UNSET)

        can_delete = d.pop("canDelete", UNSET)

        can_edit = d.pop("canEdit", UNSET)

        can_edit_notes_only = d.pop("canEditNotesOnly", UNSET)

        can_view_costs = d.pop("canViewCosts", UNSET)

        can_approve = d.pop("canApprove", UNSET)

        _termination_date = d.pop("terminationDate", UNSET)
        termination_date: Union[Unset, datetime.datetime]
        if isinstance(_termination_date, Unset):
            termination_date = UNSET
        else:
            termination_date = isoparse(_termination_date)

        _employee_start_date = d.pop("employeeStartDate", UNSET)
        employee_start_date: Union[Unset, datetime.datetime]
        if isinstance(_employee_start_date, Unset):
            employee_start_date = UNSET
        else:
            employee_start_date = isoparse(_employee_start_date)

        dimension_values = []
        _dimension_values = d.pop("dimensionValues", UNSET)
        for dimension_values_item_data in _dimension_values or []:
            dimension_values_item = ReportingDimensionValueBaseApiModel.from_dict(dimension_values_item_data)

            dimension_values.append(dimension_values_item)

        _classification = d.pop("classification", UNSET)
        classification: Union[Unset, ClassificationSelection]
        if isinstance(_classification, Unset):
            classification = UNSET
        else:
            classification = ClassificationSelection.from_dict(_classification)

        employee_name = d.pop("employeeName", UNSET)

        id = d.pop("id", UNSET)

        employee_id = d.pop("employeeId", UNSET)

        location_id = d.pop("locationId", UNSET)

        work_type_id = d.pop("workTypeId", UNSET)

        work_type_name = d.pop("workTypeName", UNSET)

        location_name = d.pop("locationName", UNSET)

        unit_type = d.pop("unitType", UNSET)

        is_unit_based_work_type = d.pop("isUnitBasedWorkType", UNSET)

        pay_run_id = d.pop("payRunId", UNSET)

        _start = d.pop("start", UNSET)
        start: Union[Unset, datetime.datetime]
        if isinstance(_start, Unset):
            start = UNSET
        else:
            start = isoparse(_start)

        _end = d.pop("end", UNSET)
        end: Union[Unset, datetime.datetime]
        if isinstance(_end, Unset):
            end = UNSET
        else:
            end = isoparse(_end)

        _submitted_start = d.pop("submittedStart", UNSET)
        submitted_start: Union[Unset, datetime.datetime]
        if isinstance(_submitted_start, Unset):
            submitted_start = UNSET
        else:
            submitted_start = isoparse(_submitted_start)

        _submitted_end = d.pop("submittedEnd", UNSET)
        submitted_end: Union[Unset, datetime.datetime]
        if isinstance(_submitted_end, Unset):
            submitted_end = UNSET
        else:
            submitted_end = isoparse(_submitted_end)

        units = d.pop("units", UNSET)

        _status = d.pop("status", UNSET)
        status: Union[Unset, ManagerTimesheetLineModelTimesheetLineStatusType]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = ManagerTimesheetLineModelTimesheetLineStatusType(_status)

        pay_slip_url = d.pop("paySlipUrl", UNSET)

        breaks = []
        _breaks = d.pop("breaks", UNSET)
        for breaks_item_data in _breaks or []:
            breaks_item = TimesheetBreakManagerModel.from_dict(breaks_item_data)

            breaks.append(breaks_item)

        comments = d.pop("comments", UNSET)

        rate = d.pop("rate", UNSET)

        external_reference_id = d.pop("externalReferenceId", UNSET)

        _source = d.pop("source", UNSET)
        source: Union[Unset, ManagerTimesheetLineModelExternalService]
        if isinstance(_source, Unset):
            source = UNSET
        else:
            source = ManagerTimesheetLineModelExternalService(_source)

        pay_category_id = d.pop("payCategoryId", UNSET)

        leave_category_id = d.pop("leaveCategoryId", UNSET)

        leave_request_id = d.pop("leaveRequestId", UNSET)

        is_locked = d.pop("isLocked", UNSET)

        cost = d.pop("cost", UNSET)

        discard = d.pop("discard", UNSET)

        _attachment = d.pop("attachment", UNSET)
        attachment: Union[Unset, AttachmentModel]
        if isinstance(_attachment, Unset):
            attachment = UNSET
        else:
            attachment = AttachmentModel.from_dict(_attachment)

        is_overlapping = d.pop("isOverlapping", UNSET)

        overdraws_leave = d.pop("overdrawsLeave", UNSET)

        reviewed_by = d.pop("reviewedBy", UNSET)

        duration_override = d.pop("durationOverride", UNSET)

        auto_approved_by_roster_shift_id = d.pop("autoApprovedByRosterShiftId", UNSET)

        work_duration_in_minutes = d.pop("workDurationInMinutes", UNSET)

        breaks_duration_in_minutes = d.pop("breaksDurationInMinutes", UNSET)

        total_duration_in_minutes = d.pop("totalDurationInMinutes", UNSET)

        hidden_comments = d.pop("hiddenComments", UNSET)

        read_only = d.pop("readOnly", UNSET)

        ignore_rounding = d.pop("ignoreRounding", UNSET)

        manager_timesheet_line_model = cls(
            default_location_id=default_location_id,
            default_location_name=default_location_name,
            pay_schedule_id=pay_schedule_id,
            pay_schedule_name=pay_schedule_name,
            employee_groups=employee_groups,
            shift_conditions=shift_conditions,
            cost_formatted=cost_formatted,
            can_delete=can_delete,
            can_edit=can_edit,
            can_edit_notes_only=can_edit_notes_only,
            can_view_costs=can_view_costs,
            can_approve=can_approve,
            termination_date=termination_date,
            employee_start_date=employee_start_date,
            dimension_values=dimension_values,
            classification=classification,
            employee_name=employee_name,
            id=id,
            employee_id=employee_id,
            location_id=location_id,
            work_type_id=work_type_id,
            work_type_name=work_type_name,
            location_name=location_name,
            unit_type=unit_type,
            is_unit_based_work_type=is_unit_based_work_type,
            pay_run_id=pay_run_id,
            start=start,
            end=end,
            submitted_start=submitted_start,
            submitted_end=submitted_end,
            units=units,
            status=status,
            pay_slip_url=pay_slip_url,
            breaks=breaks,
            comments=comments,
            rate=rate,
            external_reference_id=external_reference_id,
            source=source,
            pay_category_id=pay_category_id,
            leave_category_id=leave_category_id,
            leave_request_id=leave_request_id,
            is_locked=is_locked,
            cost=cost,
            discard=discard,
            attachment=attachment,
            is_overlapping=is_overlapping,
            overdraws_leave=overdraws_leave,
            reviewed_by=reviewed_by,
            duration_override=duration_override,
            auto_approved_by_roster_shift_id=auto_approved_by_roster_shift_id,
            work_duration_in_minutes=work_duration_in_minutes,
            breaks_duration_in_minutes=breaks_duration_in_minutes,
            total_duration_in_minutes=total_duration_in_minutes,
            hidden_comments=hidden_comments,
            read_only=read_only,
            ignore_rounding=ignore_rounding,
        )

        manager_timesheet_line_model.additional_properties = d
        return manager_timesheet_line_model

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
