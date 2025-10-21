import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="AuActiveEmployeesModel")


@_attrs_define
class AuActiveEmployeesModel:
    """
    Attributes:
        abn (Union[Unset, str]):
        is_stp_enabled (Union[Unset, bool]):
        business_id (Union[Unset, int]):
        business_name (Union[Unset, str]):
        date_created (Union[Unset, datetime.datetime]):
        billing_plan (Union[Unset, str]):
        realm_id (Union[Unset, str]):
        external_id (Union[Unset, str]):
        email_addresses (Union[Unset, str]):
        user_ids (Union[Unset, str]):
        number_of_incomplete_employees (Union[Unset, int]):
        number_of_complete_employees (Union[Unset, int]):
        number_of_employees_paid (Union[Unset, int]):
        number_of_pay_runs (Union[Unset, int]):
        date_last_pay_run_finalised (Union[Unset, datetime.datetime]):
        date_last_billable_activity (Union[Unset, datetime.datetime]):
        active_emps (Union[Unset, int]):
    """

    abn: Union[Unset, str] = UNSET
    is_stp_enabled: Union[Unset, bool] = UNSET
    business_id: Union[Unset, int] = UNSET
    business_name: Union[Unset, str] = UNSET
    date_created: Union[Unset, datetime.datetime] = UNSET
    billing_plan: Union[Unset, str] = UNSET
    realm_id: Union[Unset, str] = UNSET
    external_id: Union[Unset, str] = UNSET
    email_addresses: Union[Unset, str] = UNSET
    user_ids: Union[Unset, str] = UNSET
    number_of_incomplete_employees: Union[Unset, int] = UNSET
    number_of_complete_employees: Union[Unset, int] = UNSET
    number_of_employees_paid: Union[Unset, int] = UNSET
    number_of_pay_runs: Union[Unset, int] = UNSET
    date_last_pay_run_finalised: Union[Unset, datetime.datetime] = UNSET
    date_last_billable_activity: Union[Unset, datetime.datetime] = UNSET
    active_emps: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        abn = self.abn

        is_stp_enabled = self.is_stp_enabled

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

        number_of_incomplete_employees = self.number_of_incomplete_employees

        number_of_complete_employees = self.number_of_complete_employees

        number_of_employees_paid = self.number_of_employees_paid

        number_of_pay_runs = self.number_of_pay_runs

        date_last_pay_run_finalised: Union[Unset, str] = UNSET
        if not isinstance(self.date_last_pay_run_finalised, Unset):
            date_last_pay_run_finalised = self.date_last_pay_run_finalised.isoformat()

        date_last_billable_activity: Union[Unset, str] = UNSET
        if not isinstance(self.date_last_billable_activity, Unset):
            date_last_billable_activity = self.date_last_billable_activity.isoformat()

        active_emps = self.active_emps

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if abn is not UNSET:
            field_dict["abn"] = abn
        if is_stp_enabled is not UNSET:
            field_dict["isStpEnabled"] = is_stp_enabled
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
        if number_of_incomplete_employees is not UNSET:
            field_dict["numberOfIncompleteEmployees"] = number_of_incomplete_employees
        if number_of_complete_employees is not UNSET:
            field_dict["numberOfCompleteEmployees"] = number_of_complete_employees
        if number_of_employees_paid is not UNSET:
            field_dict["numberOfEmployeesPaid"] = number_of_employees_paid
        if number_of_pay_runs is not UNSET:
            field_dict["numberOfPayRuns"] = number_of_pay_runs
        if date_last_pay_run_finalised is not UNSET:
            field_dict["dateLastPayRunFinalised"] = date_last_pay_run_finalised
        if date_last_billable_activity is not UNSET:
            field_dict["dateLastBillableActivity"] = date_last_billable_activity
        if active_emps is not UNSET:
            field_dict["activeEmps"] = active_emps

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        abn = d.pop("abn", UNSET)

        is_stp_enabled = d.pop("isStpEnabled", UNSET)

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

        number_of_incomplete_employees = d.pop("numberOfIncompleteEmployees", UNSET)

        number_of_complete_employees = d.pop("numberOfCompleteEmployees", UNSET)

        number_of_employees_paid = d.pop("numberOfEmployeesPaid", UNSET)

        number_of_pay_runs = d.pop("numberOfPayRuns", UNSET)

        _date_last_pay_run_finalised = d.pop("dateLastPayRunFinalised", UNSET)
        date_last_pay_run_finalised: Union[Unset, datetime.datetime]
        if isinstance(_date_last_pay_run_finalised, Unset):
            date_last_pay_run_finalised = UNSET
        else:
            date_last_pay_run_finalised = isoparse(_date_last_pay_run_finalised)

        _date_last_billable_activity = d.pop("dateLastBillableActivity", UNSET)
        date_last_billable_activity: Union[Unset, datetime.datetime]
        if isinstance(_date_last_billable_activity, Unset):
            date_last_billable_activity = UNSET
        else:
            date_last_billable_activity = isoparse(_date_last_billable_activity)

        active_emps = d.pop("activeEmps", UNSET)

        au_active_employees_model = cls(
            abn=abn,
            is_stp_enabled=is_stp_enabled,
            business_id=business_id,
            business_name=business_name,
            date_created=date_created,
            billing_plan=billing_plan,
            realm_id=realm_id,
            external_id=external_id,
            email_addresses=email_addresses,
            user_ids=user_ids,
            number_of_incomplete_employees=number_of_incomplete_employees,
            number_of_complete_employees=number_of_complete_employees,
            number_of_employees_paid=number_of_employees_paid,
            number_of_pay_runs=number_of_pay_runs,
            date_last_pay_run_finalised=date_last_pay_run_finalised,
            date_last_billable_activity=date_last_billable_activity,
            active_emps=active_emps,
        )

        au_active_employees_model.additional_properties = d
        return au_active_employees_model

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
