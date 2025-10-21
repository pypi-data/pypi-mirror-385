from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.au_initial_earnings_model_au_pay_category_type import AuInitialEarningsModelAuPayCategoryType
from ..types import UNSET, Unset

T = TypeVar("T", bound="AuInitialEarningsModel")


@_attrs_define
class AuInitialEarningsModel:
    """
    Attributes:
        pay_category_type (Union[Unset, AuInitialEarningsModelAuPayCategoryType]): <p><i>Note:</i> The amounts specified
            for any ETP-related pay categories (with the exception of Lump Sum D) must represent the total of the
            corresponding amounts supplied in the etps collection
        pay_category_id (Union[Unset, int]):
        is_standard_pay_category (Union[Unset, bool]):
        name (Union[Unset, str]):
        amount (Union[Unset, float]):
    """

    pay_category_type: Union[Unset, AuInitialEarningsModelAuPayCategoryType] = UNSET
    pay_category_id: Union[Unset, int] = UNSET
    is_standard_pay_category: Union[Unset, bool] = UNSET
    name: Union[Unset, str] = UNSET
    amount: Union[Unset, float] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        pay_category_type: Union[Unset, str] = UNSET
        if not isinstance(self.pay_category_type, Unset):
            pay_category_type = self.pay_category_type.value

        pay_category_id = self.pay_category_id

        is_standard_pay_category = self.is_standard_pay_category

        name = self.name

        amount = self.amount

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if pay_category_type is not UNSET:
            field_dict["payCategoryType"] = pay_category_type
        if pay_category_id is not UNSET:
            field_dict["payCategoryId"] = pay_category_id
        if is_standard_pay_category is not UNSET:
            field_dict["isStandardPayCategory"] = is_standard_pay_category
        if name is not UNSET:
            field_dict["name"] = name
        if amount is not UNSET:
            field_dict["amount"] = amount

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _pay_category_type = d.pop("payCategoryType", UNSET)
        pay_category_type: Union[Unset, AuInitialEarningsModelAuPayCategoryType]
        if isinstance(_pay_category_type, Unset):
            pay_category_type = UNSET
        else:
            pay_category_type = AuInitialEarningsModelAuPayCategoryType(_pay_category_type)

        pay_category_id = d.pop("payCategoryId", UNSET)

        is_standard_pay_category = d.pop("isStandardPayCategory", UNSET)

        name = d.pop("name", UNSET)

        amount = d.pop("amount", UNSET)

        au_initial_earnings_model = cls(
            pay_category_type=pay_category_type,
            pay_category_id=pay_category_id,
            is_standard_pay_category=is_standard_pay_category,
            name=name,
            amount=amount,
        )

        au_initial_earnings_model.additional_properties = d
        return au_initial_earnings_model

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
