from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ExpenseTaxCode")


@_attrs_define
class ExpenseTaxCode:
    """
    Attributes:
        tax_code (Union[Unset, str]):
        tax_code_display_name (Union[Unset, str]):
        tax_rate (Union[Unset, float]):
    """

    tax_code: Union[Unset, str] = UNSET
    tax_code_display_name: Union[Unset, str] = UNSET
    tax_rate: Union[Unset, float] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        tax_code = self.tax_code

        tax_code_display_name = self.tax_code_display_name

        tax_rate = self.tax_rate

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if tax_code is not UNSET:
            field_dict["taxCode"] = tax_code
        if tax_code_display_name is not UNSET:
            field_dict["taxCodeDisplayName"] = tax_code_display_name
        if tax_rate is not UNSET:
            field_dict["taxRate"] = tax_rate

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        tax_code = d.pop("taxCode", UNSET)

        tax_code_display_name = d.pop("taxCodeDisplayName", UNSET)

        tax_rate = d.pop("taxRate", UNSET)

        expense_tax_code = cls(
            tax_code=tax_code,
            tax_code_display_name=tax_code_display_name,
            tax_rate=tax_rate,
        )

        expense_tax_code.additional_properties = d
        return expense_tax_code

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
