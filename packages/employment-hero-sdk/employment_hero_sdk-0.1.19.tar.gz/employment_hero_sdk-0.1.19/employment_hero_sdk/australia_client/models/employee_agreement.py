from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.employee_agreement_object import EmployeeAgreementObject


T = TypeVar("T", bound="EmployeeAgreement")


@_attrs_define
class EmployeeAgreement:
    """
    Attributes:
        search (Union[Unset, EmployeeAgreementObject]):
        start (Union[Unset, int]):
        max_ (Union[Unset, int]):
        id (Union[Unset, int]):
        employee_id (Union[Unset, int]):
        pay_point (Union[Unset, int]):
        emp_type (Union[Unset, int]):
        company_name (Union[Unset, str]):
        active (Union[Unset, bool]):
        start_date (Union[Unset, str]):
        contract (Union[Unset, int]):
        salary_pay_rule (Union[Unset, int]):
        contract_file (Union[Unset, int]):
        payroll_id (Union[Unset, str]):
        pay_period (Union[Unset, int]):
        history_id (Union[Unset, int]):
        creator (Union[Unset, int]):
        created (Union[Unset, str]):
        modified (Union[Unset, str]):
    """

    search: Union[Unset, "EmployeeAgreementObject"] = UNSET
    start: Union[Unset, int] = UNSET
    max_: Union[Unset, int] = UNSET
    id: Union[Unset, int] = UNSET
    employee_id: Union[Unset, int] = UNSET
    pay_point: Union[Unset, int] = UNSET
    emp_type: Union[Unset, int] = UNSET
    company_name: Union[Unset, str] = UNSET
    active: Union[Unset, bool] = UNSET
    start_date: Union[Unset, str] = UNSET
    contract: Union[Unset, int] = UNSET
    salary_pay_rule: Union[Unset, int] = UNSET
    contract_file: Union[Unset, int] = UNSET
    payroll_id: Union[Unset, str] = UNSET
    pay_period: Union[Unset, int] = UNSET
    history_id: Union[Unset, int] = UNSET
    creator: Union[Unset, int] = UNSET
    created: Union[Unset, str] = UNSET
    modified: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        search: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.search, Unset):
            search = self.search.to_dict()

        start = self.start

        max_ = self.max_

        id = self.id

        employee_id = self.employee_id

        pay_point = self.pay_point

        emp_type = self.emp_type

        company_name = self.company_name

        active = self.active

        start_date = self.start_date

        contract = self.contract

        salary_pay_rule = self.salary_pay_rule

        contract_file = self.contract_file

        payroll_id = self.payroll_id

        pay_period = self.pay_period

        history_id = self.history_id

        creator = self.creator

        created = self.created

        modified = self.modified

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if search is not UNSET:
            field_dict["search"] = search
        if start is not UNSET:
            field_dict["start"] = start
        if max_ is not UNSET:
            field_dict["max"] = max_
        if id is not UNSET:
            field_dict["id"] = id
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if pay_point is not UNSET:
            field_dict["payPoint"] = pay_point
        if emp_type is not UNSET:
            field_dict["empType"] = emp_type
        if company_name is not UNSET:
            field_dict["companyName"] = company_name
        if active is not UNSET:
            field_dict["active"] = active
        if start_date is not UNSET:
            field_dict["startDate"] = start_date
        if contract is not UNSET:
            field_dict["contract"] = contract
        if salary_pay_rule is not UNSET:
            field_dict["salaryPayRule"] = salary_pay_rule
        if contract_file is not UNSET:
            field_dict["contractFile"] = contract_file
        if payroll_id is not UNSET:
            field_dict["payrollId"] = payroll_id
        if pay_period is not UNSET:
            field_dict["payPeriod"] = pay_period
        if history_id is not UNSET:
            field_dict["historyId"] = history_id
        if creator is not UNSET:
            field_dict["creator"] = creator
        if created is not UNSET:
            field_dict["created"] = created
        if modified is not UNSET:
            field_dict["modified"] = modified

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.employee_agreement_object import EmployeeAgreementObject

        d = src_dict.copy()
        _search = d.pop("search", UNSET)
        search: Union[Unset, EmployeeAgreementObject]
        if isinstance(_search, Unset):
            search = UNSET
        else:
            search = EmployeeAgreementObject.from_dict(_search)

        start = d.pop("start", UNSET)

        max_ = d.pop("max", UNSET)

        id = d.pop("id", UNSET)

        employee_id = d.pop("employeeId", UNSET)

        pay_point = d.pop("payPoint", UNSET)

        emp_type = d.pop("empType", UNSET)

        company_name = d.pop("companyName", UNSET)

        active = d.pop("active", UNSET)

        start_date = d.pop("startDate", UNSET)

        contract = d.pop("contract", UNSET)

        salary_pay_rule = d.pop("salaryPayRule", UNSET)

        contract_file = d.pop("contractFile", UNSET)

        payroll_id = d.pop("payrollId", UNSET)

        pay_period = d.pop("payPeriod", UNSET)

        history_id = d.pop("historyId", UNSET)

        creator = d.pop("creator", UNSET)

        created = d.pop("created", UNSET)

        modified = d.pop("modified", UNSET)

        employee_agreement = cls(
            search=search,
            start=start,
            max_=max_,
            id=id,
            employee_id=employee_id,
            pay_point=pay_point,
            emp_type=emp_type,
            company_name=company_name,
            active=active,
            start_date=start_date,
            contract=contract,
            salary_pay_rule=salary_pay_rule,
            contract_file=contract_file,
            payroll_id=payroll_id,
            pay_period=pay_period,
            history_id=history_id,
            creator=creator,
            created=created,
            modified=modified,
        )

        employee_agreement.additional_properties = d
        return employee_agreement

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
