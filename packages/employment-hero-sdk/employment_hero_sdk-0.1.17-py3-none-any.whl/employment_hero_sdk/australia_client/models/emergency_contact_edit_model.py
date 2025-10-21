from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="EmergencyContactEditModel")


@_attrs_define
class EmergencyContactEditModel:
    """
    Attributes:
        id (Union[Unset, int]):
        name (Union[Unset, str]):
        relationship (Union[Unset, str]):
        address (Union[Unset, str]):
        contact_number (Union[Unset, str]):
        alternate_contact_number (Union[Unset, str]):
    """

    id: Union[Unset, int] = UNSET
    name: Union[Unset, str] = UNSET
    relationship: Union[Unset, str] = UNSET
    address: Union[Unset, str] = UNSET
    contact_number: Union[Unset, str] = UNSET
    alternate_contact_number: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        name = self.name

        relationship = self.relationship

        address = self.address

        contact_number = self.contact_number

        alternate_contact_number = self.alternate_contact_number

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if relationship is not UNSET:
            field_dict["relationship"] = relationship
        if address is not UNSET:
            field_dict["address"] = address
        if contact_number is not UNSET:
            field_dict["contactNumber"] = contact_number
        if alternate_contact_number is not UNSET:
            field_dict["alternateContactNumber"] = alternate_contact_number

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        relationship = d.pop("relationship", UNSET)

        address = d.pop("address", UNSET)

        contact_number = d.pop("contactNumber", UNSET)

        alternate_contact_number = d.pop("alternateContactNumber", UNSET)

        emergency_contact_edit_model = cls(
            id=id,
            name=name,
            relationship=relationship,
            address=address,
            contact_number=contact_number,
            alternate_contact_number=alternate_contact_number,
        )

        emergency_contact_edit_model.additional_properties = d
        return emergency_contact_edit_model

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
