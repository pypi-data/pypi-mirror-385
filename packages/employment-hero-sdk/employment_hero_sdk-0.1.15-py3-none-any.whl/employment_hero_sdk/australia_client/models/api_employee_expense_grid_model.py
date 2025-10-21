from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ApiEmployeeExpenseGridModel")


@_attrs_define
class ApiEmployeeExpenseGridModel:
    """
    Attributes:
        notes (Union[Unset, str]):
        amount (Union[Unset, float]):
        location_name (Union[Unset, str]):
        employee_expense_category_name (Union[Unset, str]):
    """

    notes: Union[Unset, str] = UNSET
    amount: Union[Unset, float] = UNSET
    location_name: Union[Unset, str] = UNSET
    employee_expense_category_name: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        notes = self.notes

        amount = self.amount

        location_name = self.location_name

        employee_expense_category_name = self.employee_expense_category_name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if notes is not UNSET:
            field_dict["notes"] = notes
        if amount is not UNSET:
            field_dict["amount"] = amount
        if location_name is not UNSET:
            field_dict["locationName"] = location_name
        if employee_expense_category_name is not UNSET:
            field_dict["employeeExpenseCategoryName"] = employee_expense_category_name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        notes = d.pop("notes", UNSET)

        amount = d.pop("amount", UNSET)

        location_name = d.pop("locationName", UNSET)

        employee_expense_category_name = d.pop("employeeExpenseCategoryName", UNSET)

        api_employee_expense_grid_model = cls(
            notes=notes,
            amount=amount,
            location_name=location_name,
            employee_expense_category_name=employee_expense_category_name,
        )

        api_employee_expense_grid_model.additional_properties = d
        return api_employee_expense_grid_model

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
