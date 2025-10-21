from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.user_access_model_nullable_related_user_type import UserAccessModelNullableRelatedUserType
from ..types import UNSET, Unset

T = TypeVar("T", bound="UserAccessModel")


@_attrs_define
class UserAccessModel:
    """
    Attributes:
        access_type (Union[Unset, UserAccessModelNullableRelatedUserType]):
    """

    access_type: Union[Unset, UserAccessModelNullableRelatedUserType] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        access_type: Union[Unset, str] = UNSET
        if not isinstance(self.access_type, Unset):
            access_type = self.access_type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if access_type is not UNSET:
            field_dict["accessType"] = access_type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _access_type = d.pop("accessType", UNSET)
        access_type: Union[Unset, UserAccessModelNullableRelatedUserType]
        if isinstance(_access_type, Unset):
            access_type = UNSET
        else:
            access_type = UserAccessModelNullableRelatedUserType(_access_type)

        user_access_model = cls(
            access_type=access_type,
        )

        user_access_model.additional_properties = d
        return user_access_model

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
