from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.au_pay_run_total_response_dictionary_string_au_pay_run_total_model import (
        AuPayRunTotalResponseDictionaryStringAuPayRunTotalModel,
    )


T = TypeVar("T", bound="AuPayRunTotalResponse")


@_attrs_define
class AuPayRunTotalResponse:
    """
    Attributes:
        pay_run_id (Union[Unset, int]):
        pay_run_totals (Union[Unset, AuPayRunTotalResponseDictionaryStringAuPayRunTotalModel]):
    """

    pay_run_id: Union[Unset, int] = UNSET
    pay_run_totals: Union[Unset, "AuPayRunTotalResponseDictionaryStringAuPayRunTotalModel"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        pay_run_id = self.pay_run_id

        pay_run_totals: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.pay_run_totals, Unset):
            pay_run_totals = self.pay_run_totals.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if pay_run_id is not UNSET:
            field_dict["payRunId"] = pay_run_id
        if pay_run_totals is not UNSET:
            field_dict["payRunTotals"] = pay_run_totals

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.au_pay_run_total_response_dictionary_string_au_pay_run_total_model import (
            AuPayRunTotalResponseDictionaryStringAuPayRunTotalModel,
        )

        d = src_dict.copy()
        pay_run_id = d.pop("payRunId", UNSET)

        _pay_run_totals = d.pop("payRunTotals", UNSET)
        pay_run_totals: Union[Unset, AuPayRunTotalResponseDictionaryStringAuPayRunTotalModel]
        if isinstance(_pay_run_totals, Unset):
            pay_run_totals = UNSET
        else:
            pay_run_totals = AuPayRunTotalResponseDictionaryStringAuPayRunTotalModel.from_dict(_pay_run_totals)

        au_pay_run_total_response = cls(
            pay_run_id=pay_run_id,
            pay_run_totals=pay_run_totals,
        )

        au_pay_run_total_response.additional_properties = d
        return au_pay_run_total_response

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
