import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.ess_timesheet_model_external_service import EssTimesheetModelExternalService
from ..models.ess_timesheet_model_timesheet_line_status_type import EssTimesheetModelTimesheetLineStatusType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.attachment import Attachment
    from ..models.shift_costing_data import ShiftCostingData
    from ..models.timesheet_break_view_model import TimesheetBreakViewModel


T = TypeVar("T", bound="EssTimesheetModel")


@_attrs_define
class EssTimesheetModel:
    """
    Attributes:
        can_delete (Union[Unset, bool]):
        can_edit (Union[Unset, bool]):
        status_id (Union[Unset, int]):
        attachment (Union[Unset, Attachment]):
        work_duration_in_minutes (Union[Unset, int]):
        breaks_duration_in_minutes (Union[Unset, int]):
        total_duration_in_minutes (Union[Unset, int]):
        auto_approved_by_roster_shift_id (Union[Unset, int]):
        location_is_deleted (Union[Unset, bool]):
        employee_name (Union[Unset, str]):
        id (Union[Unset, int]):
        employee_id (Union[Unset, int]):
        location_id (Union[Unset, int]):
        work_type_id (Union[Unset, int]):
        classification_id (Union[Unset, int]):
        classification_name (Union[Unset, str]):
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
        status (Union[Unset, EssTimesheetModelTimesheetLineStatusType]):
        pay_slip_url (Union[Unset, str]):
        breaks (Union[Unset, List['TimesheetBreakViewModel']]):
        comments (Union[Unset, str]):
        rate (Union[Unset, float]):
        external_reference_id (Union[Unset, str]):
        source (Union[Unset, EssTimesheetModelExternalService]):
        pay_category_id (Union[Unset, int]):
        leave_category_id (Union[Unset, int]):
        leave_request_id (Union[Unset, int]):
        is_locked (Union[Unset, bool]):
        cost (Union[Unset, float]):
        costing_data (Union[Unset, ShiftCostingData]):
        cost_by_location (Union[Unset, float]):
        costing_data_by_location (Union[Unset, ShiftCostingData]):
        discard (Union[Unset, bool]):
        shift_condition_ids (Union[Unset, List[int]]):
        is_overlapping (Union[Unset, bool]):
        overdraws_leave (Union[Unset, bool]):
        reviewed_by (Union[Unset, str]):
        duration_override (Union[Unset, str]):
        hidden_comments (Union[Unset, str]):
        read_only (Union[Unset, bool]):
        ignore_rounding (Union[Unset, bool]):
        dimension_value_ids (Union[Unset, List[int]]):
    """

    can_delete: Union[Unset, bool] = UNSET
    can_edit: Union[Unset, bool] = UNSET
    status_id: Union[Unset, int] = UNSET
    attachment: Union[Unset, "Attachment"] = UNSET
    work_duration_in_minutes: Union[Unset, int] = UNSET
    breaks_duration_in_minutes: Union[Unset, int] = UNSET
    total_duration_in_minutes: Union[Unset, int] = UNSET
    auto_approved_by_roster_shift_id: Union[Unset, int] = UNSET
    location_is_deleted: Union[Unset, bool] = UNSET
    employee_name: Union[Unset, str] = UNSET
    id: Union[Unset, int] = UNSET
    employee_id: Union[Unset, int] = UNSET
    location_id: Union[Unset, int] = UNSET
    work_type_id: Union[Unset, int] = UNSET
    classification_id: Union[Unset, int] = UNSET
    classification_name: Union[Unset, str] = UNSET
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
    status: Union[Unset, EssTimesheetModelTimesheetLineStatusType] = UNSET
    pay_slip_url: Union[Unset, str] = UNSET
    breaks: Union[Unset, List["TimesheetBreakViewModel"]] = UNSET
    comments: Union[Unset, str] = UNSET
    rate: Union[Unset, float] = UNSET
    external_reference_id: Union[Unset, str] = UNSET
    source: Union[Unset, EssTimesheetModelExternalService] = UNSET
    pay_category_id: Union[Unset, int] = UNSET
    leave_category_id: Union[Unset, int] = UNSET
    leave_request_id: Union[Unset, int] = UNSET
    is_locked: Union[Unset, bool] = UNSET
    cost: Union[Unset, float] = UNSET
    costing_data: Union[Unset, "ShiftCostingData"] = UNSET
    cost_by_location: Union[Unset, float] = UNSET
    costing_data_by_location: Union[Unset, "ShiftCostingData"] = UNSET
    discard: Union[Unset, bool] = UNSET
    shift_condition_ids: Union[Unset, List[int]] = UNSET
    is_overlapping: Union[Unset, bool] = UNSET
    overdraws_leave: Union[Unset, bool] = UNSET
    reviewed_by: Union[Unset, str] = UNSET
    duration_override: Union[Unset, str] = UNSET
    hidden_comments: Union[Unset, str] = UNSET
    read_only: Union[Unset, bool] = UNSET
    ignore_rounding: Union[Unset, bool] = UNSET
    dimension_value_ids: Union[Unset, List[int]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        can_delete = self.can_delete

        can_edit = self.can_edit

        status_id = self.status_id

        attachment: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.attachment, Unset):
            attachment = self.attachment.to_dict()

        work_duration_in_minutes = self.work_duration_in_minutes

        breaks_duration_in_minutes = self.breaks_duration_in_minutes

        total_duration_in_minutes = self.total_duration_in_minutes

        auto_approved_by_roster_shift_id = self.auto_approved_by_roster_shift_id

        location_is_deleted = self.location_is_deleted

        employee_name = self.employee_name

        id = self.id

        employee_id = self.employee_id

        location_id = self.location_id

        work_type_id = self.work_type_id

        classification_id = self.classification_id

        classification_name = self.classification_name

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

        costing_data: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.costing_data, Unset):
            costing_data = self.costing_data.to_dict()

        cost_by_location = self.cost_by_location

        costing_data_by_location: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.costing_data_by_location, Unset):
            costing_data_by_location = self.costing_data_by_location.to_dict()

        discard = self.discard

        shift_condition_ids: Union[Unset, List[int]] = UNSET
        if not isinstance(self.shift_condition_ids, Unset):
            shift_condition_ids = self.shift_condition_ids

        is_overlapping = self.is_overlapping

        overdraws_leave = self.overdraws_leave

        reviewed_by = self.reviewed_by

        duration_override = self.duration_override

        hidden_comments = self.hidden_comments

        read_only = self.read_only

        ignore_rounding = self.ignore_rounding

        dimension_value_ids: Union[Unset, List[int]] = UNSET
        if not isinstance(self.dimension_value_ids, Unset):
            dimension_value_ids = self.dimension_value_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if can_delete is not UNSET:
            field_dict["canDelete"] = can_delete
        if can_edit is not UNSET:
            field_dict["canEdit"] = can_edit
        if status_id is not UNSET:
            field_dict["statusId"] = status_id
        if attachment is not UNSET:
            field_dict["attachment"] = attachment
        if work_duration_in_minutes is not UNSET:
            field_dict["workDurationInMinutes"] = work_duration_in_minutes
        if breaks_duration_in_minutes is not UNSET:
            field_dict["breaksDurationInMinutes"] = breaks_duration_in_minutes
        if total_duration_in_minutes is not UNSET:
            field_dict["totalDurationInMinutes"] = total_duration_in_minutes
        if auto_approved_by_roster_shift_id is not UNSET:
            field_dict["autoApprovedByRosterShiftId"] = auto_approved_by_roster_shift_id
        if location_is_deleted is not UNSET:
            field_dict["locationIsDeleted"] = location_is_deleted
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
        if classification_id is not UNSET:
            field_dict["classificationId"] = classification_id
        if classification_name is not UNSET:
            field_dict["classificationName"] = classification_name
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
        if costing_data is not UNSET:
            field_dict["costingData"] = costing_data
        if cost_by_location is not UNSET:
            field_dict["costByLocation"] = cost_by_location
        if costing_data_by_location is not UNSET:
            field_dict["costingDataByLocation"] = costing_data_by_location
        if discard is not UNSET:
            field_dict["discard"] = discard
        if shift_condition_ids is not UNSET:
            field_dict["shiftConditionIds"] = shift_condition_ids
        if is_overlapping is not UNSET:
            field_dict["isOverlapping"] = is_overlapping
        if overdraws_leave is not UNSET:
            field_dict["overdrawsLeave"] = overdraws_leave
        if reviewed_by is not UNSET:
            field_dict["reviewedBy"] = reviewed_by
        if duration_override is not UNSET:
            field_dict["durationOverride"] = duration_override
        if hidden_comments is not UNSET:
            field_dict["hiddenComments"] = hidden_comments
        if read_only is not UNSET:
            field_dict["readOnly"] = read_only
        if ignore_rounding is not UNSET:
            field_dict["ignoreRounding"] = ignore_rounding
        if dimension_value_ids is not UNSET:
            field_dict["dimensionValueIds"] = dimension_value_ids

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.attachment import Attachment
        from ..models.shift_costing_data import ShiftCostingData
        from ..models.timesheet_break_view_model import TimesheetBreakViewModel

        d = src_dict.copy()
        can_delete = d.pop("canDelete", UNSET)

        can_edit = d.pop("canEdit", UNSET)

        status_id = d.pop("statusId", UNSET)

        _attachment = d.pop("attachment", UNSET)
        attachment: Union[Unset, Attachment]
        if isinstance(_attachment, Unset):
            attachment = UNSET
        else:
            attachment = Attachment.from_dict(_attachment)

        work_duration_in_minutes = d.pop("workDurationInMinutes", UNSET)

        breaks_duration_in_minutes = d.pop("breaksDurationInMinutes", UNSET)

        total_duration_in_minutes = d.pop("totalDurationInMinutes", UNSET)

        auto_approved_by_roster_shift_id = d.pop("autoApprovedByRosterShiftId", UNSET)

        location_is_deleted = d.pop("locationIsDeleted", UNSET)

        employee_name = d.pop("employeeName", UNSET)

        id = d.pop("id", UNSET)

        employee_id = d.pop("employeeId", UNSET)

        location_id = d.pop("locationId", UNSET)

        work_type_id = d.pop("workTypeId", UNSET)

        classification_id = d.pop("classificationId", UNSET)

        classification_name = d.pop("classificationName", UNSET)

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
        status: Union[Unset, EssTimesheetModelTimesheetLineStatusType]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = EssTimesheetModelTimesheetLineStatusType(_status)

        pay_slip_url = d.pop("paySlipUrl", UNSET)

        breaks = []
        _breaks = d.pop("breaks", UNSET)
        for breaks_item_data in _breaks or []:
            breaks_item = TimesheetBreakViewModel.from_dict(breaks_item_data)

            breaks.append(breaks_item)

        comments = d.pop("comments", UNSET)

        rate = d.pop("rate", UNSET)

        external_reference_id = d.pop("externalReferenceId", UNSET)

        _source = d.pop("source", UNSET)
        source: Union[Unset, EssTimesheetModelExternalService]
        if isinstance(_source, Unset):
            source = UNSET
        else:
            source = EssTimesheetModelExternalService(_source)

        pay_category_id = d.pop("payCategoryId", UNSET)

        leave_category_id = d.pop("leaveCategoryId", UNSET)

        leave_request_id = d.pop("leaveRequestId", UNSET)

        is_locked = d.pop("isLocked", UNSET)

        cost = d.pop("cost", UNSET)

        _costing_data = d.pop("costingData", UNSET)
        costing_data: Union[Unset, ShiftCostingData]
        if isinstance(_costing_data, Unset):
            costing_data = UNSET
        else:
            costing_data = ShiftCostingData.from_dict(_costing_data)

        cost_by_location = d.pop("costByLocation", UNSET)

        _costing_data_by_location = d.pop("costingDataByLocation", UNSET)
        costing_data_by_location: Union[Unset, ShiftCostingData]
        if isinstance(_costing_data_by_location, Unset):
            costing_data_by_location = UNSET
        else:
            costing_data_by_location = ShiftCostingData.from_dict(_costing_data_by_location)

        discard = d.pop("discard", UNSET)

        shift_condition_ids = cast(List[int], d.pop("shiftConditionIds", UNSET))

        is_overlapping = d.pop("isOverlapping", UNSET)

        overdraws_leave = d.pop("overdrawsLeave", UNSET)

        reviewed_by = d.pop("reviewedBy", UNSET)

        duration_override = d.pop("durationOverride", UNSET)

        hidden_comments = d.pop("hiddenComments", UNSET)

        read_only = d.pop("readOnly", UNSET)

        ignore_rounding = d.pop("ignoreRounding", UNSET)

        dimension_value_ids = cast(List[int], d.pop("dimensionValueIds", UNSET))

        ess_timesheet_model = cls(
            can_delete=can_delete,
            can_edit=can_edit,
            status_id=status_id,
            attachment=attachment,
            work_duration_in_minutes=work_duration_in_minutes,
            breaks_duration_in_minutes=breaks_duration_in_minutes,
            total_duration_in_minutes=total_duration_in_minutes,
            auto_approved_by_roster_shift_id=auto_approved_by_roster_shift_id,
            location_is_deleted=location_is_deleted,
            employee_name=employee_name,
            id=id,
            employee_id=employee_id,
            location_id=location_id,
            work_type_id=work_type_id,
            classification_id=classification_id,
            classification_name=classification_name,
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
            costing_data=costing_data,
            cost_by_location=cost_by_location,
            costing_data_by_location=costing_data_by_location,
            discard=discard,
            shift_condition_ids=shift_condition_ids,
            is_overlapping=is_overlapping,
            overdraws_leave=overdraws_leave,
            reviewed_by=reviewed_by,
            duration_override=duration_override,
            hidden_comments=hidden_comments,
            read_only=read_only,
            ignore_rounding=ignore_rounding,
            dimension_value_ids=dimension_value_ids,
        )

        ess_timesheet_model.additional_properties = d
        return ess_timesheet_model

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
