from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="MetadataLite")


@_attrs_define
class MetadataLite:
    """
    Attributes:
        employee_id (Union[Unset, int]):
        business_id (Union[Unset, int]):
        brand_id (Union[Unset, int]):
        partner_id (Union[Unset, int]):
    """

    employee_id: Union[Unset, int] = UNSET
    business_id: Union[Unset, int] = UNSET
    brand_id: Union[Unset, int] = UNSET
    partner_id: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        employee_id = self.employee_id

        business_id = self.business_id

        brand_id = self.brand_id

        partner_id = self.partner_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if business_id is not UNSET:
            field_dict["businessId"] = business_id
        if brand_id is not UNSET:
            field_dict["brandId"] = brand_id
        if partner_id is not UNSET:
            field_dict["partnerId"] = partner_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        employee_id = d.pop("employeeId", UNSET)

        business_id = d.pop("businessId", UNSET)

        brand_id = d.pop("brandId", UNSET)

        partner_id = d.pop("partnerId", UNSET)

        metadata_lite = cls(
            employee_id=employee_id,
            business_id=business_id,
            brand_id=brand_id,
            partner_id=partner_id,
        )

        metadata_lite.additional_properties = d
        return metadata_lite

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
