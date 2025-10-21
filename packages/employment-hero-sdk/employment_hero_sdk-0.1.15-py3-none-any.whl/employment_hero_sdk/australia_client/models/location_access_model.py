from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.location_access_model_location_restriction_filter_type_enum import (
    LocationAccessModelLocationRestrictionFilterTypeEnum,
)
from ..models.location_access_model_user_permission import LocationAccessModelUserPermission
from ..types import UNSET, Unset

T = TypeVar("T", bound="LocationAccessModel")


@_attrs_define
class LocationAccessModel:
    """
    Attributes:
        filter_type (Union[Unset, LocationAccessModelLocationRestrictionFilterTypeEnum]):
        location_ids (Union[Unset, List[int]]):
        permissions (Union[Unset, LocationAccessModelUserPermission]):
    """

    filter_type: Union[Unset, LocationAccessModelLocationRestrictionFilterTypeEnum] = UNSET
    location_ids: Union[Unset, List[int]] = UNSET
    permissions: Union[Unset, LocationAccessModelUserPermission] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        filter_type: Union[Unset, str] = UNSET
        if not isinstance(self.filter_type, Unset):
            filter_type = self.filter_type.value

        location_ids: Union[Unset, List[int]] = UNSET
        if not isinstance(self.location_ids, Unset):
            location_ids = self.location_ids

        permissions: Union[Unset, str] = UNSET
        if not isinstance(self.permissions, Unset):
            permissions = self.permissions.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if filter_type is not UNSET:
            field_dict["filterType"] = filter_type
        if location_ids is not UNSET:
            field_dict["locationIds"] = location_ids
        if permissions is not UNSET:
            field_dict["permissions"] = permissions

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _filter_type = d.pop("filterType", UNSET)
        filter_type: Union[Unset, LocationAccessModelLocationRestrictionFilterTypeEnum]
        if isinstance(_filter_type, Unset):
            filter_type = UNSET
        else:
            filter_type = LocationAccessModelLocationRestrictionFilterTypeEnum(_filter_type)

        location_ids = cast(List[int], d.pop("locationIds", UNSET))

        _permissions = d.pop("permissions", UNSET)
        permissions: Union[Unset, LocationAccessModelUserPermission]
        if isinstance(_permissions, Unset):
            permissions = UNSET
        else:
            permissions = LocationAccessModelUserPermission(_permissions)

        location_access_model = cls(
            filter_type=filter_type,
            location_ids=location_ids,
            permissions=permissions,
        )

        location_access_model.additional_properties = d
        return location_access_model

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
