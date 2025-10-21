from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.au_pay_run_deduction_response_dictionary_string_list_1 import (
        AuPayRunDeductionResponseDictionaryStringList1,
    )


T = TypeVar("T", bound="AuPayRunDeductionResponse")


@_attrs_define
class AuPayRunDeductionResponse:
    """
    Attributes:
        deductions (Union[Unset, AuPayRunDeductionResponseDictionaryStringList1]):
        pay_run_id (Union[Unset, int]):
    """

    deductions: Union[Unset, "AuPayRunDeductionResponseDictionaryStringList1"] = UNSET
    pay_run_id: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        deductions: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.deductions, Unset):
            deductions = self.deductions.to_dict()

        pay_run_id = self.pay_run_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if deductions is not UNSET:
            field_dict["deductions"] = deductions
        if pay_run_id is not UNSET:
            field_dict["payRunId"] = pay_run_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.au_pay_run_deduction_response_dictionary_string_list_1 import (
            AuPayRunDeductionResponseDictionaryStringList1,
        )

        d = src_dict.copy()
        _deductions = d.pop("deductions", UNSET)
        deductions: Union[Unset, AuPayRunDeductionResponseDictionaryStringList1]
        if isinstance(_deductions, Unset):
            deductions = UNSET
        else:
            deductions = AuPayRunDeductionResponseDictionaryStringList1.from_dict(_deductions)

        pay_run_id = d.pop("payRunId", UNSET)

        au_pay_run_deduction_response = cls(
            deductions=deductions,
            pay_run_id=pay_run_id,
        )

        au_pay_run_deduction_response.additional_properties = d
        return au_pay_run_deduction_response

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
