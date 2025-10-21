from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ChangeKioskPinModel")


@_attrs_define
class ChangeKioskPinModel:
    """
    Attributes:
        employee_id (Union[Unset, int]):
        old_pin (Union[Unset, str]):
        new_pin (Union[Unset, str]):
    """

    employee_id: Union[Unset, int] = UNSET
    old_pin: Union[Unset, str] = UNSET
    new_pin: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        employee_id = self.employee_id

        old_pin = self.old_pin

        new_pin = self.new_pin

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if old_pin is not UNSET:
            field_dict["oldPin"] = old_pin
        if new_pin is not UNSET:
            field_dict["newPin"] = new_pin

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        employee_id = d.pop("employeeId", UNSET)

        old_pin = d.pop("oldPin", UNSET)

        new_pin = d.pop("newPin", UNSET)

        change_kiosk_pin_model = cls(
            employee_id=employee_id,
            old_pin=old_pin,
            new_pin=new_pin,
        )

        change_kiosk_pin_model.additional_properties = d
        return change_kiosk_pin_model

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
