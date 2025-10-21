from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DeductionsReportDeductionAmountModel")


@_attrs_define
class DeductionsReportDeductionAmountModel:
    """
    Attributes:
        deduction_category_id (Union[Unset, int]):
        deduction_category_name (Union[Unset, str]):
        amount (Union[Unset, float]):
    """

    deduction_category_id: Union[Unset, int] = UNSET
    deduction_category_name: Union[Unset, str] = UNSET
    amount: Union[Unset, float] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        deduction_category_id = self.deduction_category_id

        deduction_category_name = self.deduction_category_name

        amount = self.amount

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if deduction_category_id is not UNSET:
            field_dict["deductionCategoryId"] = deduction_category_id
        if deduction_category_name is not UNSET:
            field_dict["deductionCategoryName"] = deduction_category_name
        if amount is not UNSET:
            field_dict["amount"] = amount

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        deduction_category_id = d.pop("deductionCategoryId", UNSET)

        deduction_category_name = d.pop("deductionCategoryName", UNSET)

        amount = d.pop("amount", UNSET)

        deductions_report_deduction_amount_model = cls(
            deduction_category_id=deduction_category_id,
            deduction_category_name=deduction_category_name,
            amount=amount,
        )

        deductions_report_deduction_amount_model.additional_properties = d
        return deductions_report_deduction_amount_model

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
