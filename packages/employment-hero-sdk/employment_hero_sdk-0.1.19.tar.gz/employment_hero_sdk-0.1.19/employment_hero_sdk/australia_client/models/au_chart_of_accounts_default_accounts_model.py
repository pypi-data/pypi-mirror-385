from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.au_chart_of_accounts_default_accounts_model_account_split import (
    AuChartOfAccountsDefaultAccountsModelAccountSplit,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="AuChartOfAccountsDefaultAccountsModel")


@_attrs_define
class AuChartOfAccountsDefaultAccountsModel:
    """
    Attributes:
        payment_account_split_by_location (Union[Unset, bool]):
        default_expense_split_by_location (Union[Unset, bool]):
        employee_expense_split_by_location (Union[Unset, bool]):
        employer_liability_expense_split_by_location (Union[Unset, bool]):
        employer_liability_liability_split_by_location (Union[Unset, bool]):
        default_liability_split_by_location (Union[Unset, bool]):
        payg_liability_account_split_by_location (Union[Unset, bool]):
        payg_expense_split_by_location (Union[Unset, bool]):
        superannuation_expense_split_by_location (Union[Unset, bool]):
        superannuation_liability_split_by_location (Union[Unset, bool]):
        payment_account_split (Union[Unset, AuChartOfAccountsDefaultAccountsModelAccountSplit]):
        default_expense_split (Union[Unset, AuChartOfAccountsDefaultAccountsModelAccountSplit]):
        employee_expense_split (Union[Unset, AuChartOfAccountsDefaultAccountsModelAccountSplit]):
        employer_liability_expense_split (Union[Unset, AuChartOfAccountsDefaultAccountsModelAccountSplit]):
        employer_liability_liability_split (Union[Unset, AuChartOfAccountsDefaultAccountsModelAccountSplit]):
        default_liability_split (Union[Unset, AuChartOfAccountsDefaultAccountsModelAccountSplit]):
        payg_liability_account_split (Union[Unset, AuChartOfAccountsDefaultAccountsModelAccountSplit]):
        payg_expense_split (Union[Unset, AuChartOfAccountsDefaultAccountsModelAccountSplit]):
        superannuation_expense_split (Union[Unset, AuChartOfAccountsDefaultAccountsModelAccountSplit]):
        superannuation_liability_split (Union[Unset, AuChartOfAccountsDefaultAccountsModelAccountSplit]):
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

    payment_account_split_by_location: Union[Unset, bool] = UNSET
    default_expense_split_by_location: Union[Unset, bool] = UNSET
    employee_expense_split_by_location: Union[Unset, bool] = UNSET
    employer_liability_expense_split_by_location: Union[Unset, bool] = UNSET
    employer_liability_liability_split_by_location: Union[Unset, bool] = UNSET
    default_liability_split_by_location: Union[Unset, bool] = UNSET
    payg_liability_account_split_by_location: Union[Unset, bool] = UNSET
    payg_expense_split_by_location: Union[Unset, bool] = UNSET
    superannuation_expense_split_by_location: Union[Unset, bool] = UNSET
    superannuation_liability_split_by_location: Union[Unset, bool] = UNSET
    payment_account_split: Union[Unset, AuChartOfAccountsDefaultAccountsModelAccountSplit] = UNSET
    default_expense_split: Union[Unset, AuChartOfAccountsDefaultAccountsModelAccountSplit] = UNSET
    employee_expense_split: Union[Unset, AuChartOfAccountsDefaultAccountsModelAccountSplit] = UNSET
    employer_liability_expense_split: Union[Unset, AuChartOfAccountsDefaultAccountsModelAccountSplit] = UNSET
    employer_liability_liability_split: Union[Unset, AuChartOfAccountsDefaultAccountsModelAccountSplit] = UNSET
    default_liability_split: Union[Unset, AuChartOfAccountsDefaultAccountsModelAccountSplit] = UNSET
    payg_liability_account_split: Union[Unset, AuChartOfAccountsDefaultAccountsModelAccountSplit] = UNSET
    payg_expense_split: Union[Unset, AuChartOfAccountsDefaultAccountsModelAccountSplit] = UNSET
    superannuation_expense_split: Union[Unset, AuChartOfAccountsDefaultAccountsModelAccountSplit] = UNSET
    superannuation_liability_split: Union[Unset, AuChartOfAccountsDefaultAccountsModelAccountSplit] = UNSET
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
        payment_account_split_by_location = self.payment_account_split_by_location

        default_expense_split_by_location = self.default_expense_split_by_location

        employee_expense_split_by_location = self.employee_expense_split_by_location

        employer_liability_expense_split_by_location = self.employer_liability_expense_split_by_location

        employer_liability_liability_split_by_location = self.employer_liability_liability_split_by_location

        default_liability_split_by_location = self.default_liability_split_by_location

        payg_liability_account_split_by_location = self.payg_liability_account_split_by_location

        payg_expense_split_by_location = self.payg_expense_split_by_location

        superannuation_expense_split_by_location = self.superannuation_expense_split_by_location

        superannuation_liability_split_by_location = self.superannuation_liability_split_by_location

        payment_account_split: Union[Unset, str] = UNSET
        if not isinstance(self.payment_account_split, Unset):
            payment_account_split = self.payment_account_split.value

        default_expense_split: Union[Unset, str] = UNSET
        if not isinstance(self.default_expense_split, Unset):
            default_expense_split = self.default_expense_split.value

        employee_expense_split: Union[Unset, str] = UNSET
        if not isinstance(self.employee_expense_split, Unset):
            employee_expense_split = self.employee_expense_split.value

        employer_liability_expense_split: Union[Unset, str] = UNSET
        if not isinstance(self.employer_liability_expense_split, Unset):
            employer_liability_expense_split = self.employer_liability_expense_split.value

        employer_liability_liability_split: Union[Unset, str] = UNSET
        if not isinstance(self.employer_liability_liability_split, Unset):
            employer_liability_liability_split = self.employer_liability_liability_split.value

        default_liability_split: Union[Unset, str] = UNSET
        if not isinstance(self.default_liability_split, Unset):
            default_liability_split = self.default_liability_split.value

        payg_liability_account_split: Union[Unset, str] = UNSET
        if not isinstance(self.payg_liability_account_split, Unset):
            payg_liability_account_split = self.payg_liability_account_split.value

        payg_expense_split: Union[Unset, str] = UNSET
        if not isinstance(self.payg_expense_split, Unset):
            payg_expense_split = self.payg_expense_split.value

        superannuation_expense_split: Union[Unset, str] = UNSET
        if not isinstance(self.superannuation_expense_split, Unset):
            superannuation_expense_split = self.superannuation_expense_split.value

        superannuation_liability_split: Union[Unset, str] = UNSET
        if not isinstance(self.superannuation_liability_split, Unset):
            superannuation_liability_split = self.superannuation_liability_split.value

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
        if payment_account_split_by_location is not UNSET:
            field_dict["paymentAccountSplitByLocation"] = payment_account_split_by_location
        if default_expense_split_by_location is not UNSET:
            field_dict["defaultExpenseSplitByLocation"] = default_expense_split_by_location
        if employee_expense_split_by_location is not UNSET:
            field_dict["employeeExpenseSplitByLocation"] = employee_expense_split_by_location
        if employer_liability_expense_split_by_location is not UNSET:
            field_dict["employerLiabilityExpenseSplitByLocation"] = employer_liability_expense_split_by_location
        if employer_liability_liability_split_by_location is not UNSET:
            field_dict["employerLiabilityLiabilitySplitByLocation"] = employer_liability_liability_split_by_location
        if default_liability_split_by_location is not UNSET:
            field_dict["defaultLiabilitySplitByLocation"] = default_liability_split_by_location
        if payg_liability_account_split_by_location is not UNSET:
            field_dict["paygLiabilityAccountSplitByLocation"] = payg_liability_account_split_by_location
        if payg_expense_split_by_location is not UNSET:
            field_dict["paygExpenseSplitByLocation"] = payg_expense_split_by_location
        if superannuation_expense_split_by_location is not UNSET:
            field_dict["superannuationExpenseSplitByLocation"] = superannuation_expense_split_by_location
        if superannuation_liability_split_by_location is not UNSET:
            field_dict["superannuationLiabilitySplitByLocation"] = superannuation_liability_split_by_location
        if payment_account_split is not UNSET:
            field_dict["paymentAccountSplit"] = payment_account_split
        if default_expense_split is not UNSET:
            field_dict["defaultExpenseSplit"] = default_expense_split
        if employee_expense_split is not UNSET:
            field_dict["employeeExpenseSplit"] = employee_expense_split
        if employer_liability_expense_split is not UNSET:
            field_dict["employerLiabilityExpenseSplit"] = employer_liability_expense_split
        if employer_liability_liability_split is not UNSET:
            field_dict["employerLiabilityLiabilitySplit"] = employer_liability_liability_split
        if default_liability_split is not UNSET:
            field_dict["defaultLiabilitySplit"] = default_liability_split
        if payg_liability_account_split is not UNSET:
            field_dict["paygLiabilityAccountSplit"] = payg_liability_account_split
        if payg_expense_split is not UNSET:
            field_dict["paygExpenseSplit"] = payg_expense_split
        if superannuation_expense_split is not UNSET:
            field_dict["superannuationExpenseSplit"] = superannuation_expense_split
        if superannuation_liability_split is not UNSET:
            field_dict["superannuationLiabilitySplit"] = superannuation_liability_split
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
        payment_account_split_by_location = d.pop("paymentAccountSplitByLocation", UNSET)

        default_expense_split_by_location = d.pop("defaultExpenseSplitByLocation", UNSET)

        employee_expense_split_by_location = d.pop("employeeExpenseSplitByLocation", UNSET)

        employer_liability_expense_split_by_location = d.pop("employerLiabilityExpenseSplitByLocation", UNSET)

        employer_liability_liability_split_by_location = d.pop("employerLiabilityLiabilitySplitByLocation", UNSET)

        default_liability_split_by_location = d.pop("defaultLiabilitySplitByLocation", UNSET)

        payg_liability_account_split_by_location = d.pop("paygLiabilityAccountSplitByLocation", UNSET)

        payg_expense_split_by_location = d.pop("paygExpenseSplitByLocation", UNSET)

        superannuation_expense_split_by_location = d.pop("superannuationExpenseSplitByLocation", UNSET)

        superannuation_liability_split_by_location = d.pop("superannuationLiabilitySplitByLocation", UNSET)

        _payment_account_split = d.pop("paymentAccountSplit", UNSET)
        payment_account_split: Union[Unset, AuChartOfAccountsDefaultAccountsModelAccountSplit]
        if isinstance(_payment_account_split, Unset):
            payment_account_split = UNSET
        else:
            payment_account_split = AuChartOfAccountsDefaultAccountsModelAccountSplit(_payment_account_split)

        _default_expense_split = d.pop("defaultExpenseSplit", UNSET)
        default_expense_split: Union[Unset, AuChartOfAccountsDefaultAccountsModelAccountSplit]
        if isinstance(_default_expense_split, Unset):
            default_expense_split = UNSET
        else:
            default_expense_split = AuChartOfAccountsDefaultAccountsModelAccountSplit(_default_expense_split)

        _employee_expense_split = d.pop("employeeExpenseSplit", UNSET)
        employee_expense_split: Union[Unset, AuChartOfAccountsDefaultAccountsModelAccountSplit]
        if isinstance(_employee_expense_split, Unset):
            employee_expense_split = UNSET
        else:
            employee_expense_split = AuChartOfAccountsDefaultAccountsModelAccountSplit(_employee_expense_split)

        _employer_liability_expense_split = d.pop("employerLiabilityExpenseSplit", UNSET)
        employer_liability_expense_split: Union[Unset, AuChartOfAccountsDefaultAccountsModelAccountSplit]
        if isinstance(_employer_liability_expense_split, Unset):
            employer_liability_expense_split = UNSET
        else:
            employer_liability_expense_split = AuChartOfAccountsDefaultAccountsModelAccountSplit(
                _employer_liability_expense_split
            )

        _employer_liability_liability_split = d.pop("employerLiabilityLiabilitySplit", UNSET)
        employer_liability_liability_split: Union[Unset, AuChartOfAccountsDefaultAccountsModelAccountSplit]
        if isinstance(_employer_liability_liability_split, Unset):
            employer_liability_liability_split = UNSET
        else:
            employer_liability_liability_split = AuChartOfAccountsDefaultAccountsModelAccountSplit(
                _employer_liability_liability_split
            )

        _default_liability_split = d.pop("defaultLiabilitySplit", UNSET)
        default_liability_split: Union[Unset, AuChartOfAccountsDefaultAccountsModelAccountSplit]
        if isinstance(_default_liability_split, Unset):
            default_liability_split = UNSET
        else:
            default_liability_split = AuChartOfAccountsDefaultAccountsModelAccountSplit(_default_liability_split)

        _payg_liability_account_split = d.pop("paygLiabilityAccountSplit", UNSET)
        payg_liability_account_split: Union[Unset, AuChartOfAccountsDefaultAccountsModelAccountSplit]
        if isinstance(_payg_liability_account_split, Unset):
            payg_liability_account_split = UNSET
        else:
            payg_liability_account_split = AuChartOfAccountsDefaultAccountsModelAccountSplit(
                _payg_liability_account_split
            )

        _payg_expense_split = d.pop("paygExpenseSplit", UNSET)
        payg_expense_split: Union[Unset, AuChartOfAccountsDefaultAccountsModelAccountSplit]
        if isinstance(_payg_expense_split, Unset):
            payg_expense_split = UNSET
        else:
            payg_expense_split = AuChartOfAccountsDefaultAccountsModelAccountSplit(_payg_expense_split)

        _superannuation_expense_split = d.pop("superannuationExpenseSplit", UNSET)
        superannuation_expense_split: Union[Unset, AuChartOfAccountsDefaultAccountsModelAccountSplit]
        if isinstance(_superannuation_expense_split, Unset):
            superannuation_expense_split = UNSET
        else:
            superannuation_expense_split = AuChartOfAccountsDefaultAccountsModelAccountSplit(
                _superannuation_expense_split
            )

        _superannuation_liability_split = d.pop("superannuationLiabilitySplit", UNSET)
        superannuation_liability_split: Union[Unset, AuChartOfAccountsDefaultAccountsModelAccountSplit]
        if isinstance(_superannuation_liability_split, Unset):
            superannuation_liability_split = UNSET
        else:
            superannuation_liability_split = AuChartOfAccountsDefaultAccountsModelAccountSplit(
                _superannuation_liability_split
            )

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

        au_chart_of_accounts_default_accounts_model = cls(
            payment_account_split_by_location=payment_account_split_by_location,
            default_expense_split_by_location=default_expense_split_by_location,
            employee_expense_split_by_location=employee_expense_split_by_location,
            employer_liability_expense_split_by_location=employer_liability_expense_split_by_location,
            employer_liability_liability_split_by_location=employer_liability_liability_split_by_location,
            default_liability_split_by_location=default_liability_split_by_location,
            payg_liability_account_split_by_location=payg_liability_account_split_by_location,
            payg_expense_split_by_location=payg_expense_split_by_location,
            superannuation_expense_split_by_location=superannuation_expense_split_by_location,
            superannuation_liability_split_by_location=superannuation_liability_split_by_location,
            payment_account_split=payment_account_split,
            default_expense_split=default_expense_split,
            employee_expense_split=employee_expense_split,
            employer_liability_expense_split=employer_liability_expense_split,
            employer_liability_liability_split=employer_liability_liability_split,
            default_liability_split=default_liability_split,
            payg_liability_account_split=payg_liability_account_split,
            payg_expense_split=payg_expense_split,
            superannuation_expense_split=superannuation_expense_split,
            superannuation_liability_split=superannuation_liability_split,
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

        au_chart_of_accounts_default_accounts_model.additional_properties = d
        return au_chart_of_accounts_default_accounts_model

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
