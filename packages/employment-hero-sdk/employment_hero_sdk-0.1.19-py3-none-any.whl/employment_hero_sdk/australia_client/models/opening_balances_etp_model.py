import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.opening_balances_etp_model_etp_type_enum import OpeningBalancesEtpModelEtpTypeEnum
from ..types import UNSET, Unset

T = TypeVar("T", bound="OpeningBalancesEtpModel")


@_attrs_define
class OpeningBalancesEtpModel:
    """
    Attributes:
        id (Union[Unset, int]):
        etp_type (Union[Unset, OpeningBalancesEtpModelEtpTypeEnum]):
        tax_free_component (Union[Unset, float]):
        taxable_component (Union[Unset, float]):
        tax_withheld (Union[Unset, float]):
        is_amended (Union[Unset, bool]):
        payment_date (Union[Unset, datetime.datetime]):
        generate_payment_summary (Union[Unset, bool]):
    """

    id: Union[Unset, int] = UNSET
    etp_type: Union[Unset, OpeningBalancesEtpModelEtpTypeEnum] = UNSET
    tax_free_component: Union[Unset, float] = UNSET
    taxable_component: Union[Unset, float] = UNSET
    tax_withheld: Union[Unset, float] = UNSET
    is_amended: Union[Unset, bool] = UNSET
    payment_date: Union[Unset, datetime.datetime] = UNSET
    generate_payment_summary: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        etp_type: Union[Unset, str] = UNSET
        if not isinstance(self.etp_type, Unset):
            etp_type = self.etp_type.value

        tax_free_component = self.tax_free_component

        taxable_component = self.taxable_component

        tax_withheld = self.tax_withheld

        is_amended = self.is_amended

        payment_date: Union[Unset, str] = UNSET
        if not isinstance(self.payment_date, Unset):
            payment_date = self.payment_date.isoformat()

        generate_payment_summary = self.generate_payment_summary

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if etp_type is not UNSET:
            field_dict["etpType"] = etp_type
        if tax_free_component is not UNSET:
            field_dict["taxFreeComponent"] = tax_free_component
        if taxable_component is not UNSET:
            field_dict["taxableComponent"] = taxable_component
        if tax_withheld is not UNSET:
            field_dict["taxWithheld"] = tax_withheld
        if is_amended is not UNSET:
            field_dict["isAmended"] = is_amended
        if payment_date is not UNSET:
            field_dict["paymentDate"] = payment_date
        if generate_payment_summary is not UNSET:
            field_dict["generatePaymentSummary"] = generate_payment_summary

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        _etp_type = d.pop("etpType", UNSET)
        etp_type: Union[Unset, OpeningBalancesEtpModelEtpTypeEnum]
        if isinstance(_etp_type, Unset):
            etp_type = UNSET
        else:
            etp_type = OpeningBalancesEtpModelEtpTypeEnum(_etp_type)

        tax_free_component = d.pop("taxFreeComponent", UNSET)

        taxable_component = d.pop("taxableComponent", UNSET)

        tax_withheld = d.pop("taxWithheld", UNSET)

        is_amended = d.pop("isAmended", UNSET)

        _payment_date = d.pop("paymentDate", UNSET)
        payment_date: Union[Unset, datetime.datetime]
        if isinstance(_payment_date, Unset):
            payment_date = UNSET
        else:
            payment_date = isoparse(_payment_date)

        generate_payment_summary = d.pop("generatePaymentSummary", UNSET)

        opening_balances_etp_model = cls(
            id=id,
            etp_type=etp_type,
            tax_free_component=tax_free_component,
            taxable_component=taxable_component,
            tax_withheld=tax_withheld,
            is_amended=is_amended,
            payment_date=payment_date,
            generate_payment_summary=generate_payment_summary,
        )

        opening_balances_etp_model.additional_properties = d
        return opening_balances_etp_model

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
