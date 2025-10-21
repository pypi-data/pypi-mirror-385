from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AuChartOfAccountsLocationAccountsModel")


@_attrs_define
class AuChartOfAccountsLocationAccountsModel:
    """
    Attributes:
        payg_liability_account_id (Union[Unset, int]):
        payg_expense_account_id (Union[Unset, int]):
        superannuation_expense_account_id (Union[Unset, int]):
        superannuation_liability_account_id (Union[Unset, int]):
        payment_account_id (Union[Unset, int]):
        default_expense_account_id (Union[Unset, int]):
        employee_expense_account_id (Union[Unset, int]):
        employer_liability_expense_account_id (Union[Unset, int]):
        employer_liability_liability_account_id (Union[Unset, int]):
        default_liability_account_id (Union[Unset, int]):
    """

    payg_liability_account_id: Union[Unset, int] = UNSET
    payg_expense_account_id: Union[Unset, int] = UNSET
    superannuation_expense_account_id: Union[Unset, int] = UNSET
    superannuation_liability_account_id: Union[Unset, int] = UNSET
    payment_account_id: Union[Unset, int] = UNSET
    default_expense_account_id: Union[Unset, int] = UNSET
    employee_expense_account_id: Union[Unset, int] = UNSET
    employer_liability_expense_account_id: Union[Unset, int] = UNSET
    employer_liability_liability_account_id: Union[Unset, int] = UNSET
    default_liability_account_id: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        payg_liability_account_id = self.payg_liability_account_id

        payg_expense_account_id = self.payg_expense_account_id

        superannuation_expense_account_id = self.superannuation_expense_account_id

        superannuation_liability_account_id = self.superannuation_liability_account_id

        payment_account_id = self.payment_account_id

        default_expense_account_id = self.default_expense_account_id

        employee_expense_account_id = self.employee_expense_account_id

        employer_liability_expense_account_id = self.employer_liability_expense_account_id

        employer_liability_liability_account_id = self.employer_liability_liability_account_id

        default_liability_account_id = self.default_liability_account_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if payg_liability_account_id is not UNSET:
            field_dict["paygLiabilityAccountId"] = payg_liability_account_id
        if payg_expense_account_id is not UNSET:
            field_dict["paygExpenseAccountId"] = payg_expense_account_id
        if superannuation_expense_account_id is not UNSET:
            field_dict["superannuationExpenseAccountId"] = superannuation_expense_account_id
        if superannuation_liability_account_id is not UNSET:
            field_dict["superannuationLiabilityAccountId"] = superannuation_liability_account_id
        if payment_account_id is not UNSET:
            field_dict["paymentAccountId"] = payment_account_id
        if default_expense_account_id is not UNSET:
            field_dict["defaultExpenseAccountId"] = default_expense_account_id
        if employee_expense_account_id is not UNSET:
            field_dict["employeeExpenseAccountId"] = employee_expense_account_id
        if employer_liability_expense_account_id is not UNSET:
            field_dict["employerLiabilityExpenseAccountId"] = employer_liability_expense_account_id
        if employer_liability_liability_account_id is not UNSET:
            field_dict["employerLiabilityLiabilityAccountId"] = employer_liability_liability_account_id
        if default_liability_account_id is not UNSET:
            field_dict["defaultLiabilityAccountId"] = default_liability_account_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        payg_liability_account_id = d.pop("paygLiabilityAccountId", UNSET)

        payg_expense_account_id = d.pop("paygExpenseAccountId", UNSET)

        superannuation_expense_account_id = d.pop("superannuationExpenseAccountId", UNSET)

        superannuation_liability_account_id = d.pop("superannuationLiabilityAccountId", UNSET)

        payment_account_id = d.pop("paymentAccountId", UNSET)

        default_expense_account_id = d.pop("defaultExpenseAccountId", UNSET)

        employee_expense_account_id = d.pop("employeeExpenseAccountId", UNSET)

        employer_liability_expense_account_id = d.pop("employerLiabilityExpenseAccountId", UNSET)

        employer_liability_liability_account_id = d.pop("employerLiabilityLiabilityAccountId", UNSET)

        default_liability_account_id = d.pop("defaultLiabilityAccountId", UNSET)

        au_chart_of_accounts_location_accounts_model = cls(
            payg_liability_account_id=payg_liability_account_id,
            payg_expense_account_id=payg_expense_account_id,
            superannuation_expense_account_id=superannuation_expense_account_id,
            superannuation_liability_account_id=superannuation_liability_account_id,
            payment_account_id=payment_account_id,
            default_expense_account_id=default_expense_account_id,
            employee_expense_account_id=employee_expense_account_id,
            employer_liability_expense_account_id=employer_liability_expense_account_id,
            employer_liability_liability_account_id=employer_liability_liability_account_id,
            default_liability_account_id=default_liability_account_id,
        )

        au_chart_of_accounts_location_accounts_model.additional_properties = d
        return au_chart_of_accounts_location_accounts_model

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
