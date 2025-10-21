from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.employment_termination_payment_etp_type_enum import EmploymentTerminationPaymentEtpTypeEnum
from ..types import UNSET, Unset

T = TypeVar("T", bound="EmploymentTerminationPayment")


@_attrs_define
class EmploymentTerminationPayment:
    """
    Attributes:
        tax_free_component (Union[Unset, float]):
        taxable_amount (Union[Unset, float]):
        attract_super (Union[Unset, bool]):
        comments (Union[Unset, str]):
        is_genuine_redundancy (Union[Unset, bool]):
        etp_type (Union[Unset, EmploymentTerminationPaymentEtpTypeEnum]):
    """

    tax_free_component: Union[Unset, float] = UNSET
    taxable_amount: Union[Unset, float] = UNSET
    attract_super: Union[Unset, bool] = UNSET
    comments: Union[Unset, str] = UNSET
    is_genuine_redundancy: Union[Unset, bool] = UNSET
    etp_type: Union[Unset, EmploymentTerminationPaymentEtpTypeEnum] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        tax_free_component = self.tax_free_component

        taxable_amount = self.taxable_amount

        attract_super = self.attract_super

        comments = self.comments

        is_genuine_redundancy = self.is_genuine_redundancy

        etp_type: Union[Unset, str] = UNSET
        if not isinstance(self.etp_type, Unset):
            etp_type = self.etp_type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if tax_free_component is not UNSET:
            field_dict["taxFreeComponent"] = tax_free_component
        if taxable_amount is not UNSET:
            field_dict["taxableAmount"] = taxable_amount
        if attract_super is not UNSET:
            field_dict["attractSuper"] = attract_super
        if comments is not UNSET:
            field_dict["comments"] = comments
        if is_genuine_redundancy is not UNSET:
            field_dict["isGenuineRedundancy"] = is_genuine_redundancy
        if etp_type is not UNSET:
            field_dict["etpType"] = etp_type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        tax_free_component = d.pop("taxFreeComponent", UNSET)

        taxable_amount = d.pop("taxableAmount", UNSET)

        attract_super = d.pop("attractSuper", UNSET)

        comments = d.pop("comments", UNSET)

        is_genuine_redundancy = d.pop("isGenuineRedundancy", UNSET)

        _etp_type = d.pop("etpType", UNSET)
        etp_type: Union[Unset, EmploymentTerminationPaymentEtpTypeEnum]
        if isinstance(_etp_type, Unset):
            etp_type = UNSET
        else:
            etp_type = EmploymentTerminationPaymentEtpTypeEnum(_etp_type)

        employment_termination_payment = cls(
            tax_free_component=tax_free_component,
            taxable_amount=taxable_amount,
            attract_super=attract_super,
            comments=comments,
            is_genuine_redundancy=is_genuine_redundancy,
            etp_type=etp_type,
        )

        employment_termination_payment.additional_properties = d
        return employment_termination_payment

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
