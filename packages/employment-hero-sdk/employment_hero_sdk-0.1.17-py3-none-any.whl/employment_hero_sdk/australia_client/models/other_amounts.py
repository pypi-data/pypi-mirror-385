from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="OtherAmounts")


@_attrs_define
class OtherAmounts:
    """
    Attributes:
        work_place_giving (Union[Unset, float]):
        exempt_foreign_exempt_income (Union[Unset, float]):
        deductible_amount_of_undeducted_annuity_price (Union[Unset, float]):
    """

    work_place_giving: Union[Unset, float] = UNSET
    exempt_foreign_exempt_income: Union[Unset, float] = UNSET
    deductible_amount_of_undeducted_annuity_price: Union[Unset, float] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        work_place_giving = self.work_place_giving

        exempt_foreign_exempt_income = self.exempt_foreign_exempt_income

        deductible_amount_of_undeducted_annuity_price = self.deductible_amount_of_undeducted_annuity_price

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if work_place_giving is not UNSET:
            field_dict["workPlaceGiving"] = work_place_giving
        if exempt_foreign_exempt_income is not UNSET:
            field_dict["exemptForeignExemptIncome"] = exempt_foreign_exempt_income
        if deductible_amount_of_undeducted_annuity_price is not UNSET:
            field_dict["deductibleAmountOfUndeductedAnnuityPrice"] = deductible_amount_of_undeducted_annuity_price

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        work_place_giving = d.pop("workPlaceGiving", UNSET)

        exempt_foreign_exempt_income = d.pop("exemptForeignExemptIncome", UNSET)

        deductible_amount_of_undeducted_annuity_price = d.pop("deductibleAmountOfUndeductedAnnuityPrice", UNSET)

        other_amounts = cls(
            work_place_giving=work_place_giving,
            exempt_foreign_exempt_income=exempt_foreign_exempt_income,
            deductible_amount_of_undeducted_annuity_price=deductible_amount_of_undeducted_annuity_price,
        )

        other_amounts.additional_properties = d
        return other_amounts

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
