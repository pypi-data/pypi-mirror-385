from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="EssPaymentSummaryModel")


@_attrs_define
class EssPaymentSummaryModel:
    """
    Attributes:
        id (Union[Unset, int]):
        period (Union[Unset, str]):
        is_etp (Union[Unset, bool]):
        etp_code (Union[Unset, str]):
    """

    id: Union[Unset, int] = UNSET
    period: Union[Unset, str] = UNSET
    is_etp: Union[Unset, bool] = UNSET
    etp_code: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        period = self.period

        is_etp = self.is_etp

        etp_code = self.etp_code

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if period is not UNSET:
            field_dict["period"] = period
        if is_etp is not UNSET:
            field_dict["isEtp"] = is_etp
        if etp_code is not UNSET:
            field_dict["etpCode"] = etp_code

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        period = d.pop("period", UNSET)

        is_etp = d.pop("isEtp", UNSET)

        etp_code = d.pop("etpCode", UNSET)

        ess_payment_summary_model = cls(
            id=id,
            period=period,
            is_etp=is_etp,
            etp_code=etp_code,
        )

        ess_payment_summary_model.additional_properties = d
        return ess_payment_summary_model

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
