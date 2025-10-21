from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ChartOfAccountsLiabilityCategoryModel")


@_attrs_define
class ChartOfAccountsLiabilityCategoryModel:
    """
    Attributes:
        liability_account_id (Union[Unset, int]):
        split_by_location (Union[Unset, bool]):
        id (Union[Unset, int]):
        name (Union[Unset, str]):
        expense_account_id (Union[Unset, int]):
    """

    liability_account_id: Union[Unset, int] = UNSET
    split_by_location: Union[Unset, bool] = UNSET
    id: Union[Unset, int] = UNSET
    name: Union[Unset, str] = UNSET
    expense_account_id: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        liability_account_id = self.liability_account_id

        split_by_location = self.split_by_location

        id = self.id

        name = self.name

        expense_account_id = self.expense_account_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if liability_account_id is not UNSET:
            field_dict["liabilityAccountId"] = liability_account_id
        if split_by_location is not UNSET:
            field_dict["splitByLocation"] = split_by_location
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if expense_account_id is not UNSET:
            field_dict["expenseAccountId"] = expense_account_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        liability_account_id = d.pop("liabilityAccountId", UNSET)

        split_by_location = d.pop("splitByLocation", UNSET)

        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        expense_account_id = d.pop("expenseAccountId", UNSET)

        chart_of_accounts_liability_category_model = cls(
            liability_account_id=liability_account_id,
            split_by_location=split_by_location,
            id=id,
            name=name,
            expense_account_id=expense_account_id,
        )

        chart_of_accounts_liability_category_model.additional_properties = d
        return chart_of_accounts_liability_category_model

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
