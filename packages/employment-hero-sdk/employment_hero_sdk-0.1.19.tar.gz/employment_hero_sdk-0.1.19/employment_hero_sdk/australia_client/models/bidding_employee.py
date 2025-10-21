from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="BiddingEmployee")


@_attrs_define
class BiddingEmployee:
    """
    Attributes:
        id (Union[Unset, int]):
        employee_name (Union[Unset, str]):
        employee_phone_number (Union[Unset, str]):
    """

    id: Union[Unset, int] = UNSET
    employee_name: Union[Unset, str] = UNSET
    employee_phone_number: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        employee_name = self.employee_name

        employee_phone_number = self.employee_phone_number

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if employee_name is not UNSET:
            field_dict["employeeName"] = employee_name
        if employee_phone_number is not UNSET:
            field_dict["employeePhoneNumber"] = employee_phone_number

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        employee_name = d.pop("employeeName", UNSET)

        employee_phone_number = d.pop("employeePhoneNumber", UNSET)

        bidding_employee = cls(
            id=id,
            employee_name=employee_name,
            employee_phone_number=employee_phone_number,
        )

        bidding_employee.additional_properties = d
        return bidding_employee

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
