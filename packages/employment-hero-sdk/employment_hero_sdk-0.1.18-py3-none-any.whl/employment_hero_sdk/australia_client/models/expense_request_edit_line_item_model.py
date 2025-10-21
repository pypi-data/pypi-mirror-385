import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="ExpenseRequestEditLineItemModel")


@_attrs_define
class ExpenseRequestEditLineItemModel:
    """
    Attributes:
        id (Union[Unset, int]):
        expense_category_id (Union[Unset, int]):
        location_id (Union[Unset, int]):
        notes (Union[Unset, str]):
        tax_code (Union[Unset, str]):
        tax_code_display_name (Union[Unset, str]):
        tax_rate (Union[Unset, float]):
        amount (Union[Unset, float]):
        date_incurred (Union[Unset, datetime.datetime]):
    """

    id: Union[Unset, int] = UNSET
    expense_category_id: Union[Unset, int] = UNSET
    location_id: Union[Unset, int] = UNSET
    notes: Union[Unset, str] = UNSET
    tax_code: Union[Unset, str] = UNSET
    tax_code_display_name: Union[Unset, str] = UNSET
    tax_rate: Union[Unset, float] = UNSET
    amount: Union[Unset, float] = UNSET
    date_incurred: Union[Unset, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        expense_category_id = self.expense_category_id

        location_id = self.location_id

        notes = self.notes

        tax_code = self.tax_code

        tax_code_display_name = self.tax_code_display_name

        tax_rate = self.tax_rate

        amount = self.amount

        date_incurred: Union[Unset, str] = UNSET
        if not isinstance(self.date_incurred, Unset):
            date_incurred = self.date_incurred.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if expense_category_id is not UNSET:
            field_dict["expenseCategoryId"] = expense_category_id
        if location_id is not UNSET:
            field_dict["locationId"] = location_id
        if notes is not UNSET:
            field_dict["notes"] = notes
        if tax_code is not UNSET:
            field_dict["taxCode"] = tax_code
        if tax_code_display_name is not UNSET:
            field_dict["taxCodeDisplayName"] = tax_code_display_name
        if tax_rate is not UNSET:
            field_dict["taxRate"] = tax_rate
        if amount is not UNSET:
            field_dict["amount"] = amount
        if date_incurred is not UNSET:
            field_dict["dateIncurred"] = date_incurred

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        expense_category_id = d.pop("expenseCategoryId", UNSET)

        location_id = d.pop("locationId", UNSET)

        notes = d.pop("notes", UNSET)

        tax_code = d.pop("taxCode", UNSET)

        tax_code_display_name = d.pop("taxCodeDisplayName", UNSET)

        tax_rate = d.pop("taxRate", UNSET)

        amount = d.pop("amount", UNSET)

        _date_incurred = d.pop("dateIncurred", UNSET)
        date_incurred: Union[Unset, datetime.datetime]
        if isinstance(_date_incurred, Unset):
            date_incurred = UNSET
        else:
            date_incurred = isoparse(_date_incurred)

        expense_request_edit_line_item_model = cls(
            id=id,
            expense_category_id=expense_category_id,
            location_id=location_id,
            notes=notes,
            tax_code=tax_code,
            tax_code_display_name=tax_code_display_name,
            tax_rate=tax_rate,
            amount=amount,
            date_incurred=date_incurred,
        )

        expense_request_edit_line_item_model.additional_properties = d
        return expense_request_edit_line_item_model

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
