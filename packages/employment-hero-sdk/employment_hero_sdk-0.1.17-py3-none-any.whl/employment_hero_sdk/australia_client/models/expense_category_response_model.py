from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ExpenseCategoryResponseModel")


@_attrs_define
class ExpenseCategoryResponseModel:
    """
    Attributes:
        id (Union[Unset, int]):
        name (Union[Unset, str]):
        external_tax_code_id (Union[Unset, str]):
        tax_code (Union[Unset, str]):
        tax_rate (Union[Unset, float]):
    """

    id: Union[Unset, int] = UNSET
    name: Union[Unset, str] = UNSET
    external_tax_code_id: Union[Unset, str] = UNSET
    tax_code: Union[Unset, str] = UNSET
    tax_rate: Union[Unset, float] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        name = self.name

        external_tax_code_id = self.external_tax_code_id

        tax_code = self.tax_code

        tax_rate = self.tax_rate

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if external_tax_code_id is not UNSET:
            field_dict["externalTaxCodeId"] = external_tax_code_id
        if tax_code is not UNSET:
            field_dict["taxCode"] = tax_code
        if tax_rate is not UNSET:
            field_dict["taxRate"] = tax_rate

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        external_tax_code_id = d.pop("externalTaxCodeId", UNSET)

        tax_code = d.pop("taxCode", UNSET)

        tax_rate = d.pop("taxRate", UNSET)

        expense_category_response_model = cls(
            id=id,
            name=name,
            external_tax_code_id=external_tax_code_id,
            tax_code=tax_code,
            tax_rate=tax_rate,
        )

        expense_category_response_model.additional_properties = d
        return expense_category_response_model

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
