from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="EmployeeDetailsFields")


@_attrs_define
class EmployeeDetailsFields:
    """
    Attributes:
        show_start_date (Union[Unset, bool]):
        show_title (Union[Unset, bool]):
        show_preferred_name (Union[Unset, bool]):
        show_previous_surname (Union[Unset, bool]):
        show_gender (Union[Unset, bool]):
        show_date_of_birth (Union[Unset, bool]):
        show_anniversary_date (Union[Unset, bool]):
        show_postal_address (Union[Unset, bool]):
        is_name_mandatory (Union[Unset, bool]):
        is_address_mandatory (Union[Unset, bool]):
    """

    show_start_date: Union[Unset, bool] = UNSET
    show_title: Union[Unset, bool] = UNSET
    show_preferred_name: Union[Unset, bool] = UNSET
    show_previous_surname: Union[Unset, bool] = UNSET
    show_gender: Union[Unset, bool] = UNSET
    show_date_of_birth: Union[Unset, bool] = UNSET
    show_anniversary_date: Union[Unset, bool] = UNSET
    show_postal_address: Union[Unset, bool] = UNSET
    is_name_mandatory: Union[Unset, bool] = UNSET
    is_address_mandatory: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        show_start_date = self.show_start_date

        show_title = self.show_title

        show_preferred_name = self.show_preferred_name

        show_previous_surname = self.show_previous_surname

        show_gender = self.show_gender

        show_date_of_birth = self.show_date_of_birth

        show_anniversary_date = self.show_anniversary_date

        show_postal_address = self.show_postal_address

        is_name_mandatory = self.is_name_mandatory

        is_address_mandatory = self.is_address_mandatory

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if show_start_date is not UNSET:
            field_dict["showStartDate"] = show_start_date
        if show_title is not UNSET:
            field_dict["showTitle"] = show_title
        if show_preferred_name is not UNSET:
            field_dict["showPreferredName"] = show_preferred_name
        if show_previous_surname is not UNSET:
            field_dict["showPreviousSurname"] = show_previous_surname
        if show_gender is not UNSET:
            field_dict["showGender"] = show_gender
        if show_date_of_birth is not UNSET:
            field_dict["showDateOfBirth"] = show_date_of_birth
        if show_anniversary_date is not UNSET:
            field_dict["showAnniversaryDate"] = show_anniversary_date
        if show_postal_address is not UNSET:
            field_dict["showPostalAddress"] = show_postal_address
        if is_name_mandatory is not UNSET:
            field_dict["isNameMandatory"] = is_name_mandatory
        if is_address_mandatory is not UNSET:
            field_dict["isAddressMandatory"] = is_address_mandatory

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        show_start_date = d.pop("showStartDate", UNSET)

        show_title = d.pop("showTitle", UNSET)

        show_preferred_name = d.pop("showPreferredName", UNSET)

        show_previous_surname = d.pop("showPreviousSurname", UNSET)

        show_gender = d.pop("showGender", UNSET)

        show_date_of_birth = d.pop("showDateOfBirth", UNSET)

        show_anniversary_date = d.pop("showAnniversaryDate", UNSET)

        show_postal_address = d.pop("showPostalAddress", UNSET)

        is_name_mandatory = d.pop("isNameMandatory", UNSET)

        is_address_mandatory = d.pop("isAddressMandatory", UNSET)

        employee_details_fields = cls(
            show_start_date=show_start_date,
            show_title=show_title,
            show_preferred_name=show_preferred_name,
            show_previous_surname=show_previous_surname,
            show_gender=show_gender,
            show_date_of_birth=show_date_of_birth,
            show_anniversary_date=show_anniversary_date,
            show_postal_address=show_postal_address,
            is_name_mandatory=is_name_mandatory,
            is_address_mandatory=is_address_mandatory,
        )

        employee_details_fields.additional_properties = d
        return employee_details_fields

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
