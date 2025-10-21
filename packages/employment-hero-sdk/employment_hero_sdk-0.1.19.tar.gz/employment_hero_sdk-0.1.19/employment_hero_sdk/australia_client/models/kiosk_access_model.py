from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.kiosk_access_model_kiosk_access_type import KioskAccessModelKioskAccessType
from ..models.kiosk_access_model_user_permission import KioskAccessModelUserPermission
from ..types import UNSET, Unset

T = TypeVar("T", bound="KioskAccessModel")


@_attrs_define
class KioskAccessModel:
    """
    Attributes:
        kiosks (Union[Unset, List[int]]):
        access_type (Union[Unset, KioskAccessModelKioskAccessType]):
        permissions (Union[Unset, KioskAccessModelUserPermission]):
    """

    kiosks: Union[Unset, List[int]] = UNSET
    access_type: Union[Unset, KioskAccessModelKioskAccessType] = UNSET
    permissions: Union[Unset, KioskAccessModelUserPermission] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        kiosks: Union[Unset, List[int]] = UNSET
        if not isinstance(self.kiosks, Unset):
            kiosks = self.kiosks

        access_type: Union[Unset, str] = UNSET
        if not isinstance(self.access_type, Unset):
            access_type = self.access_type.value

        permissions: Union[Unset, str] = UNSET
        if not isinstance(self.permissions, Unset):
            permissions = self.permissions.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if kiosks is not UNSET:
            field_dict["kiosks"] = kiosks
        if access_type is not UNSET:
            field_dict["accessType"] = access_type
        if permissions is not UNSET:
            field_dict["permissions"] = permissions

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        kiosks = cast(List[int], d.pop("kiosks", UNSET))

        _access_type = d.pop("accessType", UNSET)
        access_type: Union[Unset, KioskAccessModelKioskAccessType]
        if isinstance(_access_type, Unset):
            access_type = UNSET
        else:
            access_type = KioskAccessModelKioskAccessType(_access_type)

        _permissions = d.pop("permissions", UNSET)
        permissions: Union[Unset, KioskAccessModelUserPermission]
        if isinstance(_permissions, Unset):
            permissions = UNSET
        else:
            permissions = KioskAccessModelUserPermission(_permissions)

        kiosk_access_model = cls(
            kiosks=kiosks,
            access_type=access_type,
            permissions=permissions,
        )

        kiosk_access_model.additional_properties = d
        return kiosk_access_model

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
