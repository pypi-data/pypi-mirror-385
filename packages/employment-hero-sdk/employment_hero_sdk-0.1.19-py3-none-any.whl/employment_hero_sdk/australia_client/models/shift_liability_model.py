from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.shift_liability_model_shift_allowance_option import ShiftLiabilityModelShiftAllowanceOption
from ..types import UNSET, Unset

T = TypeVar("T", bound="ShiftLiabilityModel")


@_attrs_define
class ShiftLiabilityModel:
    """
    Attributes:
        liability_category_name (Union[Unset, str]):
        liability_category_id (Union[Unset, int]):
        include_in_shift_cost (Union[Unset, bool]):
        amount (Union[Unset, float]):
        option (Union[Unset, ShiftLiabilityModelShiftAllowanceOption]):
        cost (Union[Unset, float]):
    """

    liability_category_name: Union[Unset, str] = UNSET
    liability_category_id: Union[Unset, int] = UNSET
    include_in_shift_cost: Union[Unset, bool] = UNSET
    amount: Union[Unset, float] = UNSET
    option: Union[Unset, ShiftLiabilityModelShiftAllowanceOption] = UNSET
    cost: Union[Unset, float] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        liability_category_name = self.liability_category_name

        liability_category_id = self.liability_category_id

        include_in_shift_cost = self.include_in_shift_cost

        amount = self.amount

        option: Union[Unset, str] = UNSET
        if not isinstance(self.option, Unset):
            option = self.option.value

        cost = self.cost

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if liability_category_name is not UNSET:
            field_dict["liabilityCategoryName"] = liability_category_name
        if liability_category_id is not UNSET:
            field_dict["liabilityCategoryId"] = liability_category_id
        if include_in_shift_cost is not UNSET:
            field_dict["includeInShiftCost"] = include_in_shift_cost
        if amount is not UNSET:
            field_dict["amount"] = amount
        if option is not UNSET:
            field_dict["option"] = option
        if cost is not UNSET:
            field_dict["cost"] = cost

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        liability_category_name = d.pop("liabilityCategoryName", UNSET)

        liability_category_id = d.pop("liabilityCategoryId", UNSET)

        include_in_shift_cost = d.pop("includeInShiftCost", UNSET)

        amount = d.pop("amount", UNSET)

        _option = d.pop("option", UNSET)
        option: Union[Unset, ShiftLiabilityModelShiftAllowanceOption]
        if isinstance(_option, Unset):
            option = UNSET
        else:
            option = ShiftLiabilityModelShiftAllowanceOption(_option)

        cost = d.pop("cost", UNSET)

        shift_liability_model = cls(
            liability_category_name=liability_category_name,
            liability_category_id=liability_category_id,
            include_in_shift_cost=include_in_shift_cost,
            amount=amount,
            option=option,
            cost=cost,
        )

        shift_liability_model.additional_properties = d
        return shift_liability_model

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
