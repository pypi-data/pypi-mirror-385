import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="EmployeeDetailsModel")


@_attrs_define
class EmployeeDetailsModel:
    """
    Attributes:
        id (Union[Unset, int]):
        title (Union[Unset, str]):
        first_name (Union[Unset, str]):
        preferred_name (Union[Unset, str]):
        middle_name (Union[Unset, str]):
        surname (Union[Unset, str]):
        gender (Union[Unset, str]):
        date_of_birth (Union[Unset, datetime.datetime]):
        anniversary_date (Union[Unset, datetime.datetime]):
        external_id (Union[Unset, str]):
        residential_street_address (Union[Unset, str]):
        residential_address_line_2 (Union[Unset, str]):
        residential_suburb (Union[Unset, str]):
        residential_state (Union[Unset, str]):
        residential_post_code (Union[Unset, str]):
        postal_street_address (Union[Unset, str]):
        postal_address_line_2 (Union[Unset, str]):
        postal_suburb (Union[Unset, str]):
        postal_state (Union[Unset, str]):
        postal_post_code (Union[Unset, str]):
        email_address (Union[Unset, str]):
        home_phone (Union[Unset, str]):
        work_phone (Union[Unset, str]):
        mobile_phone (Union[Unset, str]):
        start_date (Union[Unset, datetime.datetime]):
        end_date (Union[Unset, datetime.datetime]):
        residential_city (Union[Unset, str]):
        residential_county (Union[Unset, str]):
        postal_city (Union[Unset, str]):
        postal_county (Union[Unset, str]):
    """

    id: Union[Unset, int] = UNSET
    title: Union[Unset, str] = UNSET
    first_name: Union[Unset, str] = UNSET
    preferred_name: Union[Unset, str] = UNSET
    middle_name: Union[Unset, str] = UNSET
    surname: Union[Unset, str] = UNSET
    gender: Union[Unset, str] = UNSET
    date_of_birth: Union[Unset, datetime.datetime] = UNSET
    anniversary_date: Union[Unset, datetime.datetime] = UNSET
    external_id: Union[Unset, str] = UNSET
    residential_street_address: Union[Unset, str] = UNSET
    residential_address_line_2: Union[Unset, str] = UNSET
    residential_suburb: Union[Unset, str] = UNSET
    residential_state: Union[Unset, str] = UNSET
    residential_post_code: Union[Unset, str] = UNSET
    postal_street_address: Union[Unset, str] = UNSET
    postal_address_line_2: Union[Unset, str] = UNSET
    postal_suburb: Union[Unset, str] = UNSET
    postal_state: Union[Unset, str] = UNSET
    postal_post_code: Union[Unset, str] = UNSET
    email_address: Union[Unset, str] = UNSET
    home_phone: Union[Unset, str] = UNSET
    work_phone: Union[Unset, str] = UNSET
    mobile_phone: Union[Unset, str] = UNSET
    start_date: Union[Unset, datetime.datetime] = UNSET
    end_date: Union[Unset, datetime.datetime] = UNSET
    residential_city: Union[Unset, str] = UNSET
    residential_county: Union[Unset, str] = UNSET
    postal_city: Union[Unset, str] = UNSET
    postal_county: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        title = self.title

        first_name = self.first_name

        preferred_name = self.preferred_name

        middle_name = self.middle_name

        surname = self.surname

        gender = self.gender

        date_of_birth: Union[Unset, str] = UNSET
        if not isinstance(self.date_of_birth, Unset):
            date_of_birth = self.date_of_birth.isoformat()

        anniversary_date: Union[Unset, str] = UNSET
        if not isinstance(self.anniversary_date, Unset):
            anniversary_date = self.anniversary_date.isoformat()

        external_id = self.external_id

        residential_street_address = self.residential_street_address

        residential_address_line_2 = self.residential_address_line_2

        residential_suburb = self.residential_suburb

        residential_state = self.residential_state

        residential_post_code = self.residential_post_code

        postal_street_address = self.postal_street_address

        postal_address_line_2 = self.postal_address_line_2

        postal_suburb = self.postal_suburb

        postal_state = self.postal_state

        postal_post_code = self.postal_post_code

        email_address = self.email_address

        home_phone = self.home_phone

        work_phone = self.work_phone

        mobile_phone = self.mobile_phone

        start_date: Union[Unset, str] = UNSET
        if not isinstance(self.start_date, Unset):
            start_date = self.start_date.isoformat()

        end_date: Union[Unset, str] = UNSET
        if not isinstance(self.end_date, Unset):
            end_date = self.end_date.isoformat()

        residential_city = self.residential_city

        residential_county = self.residential_county

        postal_city = self.postal_city

        postal_county = self.postal_county

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if title is not UNSET:
            field_dict["title"] = title
        if first_name is not UNSET:
            field_dict["firstName"] = first_name
        if preferred_name is not UNSET:
            field_dict["preferredName"] = preferred_name
        if middle_name is not UNSET:
            field_dict["middleName"] = middle_name
        if surname is not UNSET:
            field_dict["surname"] = surname
        if gender is not UNSET:
            field_dict["gender"] = gender
        if date_of_birth is not UNSET:
            field_dict["dateOfBirth"] = date_of_birth
        if anniversary_date is not UNSET:
            field_dict["anniversaryDate"] = anniversary_date
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if residential_street_address is not UNSET:
            field_dict["residentialStreetAddress"] = residential_street_address
        if residential_address_line_2 is not UNSET:
            field_dict["residentialAddressLine2"] = residential_address_line_2
        if residential_suburb is not UNSET:
            field_dict["residentialSuburb"] = residential_suburb
        if residential_state is not UNSET:
            field_dict["residentialState"] = residential_state
        if residential_post_code is not UNSET:
            field_dict["residentialPostCode"] = residential_post_code
        if postal_street_address is not UNSET:
            field_dict["postalStreetAddress"] = postal_street_address
        if postal_address_line_2 is not UNSET:
            field_dict["postalAddressLine2"] = postal_address_line_2
        if postal_suburb is not UNSET:
            field_dict["postalSuburb"] = postal_suburb
        if postal_state is not UNSET:
            field_dict["postalState"] = postal_state
        if postal_post_code is not UNSET:
            field_dict["postalPostCode"] = postal_post_code
        if email_address is not UNSET:
            field_dict["emailAddress"] = email_address
        if home_phone is not UNSET:
            field_dict["homePhone"] = home_phone
        if work_phone is not UNSET:
            field_dict["workPhone"] = work_phone
        if mobile_phone is not UNSET:
            field_dict["mobilePhone"] = mobile_phone
        if start_date is not UNSET:
            field_dict["startDate"] = start_date
        if end_date is not UNSET:
            field_dict["endDate"] = end_date
        if residential_city is not UNSET:
            field_dict["residentialCity"] = residential_city
        if residential_county is not UNSET:
            field_dict["residentialCounty"] = residential_county
        if postal_city is not UNSET:
            field_dict["postalCity"] = postal_city
        if postal_county is not UNSET:
            field_dict["postalCounty"] = postal_county

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        title = d.pop("title", UNSET)

        first_name = d.pop("firstName", UNSET)

        preferred_name = d.pop("preferredName", UNSET)

        middle_name = d.pop("middleName", UNSET)

        surname = d.pop("surname", UNSET)

        gender = d.pop("gender", UNSET)

        _date_of_birth = d.pop("dateOfBirth", UNSET)
        date_of_birth: Union[Unset, datetime.datetime]
        if isinstance(_date_of_birth, Unset):
            date_of_birth = UNSET
        else:
            date_of_birth = isoparse(_date_of_birth)

        _anniversary_date = d.pop("anniversaryDate", UNSET)
        anniversary_date: Union[Unset, datetime.datetime]
        if isinstance(_anniversary_date, Unset):
            anniversary_date = UNSET
        else:
            anniversary_date = isoparse(_anniversary_date)

        external_id = d.pop("externalId", UNSET)

        residential_street_address = d.pop("residentialStreetAddress", UNSET)

        residential_address_line_2 = d.pop("residentialAddressLine2", UNSET)

        residential_suburb = d.pop("residentialSuburb", UNSET)

        residential_state = d.pop("residentialState", UNSET)

        residential_post_code = d.pop("residentialPostCode", UNSET)

        postal_street_address = d.pop("postalStreetAddress", UNSET)

        postal_address_line_2 = d.pop("postalAddressLine2", UNSET)

        postal_suburb = d.pop("postalSuburb", UNSET)

        postal_state = d.pop("postalState", UNSET)

        postal_post_code = d.pop("postalPostCode", UNSET)

        email_address = d.pop("emailAddress", UNSET)

        home_phone = d.pop("homePhone", UNSET)

        work_phone = d.pop("workPhone", UNSET)

        mobile_phone = d.pop("mobilePhone", UNSET)

        _start_date = d.pop("startDate", UNSET)
        start_date: Union[Unset, datetime.datetime]
        if isinstance(_start_date, Unset):
            start_date = UNSET
        else:
            start_date = isoparse(_start_date)

        _end_date = d.pop("endDate", UNSET)
        end_date: Union[Unset, datetime.datetime]
        if isinstance(_end_date, Unset):
            end_date = UNSET
        else:
            end_date = isoparse(_end_date)

        residential_city = d.pop("residentialCity", UNSET)

        residential_county = d.pop("residentialCounty", UNSET)

        postal_city = d.pop("postalCity", UNSET)

        postal_county = d.pop("postalCounty", UNSET)

        employee_details_model = cls(
            id=id,
            title=title,
            first_name=first_name,
            preferred_name=preferred_name,
            middle_name=middle_name,
            surname=surname,
            gender=gender,
            date_of_birth=date_of_birth,
            anniversary_date=anniversary_date,
            external_id=external_id,
            residential_street_address=residential_street_address,
            residential_address_line_2=residential_address_line_2,
            residential_suburb=residential_suburb,
            residential_state=residential_state,
            residential_post_code=residential_post_code,
            postal_street_address=postal_street_address,
            postal_address_line_2=postal_address_line_2,
            postal_suburb=postal_suburb,
            postal_state=postal_state,
            postal_post_code=postal_post_code,
            email_address=email_address,
            home_phone=home_phone,
            work_phone=work_phone,
            mobile_phone=mobile_phone,
            start_date=start_date,
            end_date=end_date,
            residential_city=residential_city,
            residential_county=residential_county,
            postal_city=postal_city,
            postal_county=postal_county,
        )

        employee_details_model.additional_properties = d
        return employee_details_model

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
