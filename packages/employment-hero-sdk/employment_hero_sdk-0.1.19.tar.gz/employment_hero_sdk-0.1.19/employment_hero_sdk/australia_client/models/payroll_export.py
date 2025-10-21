import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.employee_agreement import EmployeeAgreement
    from ..models.timesheet_array import TimesheetArray
    from ..models.timesheet_pay_return_array import TimesheetPayReturnArray


T = TypeVar("T", bound="PayrollExport")


@_attrs_define
class PayrollExport:
    """
    Attributes:
        id (Union[Unset, int]):
        employee_id (Union[Unset, int]):
        employee_agreement_id (Union[Unset, int]):
        period_id (Union[Unset, int]):
        recommended_loadings (Union[Unset, bool]):
        timesheets (Union[Unset, int]):
        timesheets_time_approved (Union[Unset, int]):
        timesheets_pay_approved (Union[Unset, int]):
        paycycle_rules (Union[Unset, int]):
        paycycle_rules_approved (Union[Unset, int]):
        exported (Union[Unset, bool]):
        export_id (Union[Unset, int]):
        paid (Union[Unset, bool]):
        time_total (Union[Unset, float]):
        cost_total (Union[Unset, float]):
        employee_agreement_history_id (Union[Unset, int]):
        creator (Union[Unset, int]):
        created (Union[Unset, datetime.datetime]):
        modified (Union[Unset, datetime.datetime]):
        employee_agreement (Union[Unset, EmployeeAgreement]):
        paycycle_return_array (Union[Unset, List['TimesheetPayReturnArray']]):
        timesheet_array (Union[Unset, List['TimesheetArray']]):
    """

    id: Union[Unset, int] = UNSET
    employee_id: Union[Unset, int] = UNSET
    employee_agreement_id: Union[Unset, int] = UNSET
    period_id: Union[Unset, int] = UNSET
    recommended_loadings: Union[Unset, bool] = UNSET
    timesheets: Union[Unset, int] = UNSET
    timesheets_time_approved: Union[Unset, int] = UNSET
    timesheets_pay_approved: Union[Unset, int] = UNSET
    paycycle_rules: Union[Unset, int] = UNSET
    paycycle_rules_approved: Union[Unset, int] = UNSET
    exported: Union[Unset, bool] = UNSET
    export_id: Union[Unset, int] = UNSET
    paid: Union[Unset, bool] = UNSET
    time_total: Union[Unset, float] = UNSET
    cost_total: Union[Unset, float] = UNSET
    employee_agreement_history_id: Union[Unset, int] = UNSET
    creator: Union[Unset, int] = UNSET
    created: Union[Unset, datetime.datetime] = UNSET
    modified: Union[Unset, datetime.datetime] = UNSET
    employee_agreement: Union[Unset, "EmployeeAgreement"] = UNSET
    paycycle_return_array: Union[Unset, List["TimesheetPayReturnArray"]] = UNSET
    timesheet_array: Union[Unset, List["TimesheetArray"]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        employee_id = self.employee_id

        employee_agreement_id = self.employee_agreement_id

        period_id = self.period_id

        recommended_loadings = self.recommended_loadings

        timesheets = self.timesheets

        timesheets_time_approved = self.timesheets_time_approved

        timesheets_pay_approved = self.timesheets_pay_approved

        paycycle_rules = self.paycycle_rules

        paycycle_rules_approved = self.paycycle_rules_approved

        exported = self.exported

        export_id = self.export_id

        paid = self.paid

        time_total = self.time_total

        cost_total = self.cost_total

        employee_agreement_history_id = self.employee_agreement_history_id

        creator = self.creator

        created: Union[Unset, str] = UNSET
        if not isinstance(self.created, Unset):
            created = self.created.isoformat()

        modified: Union[Unset, str] = UNSET
        if not isinstance(self.modified, Unset):
            modified = self.modified.isoformat()

        employee_agreement: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.employee_agreement, Unset):
            employee_agreement = self.employee_agreement.to_dict()

        paycycle_return_array: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.paycycle_return_array, Unset):
            paycycle_return_array = []
            for paycycle_return_array_item_data in self.paycycle_return_array:
                paycycle_return_array_item = paycycle_return_array_item_data.to_dict()
                paycycle_return_array.append(paycycle_return_array_item)

        timesheet_array: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.timesheet_array, Unset):
            timesheet_array = []
            for timesheet_array_item_data in self.timesheet_array:
                timesheet_array_item = timesheet_array_item_data.to_dict()
                timesheet_array.append(timesheet_array_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if employee_agreement_id is not UNSET:
            field_dict["employeeAgreementId"] = employee_agreement_id
        if period_id is not UNSET:
            field_dict["periodId"] = period_id
        if recommended_loadings is not UNSET:
            field_dict["recommendedLoadings"] = recommended_loadings
        if timesheets is not UNSET:
            field_dict["timesheets"] = timesheets
        if timesheets_time_approved is not UNSET:
            field_dict["timesheetsTimeApproved"] = timesheets_time_approved
        if timesheets_pay_approved is not UNSET:
            field_dict["timesheetsPayApproved"] = timesheets_pay_approved
        if paycycle_rules is not UNSET:
            field_dict["paycycleRules"] = paycycle_rules
        if paycycle_rules_approved is not UNSET:
            field_dict["paycycleRulesApproved"] = paycycle_rules_approved
        if exported is not UNSET:
            field_dict["exported"] = exported
        if export_id is not UNSET:
            field_dict["exportId"] = export_id
        if paid is not UNSET:
            field_dict["paid"] = paid
        if time_total is not UNSET:
            field_dict["timeTotal"] = time_total
        if cost_total is not UNSET:
            field_dict["costTotal"] = cost_total
        if employee_agreement_history_id is not UNSET:
            field_dict["employeeAgreementHistoryId"] = employee_agreement_history_id
        if creator is not UNSET:
            field_dict["creator"] = creator
        if created is not UNSET:
            field_dict["created"] = created
        if modified is not UNSET:
            field_dict["modified"] = modified
        if employee_agreement is not UNSET:
            field_dict["employeeAgreement"] = employee_agreement
        if paycycle_return_array is not UNSET:
            field_dict["paycycleReturnArray"] = paycycle_return_array
        if timesheet_array is not UNSET:
            field_dict["timesheetArray"] = timesheet_array

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.employee_agreement import EmployeeAgreement
        from ..models.timesheet_array import TimesheetArray
        from ..models.timesheet_pay_return_array import TimesheetPayReturnArray

        d = src_dict.copy()
        id = d.pop("id", UNSET)

        employee_id = d.pop("employeeId", UNSET)

        employee_agreement_id = d.pop("employeeAgreementId", UNSET)

        period_id = d.pop("periodId", UNSET)

        recommended_loadings = d.pop("recommendedLoadings", UNSET)

        timesheets = d.pop("timesheets", UNSET)

        timesheets_time_approved = d.pop("timesheetsTimeApproved", UNSET)

        timesheets_pay_approved = d.pop("timesheetsPayApproved", UNSET)

        paycycle_rules = d.pop("paycycleRules", UNSET)

        paycycle_rules_approved = d.pop("paycycleRulesApproved", UNSET)

        exported = d.pop("exported", UNSET)

        export_id = d.pop("exportId", UNSET)

        paid = d.pop("paid", UNSET)

        time_total = d.pop("timeTotal", UNSET)

        cost_total = d.pop("costTotal", UNSET)

        employee_agreement_history_id = d.pop("employeeAgreementHistoryId", UNSET)

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

        _employee_agreement = d.pop("employeeAgreement", UNSET)
        employee_agreement: Union[Unset, EmployeeAgreement]
        if isinstance(_employee_agreement, Unset):
            employee_agreement = UNSET
        else:
            employee_agreement = EmployeeAgreement.from_dict(_employee_agreement)

        paycycle_return_array = []
        _paycycle_return_array = d.pop("paycycleReturnArray", UNSET)
        for paycycle_return_array_item_data in _paycycle_return_array or []:
            paycycle_return_array_item = TimesheetPayReturnArray.from_dict(paycycle_return_array_item_data)

            paycycle_return_array.append(paycycle_return_array_item)

        timesheet_array = []
        _timesheet_array = d.pop("timesheetArray", UNSET)
        for timesheet_array_item_data in _timesheet_array or []:
            timesheet_array_item = TimesheetArray.from_dict(timesheet_array_item_data)

            timesheet_array.append(timesheet_array_item)

        payroll_export = cls(
            id=id,
            employee_id=employee_id,
            employee_agreement_id=employee_agreement_id,
            period_id=period_id,
            recommended_loadings=recommended_loadings,
            timesheets=timesheets,
            timesheets_time_approved=timesheets_time_approved,
            timesheets_pay_approved=timesheets_pay_approved,
            paycycle_rules=paycycle_rules,
            paycycle_rules_approved=paycycle_rules_approved,
            exported=exported,
            export_id=export_id,
            paid=paid,
            time_total=time_total,
            cost_total=cost_total,
            employee_agreement_history_id=employee_agreement_history_id,
            creator=creator,
            created=created,
            modified=modified,
            employee_agreement=employee_agreement,
            paycycle_return_array=paycycle_return_array,
            timesheet_array=timesheet_array,
        )

        payroll_export.additional_properties = d
        return payroll_export

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
