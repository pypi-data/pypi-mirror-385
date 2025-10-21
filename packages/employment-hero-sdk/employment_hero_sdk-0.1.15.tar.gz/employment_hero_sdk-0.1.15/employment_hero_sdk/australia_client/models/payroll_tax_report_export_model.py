from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PayrollTaxReportExportModel")


@_attrs_define
class PayrollTaxReportExportModel:
    """
    Attributes:
        employee_id (Union[Unset, int]):
        first_name (Union[Unset, str]):
        surname (Union[Unset, str]):
        external_id (Union[Unset, str]):
        location (Union[Unset, str]):
        type (Union[Unset, str]):
        state (Union[Unset, str]):
        amount (Union[Unset, float]):
        employee_payroll_tax_exempt (Union[Unset, bool]):
        pay_category_payroll_tax_exempt (Union[Unset, bool]):
        termination_payment (Union[Unset, bool]):
        allowance (Union[Unset, bool]):
        etp (Union[Unset, bool]):
        genuine_redundancy (Union[Unset, bool]):
        lump_sum_d (Union[Unset, bool]):
    """

    employee_id: Union[Unset, int] = UNSET
    first_name: Union[Unset, str] = UNSET
    surname: Union[Unset, str] = UNSET
    external_id: Union[Unset, str] = UNSET
    location: Union[Unset, str] = UNSET
    type: Union[Unset, str] = UNSET
    state: Union[Unset, str] = UNSET
    amount: Union[Unset, float] = UNSET
    employee_payroll_tax_exempt: Union[Unset, bool] = UNSET
    pay_category_payroll_tax_exempt: Union[Unset, bool] = UNSET
    termination_payment: Union[Unset, bool] = UNSET
    allowance: Union[Unset, bool] = UNSET
    etp: Union[Unset, bool] = UNSET
    genuine_redundancy: Union[Unset, bool] = UNSET
    lump_sum_d: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        employee_id = self.employee_id

        first_name = self.first_name

        surname = self.surname

        external_id = self.external_id

        location = self.location

        type = self.type

        state = self.state

        amount = self.amount

        employee_payroll_tax_exempt = self.employee_payroll_tax_exempt

        pay_category_payroll_tax_exempt = self.pay_category_payroll_tax_exempt

        termination_payment = self.termination_payment

        allowance = self.allowance

        etp = self.etp

        genuine_redundancy = self.genuine_redundancy

        lump_sum_d = self.lump_sum_d

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if first_name is not UNSET:
            field_dict["firstName"] = first_name
        if surname is not UNSET:
            field_dict["surname"] = surname
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if location is not UNSET:
            field_dict["location"] = location
        if type is not UNSET:
            field_dict["type"] = type
        if state is not UNSET:
            field_dict["state"] = state
        if amount is not UNSET:
            field_dict["amount"] = amount
        if employee_payroll_tax_exempt is not UNSET:
            field_dict["employeePayrollTaxExempt"] = employee_payroll_tax_exempt
        if pay_category_payroll_tax_exempt is not UNSET:
            field_dict["payCategoryPayrollTaxExempt"] = pay_category_payroll_tax_exempt
        if termination_payment is not UNSET:
            field_dict["terminationPayment"] = termination_payment
        if allowance is not UNSET:
            field_dict["allowance"] = allowance
        if etp is not UNSET:
            field_dict["etp"] = etp
        if genuine_redundancy is not UNSET:
            field_dict["genuineRedundancy"] = genuine_redundancy
        if lump_sum_d is not UNSET:
            field_dict["lumpSumD"] = lump_sum_d

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        employee_id = d.pop("employeeId", UNSET)

        first_name = d.pop("firstName", UNSET)

        surname = d.pop("surname", UNSET)

        external_id = d.pop("externalId", UNSET)

        location = d.pop("location", UNSET)

        type = d.pop("type", UNSET)

        state = d.pop("state", UNSET)

        amount = d.pop("amount", UNSET)

        employee_payroll_tax_exempt = d.pop("employeePayrollTaxExempt", UNSET)

        pay_category_payroll_tax_exempt = d.pop("payCategoryPayrollTaxExempt", UNSET)

        termination_payment = d.pop("terminationPayment", UNSET)

        allowance = d.pop("allowance", UNSET)

        etp = d.pop("etp", UNSET)

        genuine_redundancy = d.pop("genuineRedundancy", UNSET)

        lump_sum_d = d.pop("lumpSumD", UNSET)

        payroll_tax_report_export_model = cls(
            employee_id=employee_id,
            first_name=first_name,
            surname=surname,
            external_id=external_id,
            location=location,
            type=type,
            state=state,
            amount=amount,
            employee_payroll_tax_exempt=employee_payroll_tax_exempt,
            pay_category_payroll_tax_exempt=pay_category_payroll_tax_exempt,
            termination_payment=termination_payment,
            allowance=allowance,
            etp=etp,
            genuine_redundancy=genuine_redundancy,
            lump_sum_d=lump_sum_d,
        )

        payroll_tax_report_export_model.additional_properties = d
        return payroll_tax_report_export_model

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
