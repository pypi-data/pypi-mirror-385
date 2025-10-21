import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.manager_leave_request_model_leave_unit_type_enum import ManagerLeaveRequestModelLeaveUnitTypeEnum
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.attachment_model import AttachmentModel
    from ..models.partially_applied_leave_request_banner_model import PartiallyAppliedLeaveRequestBannerModel


T = TypeVar("T", bound="ManagerLeaveRequestModel")


@_attrs_define
class ManagerLeaveRequestModel:
    """
    Attributes:
        employee_id (Union[Unset, int]):
        employee_name (Union[Unset, str]):
        in_progress (Union[Unset, bool]):
        termination_date (Union[Unset, datetime.datetime]):
        can_approve (Union[Unset, bool]):
        accrued_balance (Union[Unset, float]):
        exceeds_balance (Union[Unset, bool]):
        is_leave_based_roster_shift (Union[Unset, bool]):
        total_hours (Union[Unset, float]):
        leave_category_id (Union[Unset, int]):
        work_type_id (Union[Unset, int]):
        work_type_name (Union[Unset, str]):
        is_approved (Union[Unset, bool]):
        is_declined (Union[Unset, bool]):
        is_cancelled (Union[Unset, bool]):
        is_pending (Union[Unset, bool]):
        id (Union[Unset, int]):
        from_date (Union[Unset, datetime.datetime]):
        to_date (Union[Unset, datetime.datetime]):
        requested_date (Union[Unset, datetime.datetime]):
        leave_category_name (Union[Unset, str]):
        hours_per_day (Union[Unset, float]):
        total_units (Union[Unset, float]):
        previously_applied_units (Union[Unset, float]):
        can_partially_edit (Union[Unset, bool]):
        notes (Union[Unset, str]):
        total_days (Union[Unset, float]):
        amount (Union[Unset, str]):
        status (Union[Unset, str]):
        status_update_notes (Union[Unset, str]):
        can_cancel (Union[Unset, bool]):
        can_modify (Union[Unset, bool]):
        require_notes_for_leave_requests (Union[Unset, bool]):
        attachment (Union[Unset, AttachmentModel]):
        unit_type (Union[Unset, ManagerLeaveRequestModelLeaveUnitTypeEnum]):
        banner (Union[Unset, PartiallyAppliedLeaveRequestBannerModel]):
        manually_applied (Union[Unset, bool]):
        applied_leave_unit_type_description (Union[Unset, str]):
    """

    employee_id: Union[Unset, int] = UNSET
    employee_name: Union[Unset, str] = UNSET
    in_progress: Union[Unset, bool] = UNSET
    termination_date: Union[Unset, datetime.datetime] = UNSET
    can_approve: Union[Unset, bool] = UNSET
    accrued_balance: Union[Unset, float] = UNSET
    exceeds_balance: Union[Unset, bool] = UNSET
    is_leave_based_roster_shift: Union[Unset, bool] = UNSET
    total_hours: Union[Unset, float] = UNSET
    leave_category_id: Union[Unset, int] = UNSET
    work_type_id: Union[Unset, int] = UNSET
    work_type_name: Union[Unset, str] = UNSET
    is_approved: Union[Unset, bool] = UNSET
    is_declined: Union[Unset, bool] = UNSET
    is_cancelled: Union[Unset, bool] = UNSET
    is_pending: Union[Unset, bool] = UNSET
    id: Union[Unset, int] = UNSET
    from_date: Union[Unset, datetime.datetime] = UNSET
    to_date: Union[Unset, datetime.datetime] = UNSET
    requested_date: Union[Unset, datetime.datetime] = UNSET
    leave_category_name: Union[Unset, str] = UNSET
    hours_per_day: Union[Unset, float] = UNSET
    total_units: Union[Unset, float] = UNSET
    previously_applied_units: Union[Unset, float] = UNSET
    can_partially_edit: Union[Unset, bool] = UNSET
    notes: Union[Unset, str] = UNSET
    total_days: Union[Unset, float] = UNSET
    amount: Union[Unset, str] = UNSET
    status: Union[Unset, str] = UNSET
    status_update_notes: Union[Unset, str] = UNSET
    can_cancel: Union[Unset, bool] = UNSET
    can_modify: Union[Unset, bool] = UNSET
    require_notes_for_leave_requests: Union[Unset, bool] = UNSET
    attachment: Union[Unset, "AttachmentModel"] = UNSET
    unit_type: Union[Unset, ManagerLeaveRequestModelLeaveUnitTypeEnum] = UNSET
    banner: Union[Unset, "PartiallyAppliedLeaveRequestBannerModel"] = UNSET
    manually_applied: Union[Unset, bool] = UNSET
    applied_leave_unit_type_description: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        employee_id = self.employee_id

        employee_name = self.employee_name

        in_progress = self.in_progress

        termination_date: Union[Unset, str] = UNSET
        if not isinstance(self.termination_date, Unset):
            termination_date = self.termination_date.isoformat()

        can_approve = self.can_approve

        accrued_balance = self.accrued_balance

        exceeds_balance = self.exceeds_balance

        is_leave_based_roster_shift = self.is_leave_based_roster_shift

        total_hours = self.total_hours

        leave_category_id = self.leave_category_id

        work_type_id = self.work_type_id

        work_type_name = self.work_type_name

        is_approved = self.is_approved

        is_declined = self.is_declined

        is_cancelled = self.is_cancelled

        is_pending = self.is_pending

        id = self.id

        from_date: Union[Unset, str] = UNSET
        if not isinstance(self.from_date, Unset):
            from_date = self.from_date.isoformat()

        to_date: Union[Unset, str] = UNSET
        if not isinstance(self.to_date, Unset):
            to_date = self.to_date.isoformat()

        requested_date: Union[Unset, str] = UNSET
        if not isinstance(self.requested_date, Unset):
            requested_date = self.requested_date.isoformat()

        leave_category_name = self.leave_category_name

        hours_per_day = self.hours_per_day

        total_units = self.total_units

        previously_applied_units = self.previously_applied_units

        can_partially_edit = self.can_partially_edit

        notes = self.notes

        total_days = self.total_days

        amount = self.amount

        status = self.status

        status_update_notes = self.status_update_notes

        can_cancel = self.can_cancel

        can_modify = self.can_modify

        require_notes_for_leave_requests = self.require_notes_for_leave_requests

        attachment: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.attachment, Unset):
            attachment = self.attachment.to_dict()

        unit_type: Union[Unset, str] = UNSET
        if not isinstance(self.unit_type, Unset):
            unit_type = self.unit_type.value

        banner: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.banner, Unset):
            banner = self.banner.to_dict()

        manually_applied = self.manually_applied

        applied_leave_unit_type_description = self.applied_leave_unit_type_description

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if employee_name is not UNSET:
            field_dict["employeeName"] = employee_name
        if in_progress is not UNSET:
            field_dict["inProgress"] = in_progress
        if termination_date is not UNSET:
            field_dict["terminationDate"] = termination_date
        if can_approve is not UNSET:
            field_dict["canApprove"] = can_approve
        if accrued_balance is not UNSET:
            field_dict["accruedBalance"] = accrued_balance
        if exceeds_balance is not UNSET:
            field_dict["exceedsBalance"] = exceeds_balance
        if is_leave_based_roster_shift is not UNSET:
            field_dict["isLeaveBasedRosterShift"] = is_leave_based_roster_shift
        if total_hours is not UNSET:
            field_dict["totalHours"] = total_hours
        if leave_category_id is not UNSET:
            field_dict["leaveCategoryId"] = leave_category_id
        if work_type_id is not UNSET:
            field_dict["workTypeId"] = work_type_id
        if work_type_name is not UNSET:
            field_dict["workTypeName"] = work_type_name
        if is_approved is not UNSET:
            field_dict["isApproved"] = is_approved
        if is_declined is not UNSET:
            field_dict["isDeclined"] = is_declined
        if is_cancelled is not UNSET:
            field_dict["isCancelled"] = is_cancelled
        if is_pending is not UNSET:
            field_dict["isPending"] = is_pending
        if id is not UNSET:
            field_dict["id"] = id
        if from_date is not UNSET:
            field_dict["fromDate"] = from_date
        if to_date is not UNSET:
            field_dict["toDate"] = to_date
        if requested_date is not UNSET:
            field_dict["requestedDate"] = requested_date
        if leave_category_name is not UNSET:
            field_dict["leaveCategoryName"] = leave_category_name
        if hours_per_day is not UNSET:
            field_dict["hoursPerDay"] = hours_per_day
        if total_units is not UNSET:
            field_dict["totalUnits"] = total_units
        if previously_applied_units is not UNSET:
            field_dict["previouslyAppliedUnits"] = previously_applied_units
        if can_partially_edit is not UNSET:
            field_dict["canPartiallyEdit"] = can_partially_edit
        if notes is not UNSET:
            field_dict["notes"] = notes
        if total_days is not UNSET:
            field_dict["totalDays"] = total_days
        if amount is not UNSET:
            field_dict["amount"] = amount
        if status is not UNSET:
            field_dict["status"] = status
        if status_update_notes is not UNSET:
            field_dict["statusUpdateNotes"] = status_update_notes
        if can_cancel is not UNSET:
            field_dict["canCancel"] = can_cancel
        if can_modify is not UNSET:
            field_dict["canModify"] = can_modify
        if require_notes_for_leave_requests is not UNSET:
            field_dict["requireNotesForLeaveRequests"] = require_notes_for_leave_requests
        if attachment is not UNSET:
            field_dict["attachment"] = attachment
        if unit_type is not UNSET:
            field_dict["unitType"] = unit_type
        if banner is not UNSET:
            field_dict["banner"] = banner
        if manually_applied is not UNSET:
            field_dict["manuallyApplied"] = manually_applied
        if applied_leave_unit_type_description is not UNSET:
            field_dict["appliedLeaveUnitTypeDescription"] = applied_leave_unit_type_description

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.attachment_model import AttachmentModel
        from ..models.partially_applied_leave_request_banner_model import PartiallyAppliedLeaveRequestBannerModel

        d = src_dict.copy()
        employee_id = d.pop("employeeId", UNSET)

        employee_name = d.pop("employeeName", UNSET)

        in_progress = d.pop("inProgress", UNSET)

        _termination_date = d.pop("terminationDate", UNSET)
        termination_date: Union[Unset, datetime.datetime]
        if isinstance(_termination_date, Unset):
            termination_date = UNSET
        else:
            termination_date = isoparse(_termination_date)

        can_approve = d.pop("canApprove", UNSET)

        accrued_balance = d.pop("accruedBalance", UNSET)

        exceeds_balance = d.pop("exceedsBalance", UNSET)

        is_leave_based_roster_shift = d.pop("isLeaveBasedRosterShift", UNSET)

        total_hours = d.pop("totalHours", UNSET)

        leave_category_id = d.pop("leaveCategoryId", UNSET)

        work_type_id = d.pop("workTypeId", UNSET)

        work_type_name = d.pop("workTypeName", UNSET)

        is_approved = d.pop("isApproved", UNSET)

        is_declined = d.pop("isDeclined", UNSET)

        is_cancelled = d.pop("isCancelled", UNSET)

        is_pending = d.pop("isPending", UNSET)

        id = d.pop("id", UNSET)

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

        _requested_date = d.pop("requestedDate", UNSET)
        requested_date: Union[Unset, datetime.datetime]
        if isinstance(_requested_date, Unset):
            requested_date = UNSET
        else:
            requested_date = isoparse(_requested_date)

        leave_category_name = d.pop("leaveCategoryName", UNSET)

        hours_per_day = d.pop("hoursPerDay", UNSET)

        total_units = d.pop("totalUnits", UNSET)

        previously_applied_units = d.pop("previouslyAppliedUnits", UNSET)

        can_partially_edit = d.pop("canPartiallyEdit", UNSET)

        notes = d.pop("notes", UNSET)

        total_days = d.pop("totalDays", UNSET)

        amount = d.pop("amount", UNSET)

        status = d.pop("status", UNSET)

        status_update_notes = d.pop("statusUpdateNotes", UNSET)

        can_cancel = d.pop("canCancel", UNSET)

        can_modify = d.pop("canModify", UNSET)

        require_notes_for_leave_requests = d.pop("requireNotesForLeaveRequests", UNSET)

        _attachment = d.pop("attachment", UNSET)
        attachment: Union[Unset, AttachmentModel]
        if isinstance(_attachment, Unset):
            attachment = UNSET
        else:
            attachment = AttachmentModel.from_dict(_attachment)

        _unit_type = d.pop("unitType", UNSET)
        unit_type: Union[Unset, ManagerLeaveRequestModelLeaveUnitTypeEnum]
        if isinstance(_unit_type, Unset):
            unit_type = UNSET
        else:
            unit_type = ManagerLeaveRequestModelLeaveUnitTypeEnum(_unit_type)

        _banner = d.pop("banner", UNSET)
        banner: Union[Unset, PartiallyAppliedLeaveRequestBannerModel]
        if isinstance(_banner, Unset):
            banner = UNSET
        else:
            banner = PartiallyAppliedLeaveRequestBannerModel.from_dict(_banner)

        manually_applied = d.pop("manuallyApplied", UNSET)

        applied_leave_unit_type_description = d.pop("appliedLeaveUnitTypeDescription", UNSET)

        manager_leave_request_model = cls(
            employee_id=employee_id,
            employee_name=employee_name,
            in_progress=in_progress,
            termination_date=termination_date,
            can_approve=can_approve,
            accrued_balance=accrued_balance,
            exceeds_balance=exceeds_balance,
            is_leave_based_roster_shift=is_leave_based_roster_shift,
            total_hours=total_hours,
            leave_category_id=leave_category_id,
            work_type_id=work_type_id,
            work_type_name=work_type_name,
            is_approved=is_approved,
            is_declined=is_declined,
            is_cancelled=is_cancelled,
            is_pending=is_pending,
            id=id,
            from_date=from_date,
            to_date=to_date,
            requested_date=requested_date,
            leave_category_name=leave_category_name,
            hours_per_day=hours_per_day,
            total_units=total_units,
            previously_applied_units=previously_applied_units,
            can_partially_edit=can_partially_edit,
            notes=notes,
            total_days=total_days,
            amount=amount,
            status=status,
            status_update_notes=status_update_notes,
            can_cancel=can_cancel,
            can_modify=can_modify,
            require_notes_for_leave_requests=require_notes_for_leave_requests,
            attachment=attachment,
            unit_type=unit_type,
            banner=banner,
            manually_applied=manually_applied,
            applied_leave_unit_type_description=applied_leave_unit_type_description,
        )

        manager_leave_request_model.additional_properties = d
        return manager_leave_request_model

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
