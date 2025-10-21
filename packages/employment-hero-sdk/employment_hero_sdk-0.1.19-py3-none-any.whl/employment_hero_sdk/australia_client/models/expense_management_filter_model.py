import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.expense_management_filter_model_nullable_employee_expense_request_group_by import (
    ExpenseManagementFilterModelNullableEmployeeExpenseRequestGroupBy,
)
from ..models.expense_management_filter_model_nullable_employee_expense_request_status import (
    ExpenseManagementFilterModelNullableEmployeeExpenseRequestStatus,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="ExpenseManagementFilterModel")


@_attrs_define
class ExpenseManagementFilterModel:
    """
    Attributes:
        status (Union[Unset, ExpenseManagementFilterModelNullableEmployeeExpenseRequestStatus]):
        from_date (Union[Unset, datetime.datetime]):
        to_date (Union[Unset, datetime.datetime]):
        employee_id (Union[Unset, int]):
        location_id (Union[Unset, int]):
        expense_category_id (Union[Unset, int]):
        group_by (Union[Unset, ExpenseManagementFilterModelNullableEmployeeExpenseRequestGroupBy]):
        current_page (Union[Unset, int]):
        page_size (Union[Unset, int]):
    """

    status: Union[Unset, ExpenseManagementFilterModelNullableEmployeeExpenseRequestStatus] = UNSET
    from_date: Union[Unset, datetime.datetime] = UNSET
    to_date: Union[Unset, datetime.datetime] = UNSET
    employee_id: Union[Unset, int] = UNSET
    location_id: Union[Unset, int] = UNSET
    expense_category_id: Union[Unset, int] = UNSET
    group_by: Union[Unset, ExpenseManagementFilterModelNullableEmployeeExpenseRequestGroupBy] = UNSET
    current_page: Union[Unset, int] = UNSET
    page_size: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        from_date: Union[Unset, str] = UNSET
        if not isinstance(self.from_date, Unset):
            from_date = self.from_date.isoformat()

        to_date: Union[Unset, str] = UNSET
        if not isinstance(self.to_date, Unset):
            to_date = self.to_date.isoformat()

        employee_id = self.employee_id

        location_id = self.location_id

        expense_category_id = self.expense_category_id

        group_by: Union[Unset, str] = UNSET
        if not isinstance(self.group_by, Unset):
            group_by = self.group_by.value

        current_page = self.current_page

        page_size = self.page_size

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if status is not UNSET:
            field_dict["status"] = status
        if from_date is not UNSET:
            field_dict["fromDate"] = from_date
        if to_date is not UNSET:
            field_dict["toDate"] = to_date
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if location_id is not UNSET:
            field_dict["locationId"] = location_id
        if expense_category_id is not UNSET:
            field_dict["expenseCategoryId"] = expense_category_id
        if group_by is not UNSET:
            field_dict["groupBy"] = group_by
        if current_page is not UNSET:
            field_dict["currentPage"] = current_page
        if page_size is not UNSET:
            field_dict["pageSize"] = page_size

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _status = d.pop("status", UNSET)
        status: Union[Unset, ExpenseManagementFilterModelNullableEmployeeExpenseRequestStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = ExpenseManagementFilterModelNullableEmployeeExpenseRequestStatus(_status)

        _from_date = d.pop("fromDate", UNSET)
        from_date: Union[Unset, datetime.datetime]
        if isinstance(_from_date, Unset):
            from_date = UNSET
        else:
            from_date = isoparse(_from_date)

        _to_date = d.pop("toDate", UNSET)
        to_date: Union[Unset, datetime.datetime]
        if isinstance(_to_date, Unset):
            to_date = UNSET
        else:
            to_date = isoparse(_to_date)

        employee_id = d.pop("employeeId", UNSET)

        location_id = d.pop("locationId", UNSET)

        expense_category_id = d.pop("expenseCategoryId", UNSET)

        _group_by = d.pop("groupBy", UNSET)
        group_by: Union[Unset, ExpenseManagementFilterModelNullableEmployeeExpenseRequestGroupBy]
        if isinstance(_group_by, Unset):
            group_by = UNSET
        else:
            group_by = ExpenseManagementFilterModelNullableEmployeeExpenseRequestGroupBy(_group_by)

        current_page = d.pop("currentPage", UNSET)

        page_size = d.pop("pageSize", UNSET)

        expense_management_filter_model = cls(
            status=status,
            from_date=from_date,
            to_date=to_date,
            employee_id=employee_id,
            location_id=location_id,
            expense_category_id=expense_category_id,
            group_by=group_by,
            current_page=current_page,
            page_size=page_size,
        )

        expense_management_filter_model.additional_properties = d
        return expense_management_filter_model

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
