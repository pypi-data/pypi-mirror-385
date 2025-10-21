import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="SignupModel")


@_attrs_define
class SignupModel:
    """
    Attributes:
        business_id (Union[Unset, int]):
        business_name (Union[Unset, str]):
        date_created (Union[Unset, datetime.datetime]):
        billing_plan (Union[Unset, str]):
        realm_id (Union[Unset, str]):
        external_id (Union[Unset, str]):
        email_addresses (Union[Unset, str]):
        user_ids (Union[Unset, str]):
        number_of_complete_employees (Union[Unset, int]):
        number_of_incomplete_employees (Union[Unset, int]):
        date_last_pay_run_finalised (Union[Unset, datetime.datetime]):
    """

    business_id: Union[Unset, int] = UNSET
    business_name: Union[Unset, str] = UNSET
    date_created: Union[Unset, datetime.datetime] = UNSET
    billing_plan: Union[Unset, str] = UNSET
    realm_id: Union[Unset, str] = UNSET
    external_id: Union[Unset, str] = UNSET
    email_addresses: Union[Unset, str] = UNSET
    user_ids: Union[Unset, str] = UNSET
    number_of_complete_employees: Union[Unset, int] = UNSET
    number_of_incomplete_employees: Union[Unset, int] = UNSET
    date_last_pay_run_finalised: Union[Unset, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        business_id = self.business_id

        business_name = self.business_name

        date_created: Union[Unset, str] = UNSET
        if not isinstance(self.date_created, Unset):
            date_created = self.date_created.isoformat()

        billing_plan = self.billing_plan

        realm_id = self.realm_id

        external_id = self.external_id

        email_addresses = self.email_addresses

        user_ids = self.user_ids

        number_of_complete_employees = self.number_of_complete_employees

        number_of_incomplete_employees = self.number_of_incomplete_employees

        date_last_pay_run_finalised: Union[Unset, str] = UNSET
        if not isinstance(self.date_last_pay_run_finalised, Unset):
            date_last_pay_run_finalised = self.date_last_pay_run_finalised.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if business_id is not UNSET:
            field_dict["businessId"] = business_id
        if business_name is not UNSET:
            field_dict["businessName"] = business_name
        if date_created is not UNSET:
            field_dict["dateCreated"] = date_created
        if billing_plan is not UNSET:
            field_dict["billingPlan"] = billing_plan
        if realm_id is not UNSET:
            field_dict["realmId"] = realm_id
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if email_addresses is not UNSET:
            field_dict["emailAddresses"] = email_addresses
        if user_ids is not UNSET:
            field_dict["userIds"] = user_ids
        if number_of_complete_employees is not UNSET:
            field_dict["numberOfCompleteEmployees"] = number_of_complete_employees
        if number_of_incomplete_employees is not UNSET:
            field_dict["numberOfIncompleteEmployees"] = number_of_incomplete_employees
        if date_last_pay_run_finalised is not UNSET:
            field_dict["dateLastPayRunFinalised"] = date_last_pay_run_finalised

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        business_id = d.pop("businessId", UNSET)

        business_name = d.pop("businessName", UNSET)

        _date_created = d.pop("dateCreated", UNSET)
        date_created: Union[Unset, datetime.datetime]
        if isinstance(_date_created, Unset):
            date_created = UNSET
        else:
            date_created = isoparse(_date_created)

        billing_plan = d.pop("billingPlan", UNSET)

        realm_id = d.pop("realmId", UNSET)

        external_id = d.pop("externalId", UNSET)

        email_addresses = d.pop("emailAddresses", UNSET)

        user_ids = d.pop("userIds", UNSET)

        number_of_complete_employees = d.pop("numberOfCompleteEmployees", UNSET)

        number_of_incomplete_employees = d.pop("numberOfIncompleteEmployees", UNSET)

        _date_last_pay_run_finalised = d.pop("dateLastPayRunFinalised", UNSET)
        date_last_pay_run_finalised: Union[Unset, datetime.datetime]
        if isinstance(_date_last_pay_run_finalised, Unset):
            date_last_pay_run_finalised = UNSET
        else:
            date_last_pay_run_finalised = isoparse(_date_last_pay_run_finalised)

        signup_model = cls(
            business_id=business_id,
            business_name=business_name,
            date_created=date_created,
            billing_plan=billing_plan,
            realm_id=realm_id,
            external_id=external_id,
            email_addresses=email_addresses,
            user_ids=user_ids,
            number_of_complete_employees=number_of_complete_employees,
            number_of_incomplete_employees=number_of_incomplete_employees,
            date_last_pay_run_finalised=date_last_pay_run_finalised,
        )

        signup_model.additional_properties = d
        return signup_model

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
