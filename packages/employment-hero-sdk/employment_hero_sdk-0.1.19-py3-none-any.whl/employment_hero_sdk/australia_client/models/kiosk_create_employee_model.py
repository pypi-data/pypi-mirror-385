from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="KioskCreateEmployeeModel")


@_attrs_define
class KioskCreateEmployeeModel:
    """
    Attributes:
        first_name (Union[Unset, str]):
        surname (Union[Unset, str]):
        email (Union[Unset, str]):
        mobile_number (Union[Unset, str]):
        pin (Union[Unset, str]):
    """

    first_name: Union[Unset, str] = UNSET
    surname: Union[Unset, str] = UNSET
    email: Union[Unset, str] = UNSET
    mobile_number: Union[Unset, str] = UNSET
    pin: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        first_name = self.first_name

        surname = self.surname

        email = self.email

        mobile_number = self.mobile_number

        pin = self.pin

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if first_name is not UNSET:
            field_dict["firstName"] = first_name
        if surname is not UNSET:
            field_dict["surname"] = surname
        if email is not UNSET:
            field_dict["email"] = email
        if mobile_number is not UNSET:
            field_dict["mobileNumber"] = mobile_number
        if pin is not UNSET:
            field_dict["pin"] = pin

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        first_name = d.pop("firstName", UNSET)

        surname = d.pop("surname", UNSET)

        email = d.pop("email", UNSET)

        mobile_number = d.pop("mobileNumber", UNSET)

        pin = d.pop("pin", UNSET)

        kiosk_create_employee_model = cls(
            first_name=first_name,
            surname=surname,
            email=email,
            mobile_number=mobile_number,
            pin=pin,
        )

        kiosk_create_employee_model.additional_properties = d
        return kiosk_create_employee_model

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
