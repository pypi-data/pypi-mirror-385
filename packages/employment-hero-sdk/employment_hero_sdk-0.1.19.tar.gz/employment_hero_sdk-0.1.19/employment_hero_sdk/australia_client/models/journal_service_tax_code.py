from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="JournalServiceTaxCode")


@_attrs_define
class JournalServiceTaxCode:
    """
    Attributes:
        id (Union[Unset, str]):
        name (Union[Unset, str]):
        tax_rate (Union[Unset, float]):
    """

    id: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    tax_rate: Union[Unset, float] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        name = self.name

        tax_rate = self.tax_rate

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if tax_rate is not UNSET:
            field_dict["taxRate"] = tax_rate

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        tax_rate = d.pop("taxRate", UNSET)

        journal_service_tax_code = cls(
            id=id,
            name=name,
            tax_rate=tax_rate,
        )

        journal_service_tax_code.additional_properties = d
        return journal_service_tax_code

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
