from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="InitialEmployerLiabilityModel")


@_attrs_define
class InitialEmployerLiabilityModel:
    """
    Attributes:
        employer_liability_category_id (Union[Unset, int]):
        name (Union[Unset, str]):
        amount (Union[Unset, float]):
    """

    employer_liability_category_id: Union[Unset, int] = UNSET
    name: Union[Unset, str] = UNSET
    amount: Union[Unset, float] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        employer_liability_category_id = self.employer_liability_category_id

        name = self.name

        amount = self.amount

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if employer_liability_category_id is not UNSET:
            field_dict["employerLiabilityCategoryId"] = employer_liability_category_id
        if name is not UNSET:
            field_dict["name"] = name
        if amount is not UNSET:
            field_dict["amount"] = amount

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        employer_liability_category_id = d.pop("employerLiabilityCategoryId", UNSET)

        name = d.pop("name", UNSET)

        amount = d.pop("amount", UNSET)

        initial_employer_liability_model = cls(
            employer_liability_category_id=employer_liability_category_id,
            name=name,
            amount=amount,
        )

        initial_employer_liability_model.additional_properties = d
        return initial_employer_liability_model

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
