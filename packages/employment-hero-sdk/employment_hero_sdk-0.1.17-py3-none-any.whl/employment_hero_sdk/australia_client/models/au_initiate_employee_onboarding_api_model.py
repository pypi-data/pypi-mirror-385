from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AuInitiateEmployeeOnboardingApiModel")


@_attrs_define
class AuInitiateEmployeeOnboardingApiModel:
    """
    Attributes:
        employing_entity_id (Union[Unset, int]):
        id (Union[Unset, int]):
        title (Union[Unset, int]):
        first_name (Union[Unset, str]):
        surname (Union[Unset, str]):
        email (Union[Unset, str]):
        mobile (Union[Unset, str]):
        qualifications_required (Union[Unset, bool]):
        emergency_contact_details_required (Union[Unset, bool]):
    """

    employing_entity_id: Union[Unset, int] = UNSET
    id: Union[Unset, int] = UNSET
    title: Union[Unset, int] = UNSET
    first_name: Union[Unset, str] = UNSET
    surname: Union[Unset, str] = UNSET
    email: Union[Unset, str] = UNSET
    mobile: Union[Unset, str] = UNSET
    qualifications_required: Union[Unset, bool] = UNSET
    emergency_contact_details_required: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        employing_entity_id = self.employing_entity_id

        id = self.id

        title = self.title

        first_name = self.first_name

        surname = self.surname

        email = self.email

        mobile = self.mobile

        qualifications_required = self.qualifications_required

        emergency_contact_details_required = self.emergency_contact_details_required

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if employing_entity_id is not UNSET:
            field_dict["employingEntityId"] = employing_entity_id
        if id is not UNSET:
            field_dict["id"] = id
        if title is not UNSET:
            field_dict["title"] = title
        if first_name is not UNSET:
            field_dict["firstName"] = first_name
        if surname is not UNSET:
            field_dict["surname"] = surname
        if email is not UNSET:
            field_dict["email"] = email
        if mobile is not UNSET:
            field_dict["mobile"] = mobile
        if qualifications_required is not UNSET:
            field_dict["qualificationsRequired"] = qualifications_required
        if emergency_contact_details_required is not UNSET:
            field_dict["emergencyContactDetailsRequired"] = emergency_contact_details_required

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        employing_entity_id = d.pop("employingEntityId", UNSET)

        id = d.pop("id", UNSET)

        title = d.pop("title", UNSET)

        first_name = d.pop("firstName", UNSET)

        surname = d.pop("surname", UNSET)

        email = d.pop("email", UNSET)

        mobile = d.pop("mobile", UNSET)

        qualifications_required = d.pop("qualificationsRequired", UNSET)

        emergency_contact_details_required = d.pop("emergencyContactDetailsRequired", UNSET)

        au_initiate_employee_onboarding_api_model = cls(
            employing_entity_id=employing_entity_id,
            id=id,
            title=title,
            first_name=first_name,
            surname=surname,
            email=email,
            mobile=mobile,
            qualifications_required=qualifications_required,
            emergency_contact_details_required=emergency_contact_details_required,
        )

        au_initiate_employee_onboarding_api_model.additional_properties = d
        return au_initiate_employee_onboarding_api_model

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
