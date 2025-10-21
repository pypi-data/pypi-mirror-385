from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AuPayRunInclusionExportModel")


@_attrs_define
class AuPayRunInclusionExportModel:
    """
    Attributes:
        super_contribution_type (Union[Unset, str]):
        super_rate (Union[Unset, str]):
        tax_code (Union[Unset, str]):
        tax_rate (Union[Unset, str]):
        employee_id (Union[Unset, int]):
        first_name (Union[Unset, str]):
        surname (Union[Unset, str]):
        external_id (Union[Unset, str]):
        primary_location (Union[Unset, str]):
        location (Union[Unset, str]):
        deduction_category (Union[Unset, str]):
        expense_category (Union[Unset, str]):
        employer_liability_category (Union[Unset, str]):
        pay_category (Union[Unset, str]):
        tax_adjustment_type (Union[Unset, str]):
        start_date (Union[Unset, str]):
        expiry (Union[Unset, str]):
        amount (Union[Unset, float]):
        amount_type (Union[Unset, str]):
        paid (Union[Unset, str]):
        preserved_earnings (Union[Unset, str]):
        units (Union[Unset, float]):
        rate (Union[Unset, str]):
        total (Union[Unset, str]):
        notes (Union[Unset, str]):
    """

    super_contribution_type: Union[Unset, str] = UNSET
    super_rate: Union[Unset, str] = UNSET
    tax_code: Union[Unset, str] = UNSET
    tax_rate: Union[Unset, str] = UNSET
    employee_id: Union[Unset, int] = UNSET
    first_name: Union[Unset, str] = UNSET
    surname: Union[Unset, str] = UNSET
    external_id: Union[Unset, str] = UNSET
    primary_location: Union[Unset, str] = UNSET
    location: Union[Unset, str] = UNSET
    deduction_category: Union[Unset, str] = UNSET
    expense_category: Union[Unset, str] = UNSET
    employer_liability_category: Union[Unset, str] = UNSET
    pay_category: Union[Unset, str] = UNSET
    tax_adjustment_type: Union[Unset, str] = UNSET
    start_date: Union[Unset, str] = UNSET
    expiry: Union[Unset, str] = UNSET
    amount: Union[Unset, float] = UNSET
    amount_type: Union[Unset, str] = UNSET
    paid: Union[Unset, str] = UNSET
    preserved_earnings: Union[Unset, str] = UNSET
    units: Union[Unset, float] = UNSET
    rate: Union[Unset, str] = UNSET
    total: Union[Unset, str] = UNSET
    notes: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        super_contribution_type = self.super_contribution_type

        super_rate = self.super_rate

        tax_code = self.tax_code

        tax_rate = self.tax_rate

        employee_id = self.employee_id

        first_name = self.first_name

        surname = self.surname

        external_id = self.external_id

        primary_location = self.primary_location

        location = self.location

        deduction_category = self.deduction_category

        expense_category = self.expense_category

        employer_liability_category = self.employer_liability_category

        pay_category = self.pay_category

        tax_adjustment_type = self.tax_adjustment_type

        start_date = self.start_date

        expiry = self.expiry

        amount = self.amount

        amount_type = self.amount_type

        paid = self.paid

        preserved_earnings = self.preserved_earnings

        units = self.units

        rate = self.rate

        total = self.total

        notes = self.notes

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if super_contribution_type is not UNSET:
            field_dict["superContributionType"] = super_contribution_type
        if super_rate is not UNSET:
            field_dict["superRate"] = super_rate
        if tax_code is not UNSET:
            field_dict["taxCode"] = tax_code
        if tax_rate is not UNSET:
            field_dict["taxRate"] = tax_rate
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if first_name is not UNSET:
            field_dict["firstName"] = first_name
        if surname is not UNSET:
            field_dict["surname"] = surname
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if primary_location is not UNSET:
            field_dict["primaryLocation"] = primary_location
        if location is not UNSET:
            field_dict["location"] = location
        if deduction_category is not UNSET:
            field_dict["deductionCategory"] = deduction_category
        if expense_category is not UNSET:
            field_dict["expenseCategory"] = expense_category
        if employer_liability_category is not UNSET:
            field_dict["employerLiabilityCategory"] = employer_liability_category
        if pay_category is not UNSET:
            field_dict["payCategory"] = pay_category
        if tax_adjustment_type is not UNSET:
            field_dict["taxAdjustmentType"] = tax_adjustment_type
        if start_date is not UNSET:
            field_dict["startDate"] = start_date
        if expiry is not UNSET:
            field_dict["expiry"] = expiry
        if amount is not UNSET:
            field_dict["amount"] = amount
        if amount_type is not UNSET:
            field_dict["amountType"] = amount_type
        if paid is not UNSET:
            field_dict["paid"] = paid
        if preserved_earnings is not UNSET:
            field_dict["preservedEarnings"] = preserved_earnings
        if units is not UNSET:
            field_dict["units"] = units
        if rate is not UNSET:
            field_dict["rate"] = rate
        if total is not UNSET:
            field_dict["total"] = total
        if notes is not UNSET:
            field_dict["notes"] = notes

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        super_contribution_type = d.pop("superContributionType", UNSET)

        super_rate = d.pop("superRate", UNSET)

        tax_code = d.pop("taxCode", UNSET)

        tax_rate = d.pop("taxRate", UNSET)

        employee_id = d.pop("employeeId", UNSET)

        first_name = d.pop("firstName", UNSET)

        surname = d.pop("surname", UNSET)

        external_id = d.pop("externalId", UNSET)

        primary_location = d.pop("primaryLocation", UNSET)

        location = d.pop("location", UNSET)

        deduction_category = d.pop("deductionCategory", UNSET)

        expense_category = d.pop("expenseCategory", UNSET)

        employer_liability_category = d.pop("employerLiabilityCategory", UNSET)

        pay_category = d.pop("payCategory", UNSET)

        tax_adjustment_type = d.pop("taxAdjustmentType", UNSET)

        start_date = d.pop("startDate", UNSET)

        expiry = d.pop("expiry", UNSET)

        amount = d.pop("amount", UNSET)

        amount_type = d.pop("amountType", UNSET)

        paid = d.pop("paid", UNSET)

        preserved_earnings = d.pop("preservedEarnings", UNSET)

        units = d.pop("units", UNSET)

        rate = d.pop("rate", UNSET)

        total = d.pop("total", UNSET)

        notes = d.pop("notes", UNSET)

        au_pay_run_inclusion_export_model = cls(
            super_contribution_type=super_contribution_type,
            super_rate=super_rate,
            tax_code=tax_code,
            tax_rate=tax_rate,
            employee_id=employee_id,
            first_name=first_name,
            surname=surname,
            external_id=external_id,
            primary_location=primary_location,
            location=location,
            deduction_category=deduction_category,
            expense_category=expense_category,
            employer_liability_category=employer_liability_category,
            pay_category=pay_category,
            tax_adjustment_type=tax_adjustment_type,
            start_date=start_date,
            expiry=expiry,
            amount=amount,
            amount_type=amount_type,
            paid=paid,
            preserved_earnings=preserved_earnings,
            units=units,
            rate=rate,
            total=total,
            notes=notes,
        )

        au_pay_run_inclusion_export_model.additional_properties = d
        return au_pay_run_inclusion_export_model

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
