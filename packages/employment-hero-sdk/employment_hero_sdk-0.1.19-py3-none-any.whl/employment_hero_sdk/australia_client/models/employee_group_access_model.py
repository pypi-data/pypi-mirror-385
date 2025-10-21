from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.employee_group_access_model_user_permission import EmployeeGroupAccessModelUserPermission
from ..types import UNSET, Unset

T = TypeVar("T", bound="EmployeeGroupAccessModel")


@_attrs_define
class EmployeeGroupAccessModel:
    """
    Attributes:
        employee_group_id (Union[Unset, int]):
        permissions (Union[Unset, EmployeeGroupAccessModelUserPermission]):
    """

    employee_group_id: Union[Unset, int] = UNSET
    permissions: Union[Unset, EmployeeGroupAccessModelUserPermission] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        employee_group_id = self.employee_group_id

        permissions: Union[Unset, str] = UNSET
        if not isinstance(self.permissions, Unset):
            permissions = self.permissions.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if employee_group_id is not UNSET:
            field_dict["employeeGroupId"] = employee_group_id
        if permissions is not UNSET:
            field_dict["permissions"] = permissions

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        employee_group_id = d.pop("employeeGroupId", UNSET)

        _permissions = d.pop("permissions", UNSET)
        permissions: Union[Unset, EmployeeGroupAccessModelUserPermission]
        if isinstance(_permissions, Unset):
            permissions = UNSET
        else:
            permissions = EmployeeGroupAccessModelUserPermission(_permissions)

        employee_group_access_model = cls(
            employee_group_id=employee_group_id,
            permissions=permissions,
        )

        employee_group_access_model.additional_properties = d
        return employee_group_access_model

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
