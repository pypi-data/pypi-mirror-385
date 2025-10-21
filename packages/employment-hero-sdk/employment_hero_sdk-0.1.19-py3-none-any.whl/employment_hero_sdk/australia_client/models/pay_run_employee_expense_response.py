from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.pay_run_employee_expense_response_dictionary_string_list_1 import (
        PayRunEmployeeExpenseResponseDictionaryStringList1,
    )


T = TypeVar("T", bound="PayRunEmployeeExpenseResponse")


@_attrs_define
class PayRunEmployeeExpenseResponse:
    """
    Attributes:
        employee_expenses (Union[Unset, PayRunEmployeeExpenseResponseDictionaryStringList1]):
        pay_run_id (Union[Unset, int]):
    """

    employee_expenses: Union[Unset, "PayRunEmployeeExpenseResponseDictionaryStringList1"] = UNSET
    pay_run_id: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        employee_expenses: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.employee_expenses, Unset):
            employee_expenses = self.employee_expenses.to_dict()

        pay_run_id = self.pay_run_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if employee_expenses is not UNSET:
            field_dict["employeeExpenses"] = employee_expenses
        if pay_run_id is not UNSET:
            field_dict["payRunId"] = pay_run_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.pay_run_employee_expense_response_dictionary_string_list_1 import (
            PayRunEmployeeExpenseResponseDictionaryStringList1,
        )

        d = src_dict.copy()
        _employee_expenses = d.pop("employeeExpenses", UNSET)
        employee_expenses: Union[Unset, PayRunEmployeeExpenseResponseDictionaryStringList1]
        if isinstance(_employee_expenses, Unset):
            employee_expenses = UNSET
        else:
            employee_expenses = PayRunEmployeeExpenseResponseDictionaryStringList1.from_dict(_employee_expenses)

        pay_run_id = d.pop("payRunId", UNSET)

        pay_run_employee_expense_response = cls(
            employee_expenses=employee_expenses,
            pay_run_id=pay_run_id,
        )

        pay_run_employee_expense_response.additional_properties = d
        return pay_run_employee_expense_response

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
