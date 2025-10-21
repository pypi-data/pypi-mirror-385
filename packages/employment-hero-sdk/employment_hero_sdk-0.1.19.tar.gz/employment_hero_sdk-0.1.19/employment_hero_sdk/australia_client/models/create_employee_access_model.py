from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateEmployeeAccessModel")


@_attrs_define
class CreateEmployeeAccessModel:
    """
    Attributes:
        suppress_notification_emails (Union[Unset, bool]):
        name (Union[Unset, str]):
        email (Union[Unset, str]):
    """

    suppress_notification_emails: Union[Unset, bool] = UNSET
    name: Union[Unset, str] = UNSET
    email: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        suppress_notification_emails = self.suppress_notification_emails

        name = self.name

        email = self.email

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if suppress_notification_emails is not UNSET:
            field_dict["suppressNotificationEmails"] = suppress_notification_emails
        if name is not UNSET:
            field_dict["name"] = name
        if email is not UNSET:
            field_dict["email"] = email

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        suppress_notification_emails = d.pop("suppressNotificationEmails", UNSET)

        name = d.pop("name", UNSET)

        email = d.pop("email", UNSET)

        create_employee_access_model = cls(
            suppress_notification_emails=suppress_notification_emails,
            name=name,
            email=email,
        )

        create_employee_access_model.additional_properties = d
        return create_employee_access_model

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
