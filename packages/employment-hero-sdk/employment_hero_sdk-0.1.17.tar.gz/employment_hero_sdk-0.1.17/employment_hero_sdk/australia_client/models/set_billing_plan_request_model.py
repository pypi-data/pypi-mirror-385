from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SetBillingPlanRequestModel")


@_attrs_define
class SetBillingPlanRequestModel:
    """
    Attributes:
        billing_plan_id (Union[Unset, int]):
    """

    billing_plan_id: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        billing_plan_id = self.billing_plan_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if billing_plan_id is not UNSET:
            field_dict["billingPlanId"] = billing_plan_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        billing_plan_id = d.pop("billingPlanId", UNSET)

        set_billing_plan_request_model = cls(
            billing_plan_id=billing_plan_id,
        )

        set_billing_plan_request_model.additional_properties = d
        return set_billing_plan_request_model

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
