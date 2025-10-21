from enum import Enum


class ExpenseManagementFilterModelNullableEmployeeExpenseRequestGroupBy(str, Enum):
    EMPLOYEE = "Employee"
    EXPENSECATEGORY = "ExpenseCategory"

    def __str__(self) -> str:
        return str(self.value)
