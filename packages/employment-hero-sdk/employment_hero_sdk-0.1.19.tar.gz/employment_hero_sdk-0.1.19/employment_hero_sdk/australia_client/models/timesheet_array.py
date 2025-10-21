import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.timesheet_pay_return_array import TimesheetPayReturnArray


T = TypeVar("T", bound="TimesheetArray")


@_attrs_define
class TimesheetArray:
    """
    Attributes:
        id (Union[Unset, int]):
        employee (Union[Unset, int]):
        employee_history (Union[Unset, int]):
        employee_agreement (Union[Unset, int]):
        date (Union[Unset, str]):
        start_time (Union[Unset, int]):
        end_time (Union[Unset, int]):
        mealbreak (Union[Unset, str]):
        total_time (Union[Unset, float]):
        total_time_inv (Union[Unset, float]):
        cost (Union[Unset, float]):
        roster (Union[Unset, int]):
        employee_comment (Union[Unset, str]):
        supervisor_comment (Union[Unset, str]):
        supervisor (Union[Unset, str]):
        disputed (Union[Unset, bool]):
        time_approved (Union[Unset, bool]):
        time_approver (Union[Unset, int]):
        discarded (Union[Unset, bool]):
        validation_flag (Union[Unset, int]):
        operational_unit (Union[Unset, int]):
        is_in_progress (Union[Unset, bool]):
        is_leave (Union[Unset, bool]):
        leave_id (Union[Unset, int]):
        leave_rule (Union[Unset, int]):
        invoiced (Union[Unset, bool]):
        invoice_comment (Union[Unset, str]):
        pay_rule_approved (Union[Unset, bool]):
        exported (Union[Unset, bool]):
        staging_id (Union[Unset, int]):
        pay_staged (Union[Unset, bool]):
        paycycle_id (Union[Unset, int]):
        file (Union[Unset, str]):
        creator (Union[Unset, int]):
        created (Union[Unset, datetime.datetime]):
        modified (Union[Unset, datetime.datetime]):
        start_time_localized (Union[Unset, str]):
        end_time_localized (Union[Unset, str]):
        timesheet_pay_return_array (Union[Unset, List['TimesheetPayReturnArray']]):
    """

    id: Union[Unset, int] = UNSET
    employee: Union[Unset, int] = UNSET
    employee_history: Union[Unset, int] = UNSET
    employee_agreement: Union[Unset, int] = UNSET
    date: Union[Unset, str] = UNSET
    start_time: Union[Unset, int] = UNSET
    end_time: Union[Unset, int] = UNSET
    mealbreak: Union[Unset, str] = UNSET
    total_time: Union[Unset, float] = UNSET
    total_time_inv: Union[Unset, float] = UNSET
    cost: Union[Unset, float] = UNSET
    roster: Union[Unset, int] = UNSET
    employee_comment: Union[Unset, str] = UNSET
    supervisor_comment: Union[Unset, str] = UNSET
    supervisor: Union[Unset, str] = UNSET
    disputed: Union[Unset, bool] = UNSET
    time_approved: Union[Unset, bool] = UNSET
    time_approver: Union[Unset, int] = UNSET
    discarded: Union[Unset, bool] = UNSET
    validation_flag: Union[Unset, int] = UNSET
    operational_unit: Union[Unset, int] = UNSET
    is_in_progress: Union[Unset, bool] = UNSET
    is_leave: Union[Unset, bool] = UNSET
    leave_id: Union[Unset, int] = UNSET
    leave_rule: Union[Unset, int] = UNSET
    invoiced: Union[Unset, bool] = UNSET
    invoice_comment: Union[Unset, str] = UNSET
    pay_rule_approved: Union[Unset, bool] = UNSET
    exported: Union[Unset, bool] = UNSET
    staging_id: Union[Unset, int] = UNSET
    pay_staged: Union[Unset, bool] = UNSET
    paycycle_id: Union[Unset, int] = UNSET
    file: Union[Unset, str] = UNSET
    creator: Union[Unset, int] = UNSET
    created: Union[Unset, datetime.datetime] = UNSET
    modified: Union[Unset, datetime.datetime] = UNSET
    start_time_localized: Union[Unset, str] = UNSET
    end_time_localized: Union[Unset, str] = UNSET
    timesheet_pay_return_array: Union[Unset, List["TimesheetPayReturnArray"]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        employee = self.employee

        employee_history = self.employee_history

        employee_agreement = self.employee_agreement

        date = self.date

        start_time = self.start_time

        end_time = self.end_time

        mealbreak = self.mealbreak

        total_time = self.total_time

        total_time_inv = self.total_time_inv

        cost = self.cost

        roster = self.roster

        employee_comment = self.employee_comment

        supervisor_comment = self.supervisor_comment

        supervisor = self.supervisor

        disputed = self.disputed

        time_approved = self.time_approved

        time_approver = self.time_approver

        discarded = self.discarded

        validation_flag = self.validation_flag

        operational_unit = self.operational_unit

        is_in_progress = self.is_in_progress

        is_leave = self.is_leave

        leave_id = self.leave_id

        leave_rule = self.leave_rule

        invoiced = self.invoiced

        invoice_comment = self.invoice_comment

        pay_rule_approved = self.pay_rule_approved

        exported = self.exported

        staging_id = self.staging_id

        pay_staged = self.pay_staged

        paycycle_id = self.paycycle_id

        file = self.file

        creator = self.creator

        created: Union[Unset, str] = UNSET
        if not isinstance(self.created, Unset):
            created = self.created.isoformat()

        modified: Union[Unset, str] = UNSET
        if not isinstance(self.modified, Unset):
            modified = self.modified.isoformat()

        start_time_localized = self.start_time_localized

        end_time_localized = self.end_time_localized

        timesheet_pay_return_array: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.timesheet_pay_return_array, Unset):
            timesheet_pay_return_array = []
            for timesheet_pay_return_array_item_data in self.timesheet_pay_return_array:
                timesheet_pay_return_array_item = timesheet_pay_return_array_item_data.to_dict()
                timesheet_pay_return_array.append(timesheet_pay_return_array_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if employee is not UNSET:
            field_dict["employee"] = employee
        if employee_history is not UNSET:
            field_dict["employeeHistory"] = employee_history
        if employee_agreement is not UNSET:
            field_dict["employeeAgreement"] = employee_agreement
        if date is not UNSET:
            field_dict["date"] = date
        if start_time is not UNSET:
            field_dict["startTime"] = start_time
        if end_time is not UNSET:
            field_dict["endTime"] = end_time
        if mealbreak is not UNSET:
            field_dict["mealbreak"] = mealbreak
        if total_time is not UNSET:
            field_dict["totalTime"] = total_time
        if total_time_inv is not UNSET:
            field_dict["totalTimeInv"] = total_time_inv
        if cost is not UNSET:
            field_dict["cost"] = cost
        if roster is not UNSET:
            field_dict["roster"] = roster
        if employee_comment is not UNSET:
            field_dict["employeeComment"] = employee_comment
        if supervisor_comment is not UNSET:
            field_dict["supervisorComment"] = supervisor_comment
        if supervisor is not UNSET:
            field_dict["supervisor"] = supervisor
        if disputed is not UNSET:
            field_dict["disputed"] = disputed
        if time_approved is not UNSET:
            field_dict["timeApproved"] = time_approved
        if time_approver is not UNSET:
            field_dict["timeApprover"] = time_approver
        if discarded is not UNSET:
            field_dict["discarded"] = discarded
        if validation_flag is not UNSET:
            field_dict["validationFlag"] = validation_flag
        if operational_unit is not UNSET:
            field_dict["operationalUnit"] = operational_unit
        if is_in_progress is not UNSET:
            field_dict["isInProgress"] = is_in_progress
        if is_leave is not UNSET:
            field_dict["isLeave"] = is_leave
        if leave_id is not UNSET:
            field_dict["leaveId"] = leave_id
        if leave_rule is not UNSET:
            field_dict["leaveRule"] = leave_rule
        if invoiced is not UNSET:
            field_dict["invoiced"] = invoiced
        if invoice_comment is not UNSET:
            field_dict["invoiceComment"] = invoice_comment
        if pay_rule_approved is not UNSET:
            field_dict["payRuleApproved"] = pay_rule_approved
        if exported is not UNSET:
            field_dict["exported"] = exported
        if staging_id is not UNSET:
            field_dict["stagingId"] = staging_id
        if pay_staged is not UNSET:
            field_dict["payStaged"] = pay_staged
        if paycycle_id is not UNSET:
            field_dict["paycycleId"] = paycycle_id
        if file is not UNSET:
            field_dict["file"] = file
        if creator is not UNSET:
            field_dict["creator"] = creator
        if created is not UNSET:
            field_dict["created"] = created
        if modified is not UNSET:
            field_dict["modified"] = modified
        if start_time_localized is not UNSET:
            field_dict["startTimeLocalized"] = start_time_localized
        if end_time_localized is not UNSET:
            field_dict["endTimeLocalized"] = end_time_localized
        if timesheet_pay_return_array is not UNSET:
            field_dict["timesheetPayReturnArray"] = timesheet_pay_return_array

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.timesheet_pay_return_array import TimesheetPayReturnArray

        d = src_dict.copy()
        id = d.pop("id", UNSET)

        employee = d.pop("employee", UNSET)

        employee_history = d.pop("employeeHistory", UNSET)

        employee_agreement = d.pop("employeeAgreement", UNSET)

        date = d.pop("date", UNSET)

        start_time = d.pop("startTime", UNSET)

        end_time = d.pop("endTime", UNSET)

        mealbreak = d.pop("mealbreak", UNSET)

        total_time = d.pop("totalTime", UNSET)

        total_time_inv = d.pop("totalTimeInv", UNSET)

        cost = d.pop("cost", UNSET)

        roster = d.pop("roster", UNSET)

        employee_comment = d.pop("employeeComment", UNSET)

        supervisor_comment = d.pop("supervisorComment", UNSET)

        supervisor = d.pop("supervisor", UNSET)

        disputed = d.pop("disputed", UNSET)

        time_approved = d.pop("timeApproved", UNSET)

        time_approver = d.pop("timeApprover", UNSET)

        discarded = d.pop("discarded", UNSET)

        validation_flag = d.pop("validationFlag", UNSET)

        operational_unit = d.pop("operationalUnit", UNSET)

        is_in_progress = d.pop("isInProgress", UNSET)

        is_leave = d.pop("isLeave", UNSET)

        leave_id = d.pop("leaveId", UNSET)

        leave_rule = d.pop("leaveRule", UNSET)

        invoiced = d.pop("invoiced", UNSET)

        invoice_comment = d.pop("invoiceComment", UNSET)

        pay_rule_approved = d.pop("payRuleApproved", UNSET)

        exported = d.pop("exported", UNSET)

        staging_id = d.pop("stagingId", UNSET)

        pay_staged = d.pop("payStaged", UNSET)

        paycycle_id = d.pop("paycycleId", UNSET)

        file = d.pop("file", UNSET)

        creator = d.pop("creator", UNSET)

        _created = d.pop("created", UNSET)
        created: Union[Unset, datetime.datetime]
        if isinstance(_created, Unset):
            created = UNSET
        else:
            created = isoparse(_created)

        _modified = d.pop("modified", UNSET)
        modified: Union[Unset, datetime.datetime]
        if isinstance(_modified, Unset):
            modified = UNSET
        else:
            modified = isoparse(_modified)

        start_time_localized = d.pop("startTimeLocalized", UNSET)

        end_time_localized = d.pop("endTimeLocalized", UNSET)

        timesheet_pay_return_array = []
        _timesheet_pay_return_array = d.pop("timesheetPayReturnArray", UNSET)
        for timesheet_pay_return_array_item_data in _timesheet_pay_return_array or []:
            timesheet_pay_return_array_item = TimesheetPayReturnArray.from_dict(timesheet_pay_return_array_item_data)

            timesheet_pay_return_array.append(timesheet_pay_return_array_item)

        timesheet_array = cls(
            id=id,
            employee=employee,
            employee_history=employee_history,
            employee_agreement=employee_agreement,
            date=date,
            start_time=start_time,
            end_time=end_time,
            mealbreak=mealbreak,
            total_time=total_time,
            total_time_inv=total_time_inv,
            cost=cost,
            roster=roster,
            employee_comment=employee_comment,
            supervisor_comment=supervisor_comment,
            supervisor=supervisor,
            disputed=disputed,
            time_approved=time_approved,
            time_approver=time_approver,
            discarded=discarded,
            validation_flag=validation_flag,
            operational_unit=operational_unit,
            is_in_progress=is_in_progress,
            is_leave=is_leave,
            leave_id=leave_id,
            leave_rule=leave_rule,
            invoiced=invoiced,
            invoice_comment=invoice_comment,
            pay_rule_approved=pay_rule_approved,
            exported=exported,
            staging_id=staging_id,
            pay_staged=pay_staged,
            paycycle_id=paycycle_id,
            file=file,
            creator=creator,
            created=created,
            modified=modified,
            start_time_localized=start_time_localized,
            end_time_localized=end_time_localized,
            timesheet_pay_return_array=timesheet_pay_return_array,
        )

        timesheet_array.additional_properties = d
        return timesheet_array

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
