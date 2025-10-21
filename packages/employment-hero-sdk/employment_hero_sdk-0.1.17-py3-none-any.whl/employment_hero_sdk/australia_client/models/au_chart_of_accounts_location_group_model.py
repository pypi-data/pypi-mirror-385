from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.au_chart_of_accounts_location_accounts_model import AuChartOfAccountsLocationAccountsModel
    from ..models.chart_of_accounts_liability_location_category_model import (
        ChartOfAccountsLiabilityLocationCategoryModel,
    )
    from ..models.chart_of_accounts_location_category_model import ChartOfAccountsLocationCategoryModel
    from ..models.chart_of_accounts_location_leave_category_model import ChartOfAccountsLocationLeaveCategoryModel


T = TypeVar("T", bound="AuChartOfAccountsLocationGroupModel")


@_attrs_define
class AuChartOfAccountsLocationGroupModel:
    """
    Attributes:
        default_accounts (Union[Unset, AuChartOfAccountsLocationAccountsModel]):
        leave_categories (Union[Unset, List['ChartOfAccountsLocationLeaveCategoryModel']]):
        location_id (Union[Unset, int]):
        pay_categories (Union[Unset, List['ChartOfAccountsLocationCategoryModel']]):
        deduction_categories (Union[Unset, List['ChartOfAccountsLiabilityLocationCategoryModel']]):
        employee_expense_categories (Union[Unset, List['ChartOfAccountsLocationCategoryModel']]):
        employer_liability_categories (Union[Unset, List['ChartOfAccountsLiabilityLocationCategoryModel']]):
    """

    default_accounts: Union[Unset, "AuChartOfAccountsLocationAccountsModel"] = UNSET
    leave_categories: Union[Unset, List["ChartOfAccountsLocationLeaveCategoryModel"]] = UNSET
    location_id: Union[Unset, int] = UNSET
    pay_categories: Union[Unset, List["ChartOfAccountsLocationCategoryModel"]] = UNSET
    deduction_categories: Union[Unset, List["ChartOfAccountsLiabilityLocationCategoryModel"]] = UNSET
    employee_expense_categories: Union[Unset, List["ChartOfAccountsLocationCategoryModel"]] = UNSET
    employer_liability_categories: Union[Unset, List["ChartOfAccountsLiabilityLocationCategoryModel"]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        default_accounts: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.default_accounts, Unset):
            default_accounts = self.default_accounts.to_dict()

        leave_categories: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.leave_categories, Unset):
            leave_categories = []
            for leave_categories_item_data in self.leave_categories:
                leave_categories_item = leave_categories_item_data.to_dict()
                leave_categories.append(leave_categories_item)

        location_id = self.location_id

        pay_categories: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.pay_categories, Unset):
            pay_categories = []
            for pay_categories_item_data in self.pay_categories:
                pay_categories_item = pay_categories_item_data.to_dict()
                pay_categories.append(pay_categories_item)

        deduction_categories: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.deduction_categories, Unset):
            deduction_categories = []
            for deduction_categories_item_data in self.deduction_categories:
                deduction_categories_item = deduction_categories_item_data.to_dict()
                deduction_categories.append(deduction_categories_item)

        employee_expense_categories: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.employee_expense_categories, Unset):
            employee_expense_categories = []
            for employee_expense_categories_item_data in self.employee_expense_categories:
                employee_expense_categories_item = employee_expense_categories_item_data.to_dict()
                employee_expense_categories.append(employee_expense_categories_item)

        employer_liability_categories: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.employer_liability_categories, Unset):
            employer_liability_categories = []
            for employer_liability_categories_item_data in self.employer_liability_categories:
                employer_liability_categories_item = employer_liability_categories_item_data.to_dict()
                employer_liability_categories.append(employer_liability_categories_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if default_accounts is not UNSET:
            field_dict["defaultAccounts"] = default_accounts
        if leave_categories is not UNSET:
            field_dict["leaveCategories"] = leave_categories
        if location_id is not UNSET:
            field_dict["locationId"] = location_id
        if pay_categories is not UNSET:
            field_dict["payCategories"] = pay_categories
        if deduction_categories is not UNSET:
            field_dict["deductionCategories"] = deduction_categories
        if employee_expense_categories is not UNSET:
            field_dict["employeeExpenseCategories"] = employee_expense_categories
        if employer_liability_categories is not UNSET:
            field_dict["employerLiabilityCategories"] = employer_liability_categories

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.au_chart_of_accounts_location_accounts_model import AuChartOfAccountsLocationAccountsModel
        from ..models.chart_of_accounts_liability_location_category_model import (
            ChartOfAccountsLiabilityLocationCategoryModel,
        )
        from ..models.chart_of_accounts_location_category_model import ChartOfAccountsLocationCategoryModel
        from ..models.chart_of_accounts_location_leave_category_model import ChartOfAccountsLocationLeaveCategoryModel

        d = src_dict.copy()
        _default_accounts = d.pop("defaultAccounts", UNSET)
        default_accounts: Union[Unset, AuChartOfAccountsLocationAccountsModel]
        if isinstance(_default_accounts, Unset):
            default_accounts = UNSET
        else:
            default_accounts = AuChartOfAccountsLocationAccountsModel.from_dict(_default_accounts)

        leave_categories = []
        _leave_categories = d.pop("leaveCategories", UNSET)
        for leave_categories_item_data in _leave_categories or []:
            leave_categories_item = ChartOfAccountsLocationLeaveCategoryModel.from_dict(leave_categories_item_data)

            leave_categories.append(leave_categories_item)

        location_id = d.pop("locationId", UNSET)

        pay_categories = []
        _pay_categories = d.pop("payCategories", UNSET)
        for pay_categories_item_data in _pay_categories or []:
            pay_categories_item = ChartOfAccountsLocationCategoryModel.from_dict(pay_categories_item_data)

            pay_categories.append(pay_categories_item)

        deduction_categories = []
        _deduction_categories = d.pop("deductionCategories", UNSET)
        for deduction_categories_item_data in _deduction_categories or []:
            deduction_categories_item = ChartOfAccountsLiabilityLocationCategoryModel.from_dict(
                deduction_categories_item_data
            )

            deduction_categories.append(deduction_categories_item)

        employee_expense_categories = []
        _employee_expense_categories = d.pop("employeeExpenseCategories", UNSET)
        for employee_expense_categories_item_data in _employee_expense_categories or []:
            employee_expense_categories_item = ChartOfAccountsLocationCategoryModel.from_dict(
                employee_expense_categories_item_data
            )

            employee_expense_categories.append(employee_expense_categories_item)

        employer_liability_categories = []
        _employer_liability_categories = d.pop("employerLiabilityCategories", UNSET)
        for employer_liability_categories_item_data in _employer_liability_categories or []:
            employer_liability_categories_item = ChartOfAccountsLiabilityLocationCategoryModel.from_dict(
                employer_liability_categories_item_data
            )

            employer_liability_categories.append(employer_liability_categories_item)

        au_chart_of_accounts_location_group_model = cls(
            default_accounts=default_accounts,
            leave_categories=leave_categories,
            location_id=location_id,
            pay_categories=pay_categories,
            deduction_categories=deduction_categories,
            employee_expense_categories=employee_expense_categories,
            employer_liability_categories=employer_liability_categories,
        )

        au_chart_of_accounts_location_group_model.additional_properties = d
        return au_chart_of_accounts_location_group_model

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
