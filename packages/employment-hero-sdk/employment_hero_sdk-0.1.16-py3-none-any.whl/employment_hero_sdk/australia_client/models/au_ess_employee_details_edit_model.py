import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.au_address_model import AuAddressModel


T = TypeVar("T", bound="AuEssEmployeeDetailsEditModel")


@_attrs_define
class AuEssEmployeeDetailsEditModel:
    """
    Attributes:
        residential_address (Union[Unset, AuAddressModel]):
        postal_address (Union[Unset, AuAddressModel]):
        id (Union[Unset, int]):
        title_id (Union[Unset, int]):
        first_name (Union[Unset, str]):
        other_name (Union[Unset, str]):
        middle_name (Union[Unset, str]):
        surname (Union[Unset, str]):
        previous_surname (Union[Unset, str]):
        date_of_birth (Union[Unset, datetime.datetime]):
        gender (Union[Unset, str]):
        email (Union[Unset, str]):
        home_phone (Union[Unset, str]):
        work_phone (Union[Unset, str]):
        mobile_phone (Union[Unset, str]):
        is_postal_address_same_as_residential (Union[Unset, bool]):
    """

    residential_address: Union[Unset, "AuAddressModel"] = UNSET
    postal_address: Union[Unset, "AuAddressModel"] = UNSET
    id: Union[Unset, int] = UNSET
    title_id: Union[Unset, int] = UNSET
    first_name: Union[Unset, str] = UNSET
    other_name: Union[Unset, str] = UNSET
    middle_name: Union[Unset, str] = UNSET
    surname: Union[Unset, str] = UNSET
    previous_surname: Union[Unset, str] = UNSET
    date_of_birth: Union[Unset, datetime.datetime] = UNSET
    gender: Union[Unset, str] = UNSET
    email: Union[Unset, str] = UNSET
    home_phone: Union[Unset, str] = UNSET
    work_phone: Union[Unset, str] = UNSET
    mobile_phone: Union[Unset, str] = UNSET
    is_postal_address_same_as_residential: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        residential_address: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.residential_address, Unset):
            residential_address = self.residential_address.to_dict()

        postal_address: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.postal_address, Unset):
            postal_address = self.postal_address.to_dict()

        id = self.id

        title_id = self.title_id

        first_name = self.first_name

        other_name = self.other_name

        middle_name = self.middle_name

        surname = self.surname

        previous_surname = self.previous_surname

        date_of_birth: Union[Unset, str] = UNSET
        if not isinstance(self.date_of_birth, Unset):
            date_of_birth = self.date_of_birth.isoformat()

        gender = self.gender

        email = self.email

        home_phone = self.home_phone

        work_phone = self.work_phone

        mobile_phone = self.mobile_phone

        is_postal_address_same_as_residential = self.is_postal_address_same_as_residential

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if residential_address is not UNSET:
            field_dict["residentialAddress"] = residential_address
        if postal_address is not UNSET:
            field_dict["postalAddress"] = postal_address
        if id is not UNSET:
            field_dict["id"] = id
        if title_id is not UNSET:
            field_dict["titleId"] = title_id
        if first_name is not UNSET:
            field_dict["firstName"] = first_name
        if other_name is not UNSET:
            field_dict["otherName"] = other_name
        if middle_name is not UNSET:
            field_dict["middleName"] = middle_name
        if surname is not UNSET:
            field_dict["surname"] = surname
        if previous_surname is not UNSET:
            field_dict["previousSurname"] = previous_surname
        if date_of_birth is not UNSET:
            field_dict["dateOfBirth"] = date_of_birth
        if gender is not UNSET:
            field_dict["gender"] = gender
        if email is not UNSET:
            field_dict["email"] = email
        if home_phone is not UNSET:
            field_dict["homePhone"] = home_phone
        if work_phone is not UNSET:
            field_dict["workPhone"] = work_phone
        if mobile_phone is not UNSET:
            field_dict["mobilePhone"] = mobile_phone
        if is_postal_address_same_as_residential is not UNSET:
            field_dict["isPostalAddressSameAsResidential"] = is_postal_address_same_as_residential

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.au_address_model import AuAddressModel

        d = src_dict.copy()
        _residential_address = d.pop("residentialAddress", UNSET)
        residential_address: Union[Unset, AuAddressModel]
        if isinstance(_residential_address, Unset):
            residential_address = UNSET
        else:
            residential_address = AuAddressModel.from_dict(_residential_address)

        _postal_address = d.pop("postalAddress", UNSET)
        postal_address: Union[Unset, AuAddressModel]
        if isinstance(_postal_address, Unset):
            postal_address = UNSET
        else:
            postal_address = AuAddressModel.from_dict(_postal_address)

        id = d.pop("id", UNSET)

        title_id = d.pop("titleId", UNSET)

        first_name = d.pop("firstName", UNSET)

        other_name = d.pop("otherName", UNSET)

        middle_name = d.pop("middleName", UNSET)

        surname = d.pop("surname", UNSET)

        previous_surname = d.pop("previousSurname", UNSET)

        _date_of_birth = d.pop("dateOfBirth", UNSET)
        date_of_birth: Union[Unset, datetime.datetime]
        if isinstance(_date_of_birth, Unset):
            date_of_birth = UNSET
        else:
            date_of_birth = isoparse(_date_of_birth)

        gender = d.pop("gender", UNSET)

        email = d.pop("email", UNSET)

        home_phone = d.pop("homePhone", UNSET)

        work_phone = d.pop("workPhone", UNSET)

        mobile_phone = d.pop("mobilePhone", UNSET)

        is_postal_address_same_as_residential = d.pop("isPostalAddressSameAsResidential", UNSET)

        au_ess_employee_details_edit_model = cls(
            residential_address=residential_address,
            postal_address=postal_address,
            id=id,
            title_id=title_id,
            first_name=first_name,
            other_name=other_name,
            middle_name=middle_name,
            surname=surname,
            previous_surname=previous_surname,
            date_of_birth=date_of_birth,
            gender=gender,
            email=email,
            home_phone=home_phone,
            work_phone=work_phone,
            mobile_phone=mobile_phone,
            is_postal_address_same_as_residential=is_postal_address_same_as_residential,
        )

        au_ess_employee_details_edit_model.additional_properties = d
        return au_ess_employee_details_edit_model

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
