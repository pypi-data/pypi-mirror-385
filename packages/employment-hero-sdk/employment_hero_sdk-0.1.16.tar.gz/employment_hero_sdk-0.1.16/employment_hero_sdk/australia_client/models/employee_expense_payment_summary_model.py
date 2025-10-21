from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="EmployeeExpensePaymentSummaryModel")


@_attrs_define
class EmployeeExpensePaymentSummaryModel:
    """
    Attributes:
        employee_id (Union[Unset, int]):
        expense_category_id (Union[Unset, int]):
        expense_category_name (Union[Unset, str]):
        ytd_amount (Union[Unset, float]):
        total_amount (Union[Unset, float]):
    """

    employee_id: Union[Unset, int] = UNSET
    expense_category_id: Union[Unset, int] = UNSET
    expense_category_name: Union[Unset, str] = UNSET
    ytd_amount: Union[Unset, float] = UNSET
    total_amount: Union[Unset, float] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        employee_id = self.employee_id

        expense_category_id = self.expense_category_id

        expense_category_name = self.expense_category_name

        ytd_amount = self.ytd_amount

        total_amount = self.total_amount

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if expense_category_id is not UNSET:
            field_dict["expenseCategoryId"] = expense_category_id
        if expense_category_name is not UNSET:
            field_dict["expenseCategoryName"] = expense_category_name
        if ytd_amount is not UNSET:
            field_dict["ytdAmount"] = ytd_amount
        if total_amount is not UNSET:
            field_dict["totalAmount"] = total_amount

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        employee_id = d.pop("employeeId", UNSET)

        expense_category_id = d.pop("expenseCategoryId", UNSET)

        expense_category_name = d.pop("expenseCategoryName", UNSET)

        ytd_amount = d.pop("ytdAmount", UNSET)

        total_amount = d.pop("totalAmount", UNSET)

        employee_expense_payment_summary_model = cls(
            employee_id=employee_id,
            expense_category_id=expense_category_id,
            expense_category_name=expense_category_name,
            ytd_amount=ytd_amount,
            total_amount=total_amount,
        )

        employee_expense_payment_summary_model.additional_properties = d
        return employee_expense_payment_summary_model

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
