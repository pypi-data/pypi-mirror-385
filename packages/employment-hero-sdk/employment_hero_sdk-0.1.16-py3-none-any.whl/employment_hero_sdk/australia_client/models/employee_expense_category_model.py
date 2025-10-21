from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="EmployeeExpenseCategoryModel")


@_attrs_define
class EmployeeExpenseCategoryModel:
    """
    Attributes:
        id (Union[Unset, int]):
        name (Union[Unset, str]):
        external_id (Union[Unset, str]):
        general_ledger_mapping_code (Union[Unset, str]):
        description (Union[Unset, str]):
        external_reference_id (Union[Unset, str]):
        external_tax_code_id (Union[Unset, str]):
        tax_code (Union[Unset, str]):
        tax_rate (Union[Unset, float]):
    """

    id: Union[Unset, int] = UNSET
    name: Union[Unset, str] = UNSET
    external_id: Union[Unset, str] = UNSET
    general_ledger_mapping_code: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    external_reference_id: Union[Unset, str] = UNSET
    external_tax_code_id: Union[Unset, str] = UNSET
    tax_code: Union[Unset, str] = UNSET
    tax_rate: Union[Unset, float] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        name = self.name

        external_id = self.external_id

        general_ledger_mapping_code = self.general_ledger_mapping_code

        description = self.description

        external_reference_id = self.external_reference_id

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
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if general_ledger_mapping_code is not UNSET:
            field_dict["generalLedgerMappingCode"] = general_ledger_mapping_code
        if description is not UNSET:
            field_dict["description"] = description
        if external_reference_id is not UNSET:
            field_dict["externalReferenceId"] = external_reference_id
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

        external_id = d.pop("externalId", UNSET)

        general_ledger_mapping_code = d.pop("generalLedgerMappingCode", UNSET)

        description = d.pop("description", UNSET)

        external_reference_id = d.pop("externalReferenceId", UNSET)

        external_tax_code_id = d.pop("externalTaxCodeId", UNSET)

        tax_code = d.pop("taxCode", UNSET)

        tax_rate = d.pop("taxRate", UNSET)

        employee_expense_category_model = cls(
            id=id,
            name=name,
            external_id=external_id,
            general_ledger_mapping_code=general_ledger_mapping_code,
            description=description,
            external_reference_id=external_reference_id,
            external_tax_code_id=external_tax_code_id,
            tax_code=tax_code,
            tax_rate=tax_rate,
        )

        employee_expense_category_model.additional_properties = d
        return employee_expense_category_model

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
