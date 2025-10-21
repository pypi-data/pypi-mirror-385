from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.pay_rate_template_model import PayRateTemplateModel


T = TypeVar("T", bound="EmploymentAgreementPayRateTemplateModel")


@_attrs_define
class EmploymentAgreementPayRateTemplateModel:
    """
    Attributes:
        pay_rate_template_id (Union[Unset, int]):
        pay_rate_template (Union[Unset, PayRateTemplateModel]):
        min_age (Union[Unset, int]):
        max_age (Union[Unset, int]):
        min_anniversary_months (Union[Unset, int]):
        max_anniversary_months (Union[Unset, int]):
    """

    pay_rate_template_id: Union[Unset, int] = UNSET
    pay_rate_template: Union[Unset, "PayRateTemplateModel"] = UNSET
    min_age: Union[Unset, int] = UNSET
    max_age: Union[Unset, int] = UNSET
    min_anniversary_months: Union[Unset, int] = UNSET
    max_anniversary_months: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        pay_rate_template_id = self.pay_rate_template_id

        pay_rate_template: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.pay_rate_template, Unset):
            pay_rate_template = self.pay_rate_template.to_dict()

        min_age = self.min_age

        max_age = self.max_age

        min_anniversary_months = self.min_anniversary_months

        max_anniversary_months = self.max_anniversary_months

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if pay_rate_template_id is not UNSET:
            field_dict["payRateTemplateId"] = pay_rate_template_id
        if pay_rate_template is not UNSET:
            field_dict["payRateTemplate"] = pay_rate_template
        if min_age is not UNSET:
            field_dict["minAge"] = min_age
        if max_age is not UNSET:
            field_dict["maxAge"] = max_age
        if min_anniversary_months is not UNSET:
            field_dict["minAnniversaryMonths"] = min_anniversary_months
        if max_anniversary_months is not UNSET:
            field_dict["maxAnniversaryMonths"] = max_anniversary_months

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.pay_rate_template_model import PayRateTemplateModel

        d = src_dict.copy()
        pay_rate_template_id = d.pop("payRateTemplateId", UNSET)

        _pay_rate_template = d.pop("payRateTemplate", UNSET)
        pay_rate_template: Union[Unset, PayRateTemplateModel]
        if isinstance(_pay_rate_template, Unset):
            pay_rate_template = UNSET
        else:
            pay_rate_template = PayRateTemplateModel.from_dict(_pay_rate_template)

        min_age = d.pop("minAge", UNSET)

        max_age = d.pop("maxAge", UNSET)

        min_anniversary_months = d.pop("minAnniversaryMonths", UNSET)

        max_anniversary_months = d.pop("maxAnniversaryMonths", UNSET)

        employment_agreement_pay_rate_template_model = cls(
            pay_rate_template_id=pay_rate_template_id,
            pay_rate_template=pay_rate_template,
            min_age=min_age,
            max_age=max_age,
            min_anniversary_months=min_anniversary_months,
            max_anniversary_months=max_anniversary_months,
        )

        employment_agreement_pay_rate_template_model.additional_properties = d
        return employment_agreement_pay_rate_template_model

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
