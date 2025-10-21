import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="EmployeeRecurringExpenseModel")


@_attrs_define
class EmployeeRecurringExpenseModel:
    """
    Attributes:
        name (Union[Unset, str]):
        expense_category_id (Union[Unset, int]):
        location_id (Union[Unset, int]):
        tax_code (Union[Unset, str]):
        tax_code_display_name (Union[Unset, str]):
        tax_rate (Union[Unset, float]):
        id (Union[Unset, int]):
        employee_id (Union[Unset, int]):
        amount (Union[Unset, float]):
        expiry_date (Union[Unset, datetime.datetime]):
        from_date (Union[Unset, datetime.datetime]):
        maximum_amount_paid (Union[Unset, float]):
        total_amount_paid (Union[Unset, float]):
        is_active (Union[Unset, bool]):
        notes (Union[Unset, str]):
    """

    name: Union[Unset, str] = UNSET
    expense_category_id: Union[Unset, int] = UNSET
    location_id: Union[Unset, int] = UNSET
    tax_code: Union[Unset, str] = UNSET
    tax_code_display_name: Union[Unset, str] = UNSET
    tax_rate: Union[Unset, float] = UNSET
    id: Union[Unset, int] = UNSET
    employee_id: Union[Unset, int] = UNSET
    amount: Union[Unset, float] = UNSET
    expiry_date: Union[Unset, datetime.datetime] = UNSET
    from_date: Union[Unset, datetime.datetime] = UNSET
    maximum_amount_paid: Union[Unset, float] = UNSET
    total_amount_paid: Union[Unset, float] = UNSET
    is_active: Union[Unset, bool] = UNSET
    notes: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name

        expense_category_id = self.expense_category_id

        location_id = self.location_id

        tax_code = self.tax_code

        tax_code_display_name = self.tax_code_display_name

        tax_rate = self.tax_rate

        id = self.id

        employee_id = self.employee_id

        amount = self.amount

        expiry_date: Union[Unset, str] = UNSET
        if not isinstance(self.expiry_date, Unset):
            expiry_date = self.expiry_date.isoformat()

        from_date: Union[Unset, str] = UNSET
        if not isinstance(self.from_date, Unset):
            from_date = self.from_date.isoformat()

        maximum_amount_paid = self.maximum_amount_paid

        total_amount_paid = self.total_amount_paid

        is_active = self.is_active

        notes = self.notes

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if expense_category_id is not UNSET:
            field_dict["expenseCategoryId"] = expense_category_id
        if location_id is not UNSET:
            field_dict["locationId"] = location_id
        if tax_code is not UNSET:
            field_dict["taxCode"] = tax_code
        if tax_code_display_name is not UNSET:
            field_dict["taxCodeDisplayName"] = tax_code_display_name
        if tax_rate is not UNSET:
            field_dict["taxRate"] = tax_rate
        if id is not UNSET:
            field_dict["id"] = id
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if amount is not UNSET:
            field_dict["amount"] = amount
        if expiry_date is not UNSET:
            field_dict["expiryDate"] = expiry_date
        if from_date is not UNSET:
            field_dict["fromDate"] = from_date
        if maximum_amount_paid is not UNSET:
            field_dict["maximumAmountPaid"] = maximum_amount_paid
        if total_amount_paid is not UNSET:
            field_dict["totalAmountPaid"] = total_amount_paid
        if is_active is not UNSET:
            field_dict["isActive"] = is_active
        if notes is not UNSET:
            field_dict["notes"] = notes

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name", UNSET)

        expense_category_id = d.pop("expenseCategoryId", UNSET)

        location_id = d.pop("locationId", UNSET)

        tax_code = d.pop("taxCode", UNSET)

        tax_code_display_name = d.pop("taxCodeDisplayName", UNSET)

        tax_rate = d.pop("taxRate", UNSET)

        id = d.pop("id", UNSET)

        employee_id = d.pop("employeeId", UNSET)

        amount = d.pop("amount", UNSET)

        _expiry_date = d.pop("expiryDate", UNSET)
        expiry_date: Union[Unset, datetime.datetime]
        if isinstance(_expiry_date, Unset):
            expiry_date = UNSET
        else:
            expiry_date = isoparse(_expiry_date)

        _from_date = d.pop("fromDate", UNSET)
        from_date: Union[Unset, datetime.datetime]
        if isinstance(_from_date, Unset):
            from_date = UNSET
        else:
            from_date = isoparse(_from_date)

        maximum_amount_paid = d.pop("maximumAmountPaid", UNSET)

        total_amount_paid = d.pop("totalAmountPaid", UNSET)

        is_active = d.pop("isActive", UNSET)

        notes = d.pop("notes", UNSET)

        employee_recurring_expense_model = cls(
            name=name,
            expense_category_id=expense_category_id,
            location_id=location_id,
            tax_code=tax_code,
            tax_code_display_name=tax_code_display_name,
            tax_rate=tax_rate,
            id=id,
            employee_id=employee_id,
            amount=amount,
            expiry_date=expiry_date,
            from_date=from_date,
            maximum_amount_paid=maximum_amount_paid,
            total_amount_paid=total_amount_paid,
            is_active=is_active,
            notes=notes,
        )

        employee_recurring_expense_model.additional_properties = d
        return employee_recurring_expense_model

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
