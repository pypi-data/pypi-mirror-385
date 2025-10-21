from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.emergency_contact_edit_model import EmergencyContactEditModel


T = TypeVar("T", bound="EmployeeEmergencyContactsEditModel")


@_attrs_define
class EmployeeEmergencyContactsEditModel:
    """
    Attributes:
        primary_emergency_contact (Union[Unset, EmergencyContactEditModel]):
        secondary_emergency_contact (Union[Unset, EmergencyContactEditModel]):
        can_edit (Union[Unset, bool]):
    """

    primary_emergency_contact: Union[Unset, "EmergencyContactEditModel"] = UNSET
    secondary_emergency_contact: Union[Unset, "EmergencyContactEditModel"] = UNSET
    can_edit: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        primary_emergency_contact: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.primary_emergency_contact, Unset):
            primary_emergency_contact = self.primary_emergency_contact.to_dict()

        secondary_emergency_contact: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.secondary_emergency_contact, Unset):
            secondary_emergency_contact = self.secondary_emergency_contact.to_dict()

        can_edit = self.can_edit

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if primary_emergency_contact is not UNSET:
            field_dict["primaryEmergencyContact"] = primary_emergency_contact
        if secondary_emergency_contact is not UNSET:
            field_dict["secondaryEmergencyContact"] = secondary_emergency_contact
        if can_edit is not UNSET:
            field_dict["canEdit"] = can_edit

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.emergency_contact_edit_model import EmergencyContactEditModel

        d = src_dict.copy()
        _primary_emergency_contact = d.pop("primaryEmergencyContact", UNSET)
        primary_emergency_contact: Union[Unset, EmergencyContactEditModel]
        if isinstance(_primary_emergency_contact, Unset):
            primary_emergency_contact = UNSET
        else:
            primary_emergency_contact = EmergencyContactEditModel.from_dict(_primary_emergency_contact)

        _secondary_emergency_contact = d.pop("secondaryEmergencyContact", UNSET)
        secondary_emergency_contact: Union[Unset, EmergencyContactEditModel]
        if isinstance(_secondary_emergency_contact, Unset):
            secondary_emergency_contact = UNSET
        else:
            secondary_emergency_contact = EmergencyContactEditModel.from_dict(_secondary_emergency_contact)

        can_edit = d.pop("canEdit", UNSET)

        employee_emergency_contacts_edit_model = cls(
            primary_emergency_contact=primary_emergency_contact,
            secondary_emergency_contact=secondary_emergency_contact,
            can_edit=can_edit,
        )

        employee_emergency_contacts_edit_model.additional_properties = d
        return employee_emergency_contacts_edit_model

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
