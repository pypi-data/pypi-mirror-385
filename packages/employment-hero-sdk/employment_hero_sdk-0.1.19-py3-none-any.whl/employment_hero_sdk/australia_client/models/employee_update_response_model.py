from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="EmployeeUpdateResponseModel")


@_attrs_define
class EmployeeUpdateResponseModel:
    """
    Attributes:
        id (Union[Unset, int]):
        status (Union[Unset, str]):
        detailed_status (Union[Unset, str]):
    """

    id: Union[Unset, int] = UNSET
    status: Union[Unset, str] = UNSET
    detailed_status: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        status = self.status

        detailed_status = self.detailed_status

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if status is not UNSET:
            field_dict["status"] = status
        if detailed_status is not UNSET:
            field_dict["detailedStatus"] = detailed_status

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        status = d.pop("status", UNSET)

        detailed_status = d.pop("detailedStatus", UNSET)

        employee_update_response_model = cls(
            id=id,
            status=status,
            detailed_status=detailed_status,
        )

        employee_update_response_model.additional_properties = d
        return employee_update_response_model

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
