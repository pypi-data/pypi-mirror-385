from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="RateOverride")


@_attrs_define
class RateOverride:
    """
    Attributes:
        pay_category_id (Union[Unset, int]):
        rate (Union[Unset, float]):
        use_rate_as_is (Union[Unset, bool]): Nullable</p><p><i>Note:</i>If set to "true", the system assumes the
            <i>Rate</i> value is inclusive of rate loading and penalty loading.
    """

    pay_category_id: Union[Unset, int] = UNSET
    rate: Union[Unset, float] = UNSET
    use_rate_as_is: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        pay_category_id = self.pay_category_id

        rate = self.rate

        use_rate_as_is = self.use_rate_as_is

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if pay_category_id is not UNSET:
            field_dict["payCategoryId"] = pay_category_id
        if rate is not UNSET:
            field_dict["rate"] = rate
        if use_rate_as_is is not UNSET:
            field_dict["useRateAsIs"] = use_rate_as_is

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        pay_category_id = d.pop("payCategoryId", UNSET)

        rate = d.pop("rate", UNSET)

        use_rate_as_is = d.pop("useRateAsIs", UNSET)

        rate_override = cls(
            pay_category_id=pay_category_id,
            rate=rate,
            use_rate_as_is=use_rate_as_is,
        )

        rate_override.additional_properties = d
        return rate_override

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
