from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.pay_run_employer_liability_response_dictionary_string_list_1 import (
        PayRunEmployerLiabilityResponseDictionaryStringList1,
    )


T = TypeVar("T", bound="PayRunEmployerLiabilityResponse")


@_attrs_define
class PayRunEmployerLiabilityResponse:
    """
    Attributes:
        employer_liabilities (Union[Unset, PayRunEmployerLiabilityResponseDictionaryStringList1]):
        pay_run_id (Union[Unset, int]):
    """

    employer_liabilities: Union[Unset, "PayRunEmployerLiabilityResponseDictionaryStringList1"] = UNSET
    pay_run_id: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        employer_liabilities: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.employer_liabilities, Unset):
            employer_liabilities = self.employer_liabilities.to_dict()

        pay_run_id = self.pay_run_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if employer_liabilities is not UNSET:
            field_dict["employerLiabilities"] = employer_liabilities
        if pay_run_id is not UNSET:
            field_dict["payRunId"] = pay_run_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.pay_run_employer_liability_response_dictionary_string_list_1 import (
            PayRunEmployerLiabilityResponseDictionaryStringList1,
        )

        d = src_dict.copy()
        _employer_liabilities = d.pop("employerLiabilities", UNSET)
        employer_liabilities: Union[Unset, PayRunEmployerLiabilityResponseDictionaryStringList1]
        if isinstance(_employer_liabilities, Unset):
            employer_liabilities = UNSET
        else:
            employer_liabilities = PayRunEmployerLiabilityResponseDictionaryStringList1.from_dict(_employer_liabilities)

        pay_run_id = d.pop("payRunId", UNSET)

        pay_run_employer_liability_response = cls(
            employer_liabilities=employer_liabilities,
            pay_run_id=pay_run_id,
        )

        pay_run_employer_liability_response.additional_properties = d
        return pay_run_employer_liability_response

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
