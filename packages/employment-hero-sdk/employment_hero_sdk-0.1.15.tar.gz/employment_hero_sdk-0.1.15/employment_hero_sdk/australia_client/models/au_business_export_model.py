import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.au_business_export_model_budget_entry_method_enum import AuBusinessExportModelBudgetEntryMethodEnum
from ..models.au_business_export_model_day_of_week import AuBusinessExportModelDayOfWeek
from ..models.au_business_export_model_leave_accrual_start_date_type import (
    AuBusinessExportModelLeaveAccrualStartDateType,
)
from ..models.au_business_export_model_nullable_external_service import AuBusinessExportModelNullableExternalService
from ..models.au_business_export_model_nullable_number_of_employees_range_enum import (
    AuBusinessExportModelNullableNumberOfEmployeesRangeEnum,
)
from ..models.au_business_export_model_nullable_pay_cycle_frequency_enum import (
    AuBusinessExportModelNullablePayCycleFrequencyEnum,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="AuBusinessExportModel")


@_attrs_define
class AuBusinessExportModel:
    """
    Attributes:
        abn (Union[Unset, str]):
        suburb (Union[Unset, str]):
        state (Union[Unset, str]):
        management_software_id (Union[Unset, str]):
        sbr_software_provider (Union[Unset, str]):
        sbr_software_id (Union[Unset, str]):
        is_foreign_entity (Union[Unset, bool]):
        foreign_entity_country (Union[Unset, str]):
        default_super_rate (Union[Unset, float]):
        id (Union[Unset, int]):
        name (Union[Unset, str]):
        region (Union[Unset, str]):
        legal_name (Union[Unset, str]):
        contact_name (Union[Unset, str]):
        contact_email_address (Union[Unset, str]):
        contact_phone_number (Union[Unset, str]):
        contact_fax_number (Union[Unset, str]):
        external_id (Union[Unset, str]):
        standard_hours_per_day (Union[Unset, float]):
        journal_service (Union[Unset, str]):
        end_of_week (Union[Unset, AuBusinessExportModelDayOfWeek]):
        initial_financial_year_start (Union[Unset, int]):
        managers_can_edit_roster_budgets (Union[Unset, bool]):
        budget_warning_percent (Union[Unset, float]):
        budget_entry_method (Union[Unset, AuBusinessExportModelBudgetEntryMethodEnum]):
        address_line_1 (Union[Unset, str]):
        address_line_2 (Union[Unset, str]):
        post_code (Union[Unset, str]):
        white_label_name (Union[Unset, str]):
        white_label_id (Union[Unset, int]):
        promo_code (Union[Unset, str]):
        date_created (Union[Unset, datetime.datetime]):
        leave_accrual_start_date_type (Union[Unset, AuBusinessExportModelLeaveAccrualStartDateType]):
        leave_year_start (Union[Unset, datetime.datetime]):
        source (Union[Unset, AuBusinessExportModelNullableExternalService]):
        number_of_employees (Union[Unset, AuBusinessExportModelNullableNumberOfEmployeesRangeEnum]):
        industry_name (Union[Unset, str]):
        pay_cycle_frequency (Union[Unset, AuBusinessExportModelNullablePayCycleFrequencyEnum]):
    """

    abn: Union[Unset, str] = UNSET
    suburb: Union[Unset, str] = UNSET
    state: Union[Unset, str] = UNSET
    management_software_id: Union[Unset, str] = UNSET
    sbr_software_provider: Union[Unset, str] = UNSET
    sbr_software_id: Union[Unset, str] = UNSET
    is_foreign_entity: Union[Unset, bool] = UNSET
    foreign_entity_country: Union[Unset, str] = UNSET
    default_super_rate: Union[Unset, float] = UNSET
    id: Union[Unset, int] = UNSET
    name: Union[Unset, str] = UNSET
    region: Union[Unset, str] = UNSET
    legal_name: Union[Unset, str] = UNSET
    contact_name: Union[Unset, str] = UNSET
    contact_email_address: Union[Unset, str] = UNSET
    contact_phone_number: Union[Unset, str] = UNSET
    contact_fax_number: Union[Unset, str] = UNSET
    external_id: Union[Unset, str] = UNSET
    standard_hours_per_day: Union[Unset, float] = UNSET
    journal_service: Union[Unset, str] = UNSET
    end_of_week: Union[Unset, AuBusinessExportModelDayOfWeek] = UNSET
    initial_financial_year_start: Union[Unset, int] = UNSET
    managers_can_edit_roster_budgets: Union[Unset, bool] = UNSET
    budget_warning_percent: Union[Unset, float] = UNSET
    budget_entry_method: Union[Unset, AuBusinessExportModelBudgetEntryMethodEnum] = UNSET
    address_line_1: Union[Unset, str] = UNSET
    address_line_2: Union[Unset, str] = UNSET
    post_code: Union[Unset, str] = UNSET
    white_label_name: Union[Unset, str] = UNSET
    white_label_id: Union[Unset, int] = UNSET
    promo_code: Union[Unset, str] = UNSET
    date_created: Union[Unset, datetime.datetime] = UNSET
    leave_accrual_start_date_type: Union[Unset, AuBusinessExportModelLeaveAccrualStartDateType] = UNSET
    leave_year_start: Union[Unset, datetime.datetime] = UNSET
    source: Union[Unset, AuBusinessExportModelNullableExternalService] = UNSET
    number_of_employees: Union[Unset, AuBusinessExportModelNullableNumberOfEmployeesRangeEnum] = UNSET
    industry_name: Union[Unset, str] = UNSET
    pay_cycle_frequency: Union[Unset, AuBusinessExportModelNullablePayCycleFrequencyEnum] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        abn = self.abn

        suburb = self.suburb

        state = self.state

        management_software_id = self.management_software_id

        sbr_software_provider = self.sbr_software_provider

        sbr_software_id = self.sbr_software_id

        is_foreign_entity = self.is_foreign_entity

        foreign_entity_country = self.foreign_entity_country

        default_super_rate = self.default_super_rate

        id = self.id

        name = self.name

        region = self.region

        legal_name = self.legal_name

        contact_name = self.contact_name

        contact_email_address = self.contact_email_address

        contact_phone_number = self.contact_phone_number

        contact_fax_number = self.contact_fax_number

        external_id = self.external_id

        standard_hours_per_day = self.standard_hours_per_day

        journal_service = self.journal_service

        end_of_week: Union[Unset, str] = UNSET
        if not isinstance(self.end_of_week, Unset):
            end_of_week = self.end_of_week.value

        initial_financial_year_start = self.initial_financial_year_start

        managers_can_edit_roster_budgets = self.managers_can_edit_roster_budgets

        budget_warning_percent = self.budget_warning_percent

        budget_entry_method: Union[Unset, str] = UNSET
        if not isinstance(self.budget_entry_method, Unset):
            budget_entry_method = self.budget_entry_method.value

        address_line_1 = self.address_line_1

        address_line_2 = self.address_line_2

        post_code = self.post_code

        white_label_name = self.white_label_name

        white_label_id = self.white_label_id

        promo_code = self.promo_code

        date_created: Union[Unset, str] = UNSET
        if not isinstance(self.date_created, Unset):
            date_created = self.date_created.isoformat()

        leave_accrual_start_date_type: Union[Unset, str] = UNSET
        if not isinstance(self.leave_accrual_start_date_type, Unset):
            leave_accrual_start_date_type = self.leave_accrual_start_date_type.value

        leave_year_start: Union[Unset, str] = UNSET
        if not isinstance(self.leave_year_start, Unset):
            leave_year_start = self.leave_year_start.isoformat()

        source: Union[Unset, str] = UNSET
        if not isinstance(self.source, Unset):
            source = self.source.value

        number_of_employees: Union[Unset, str] = UNSET
        if not isinstance(self.number_of_employees, Unset):
            number_of_employees = self.number_of_employees.value

        industry_name = self.industry_name

        pay_cycle_frequency: Union[Unset, str] = UNSET
        if not isinstance(self.pay_cycle_frequency, Unset):
            pay_cycle_frequency = self.pay_cycle_frequency.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if abn is not UNSET:
            field_dict["abn"] = abn
        if suburb is not UNSET:
            field_dict["suburb"] = suburb
        if state is not UNSET:
            field_dict["state"] = state
        if management_software_id is not UNSET:
            field_dict["managementSoftwareId"] = management_software_id
        if sbr_software_provider is not UNSET:
            field_dict["sbrSoftwareProvider"] = sbr_software_provider
        if sbr_software_id is not UNSET:
            field_dict["sbrSoftwareId"] = sbr_software_id
        if is_foreign_entity is not UNSET:
            field_dict["isForeignEntity"] = is_foreign_entity
        if foreign_entity_country is not UNSET:
            field_dict["foreignEntityCountry"] = foreign_entity_country
        if default_super_rate is not UNSET:
            field_dict["defaultSuperRate"] = default_super_rate
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if region is not UNSET:
            field_dict["region"] = region
        if legal_name is not UNSET:
            field_dict["legalName"] = legal_name
        if contact_name is not UNSET:
            field_dict["contactName"] = contact_name
        if contact_email_address is not UNSET:
            field_dict["contactEmailAddress"] = contact_email_address
        if contact_phone_number is not UNSET:
            field_dict["contactPhoneNumber"] = contact_phone_number
        if contact_fax_number is not UNSET:
            field_dict["contactFaxNumber"] = contact_fax_number
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if standard_hours_per_day is not UNSET:
            field_dict["standardHoursPerDay"] = standard_hours_per_day
        if journal_service is not UNSET:
            field_dict["journalService"] = journal_service
        if end_of_week is not UNSET:
            field_dict["endOfWeek"] = end_of_week
        if initial_financial_year_start is not UNSET:
            field_dict["initialFinancialYearStart"] = initial_financial_year_start
        if managers_can_edit_roster_budgets is not UNSET:
            field_dict["managersCanEditRosterBudgets"] = managers_can_edit_roster_budgets
        if budget_warning_percent is not UNSET:
            field_dict["budgetWarningPercent"] = budget_warning_percent
        if budget_entry_method is not UNSET:
            field_dict["budgetEntryMethod"] = budget_entry_method
        if address_line_1 is not UNSET:
            field_dict["addressLine1"] = address_line_1
        if address_line_2 is not UNSET:
            field_dict["addressLine2"] = address_line_2
        if post_code is not UNSET:
            field_dict["postCode"] = post_code
        if white_label_name is not UNSET:
            field_dict["whiteLabelName"] = white_label_name
        if white_label_id is not UNSET:
            field_dict["whiteLabelId"] = white_label_id
        if promo_code is not UNSET:
            field_dict["promoCode"] = promo_code
        if date_created is not UNSET:
            field_dict["dateCreated"] = date_created
        if leave_accrual_start_date_type is not UNSET:
            field_dict["leaveAccrualStartDateType"] = leave_accrual_start_date_type
        if leave_year_start is not UNSET:
            field_dict["leaveYearStart"] = leave_year_start
        if source is not UNSET:
            field_dict["source"] = source
        if number_of_employees is not UNSET:
            field_dict["numberOfEmployees"] = number_of_employees
        if industry_name is not UNSET:
            field_dict["industryName"] = industry_name
        if pay_cycle_frequency is not UNSET:
            field_dict["payCycleFrequency"] = pay_cycle_frequency

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        abn = d.pop("abn", UNSET)

        suburb = d.pop("suburb", UNSET)

        state = d.pop("state", UNSET)

        management_software_id = d.pop("managementSoftwareId", UNSET)

        sbr_software_provider = d.pop("sbrSoftwareProvider", UNSET)

        sbr_software_id = d.pop("sbrSoftwareId", UNSET)

        is_foreign_entity = d.pop("isForeignEntity", UNSET)

        foreign_entity_country = d.pop("foreignEntityCountry", UNSET)

        default_super_rate = d.pop("defaultSuperRate", UNSET)

        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        region = d.pop("region", UNSET)

        legal_name = d.pop("legalName", UNSET)

        contact_name = d.pop("contactName", UNSET)

        contact_email_address = d.pop("contactEmailAddress", UNSET)

        contact_phone_number = d.pop("contactPhoneNumber", UNSET)

        contact_fax_number = d.pop("contactFaxNumber", UNSET)

        external_id = d.pop("externalId", UNSET)

        standard_hours_per_day = d.pop("standardHoursPerDay", UNSET)

        journal_service = d.pop("journalService", UNSET)

        _end_of_week = d.pop("endOfWeek", UNSET)
        end_of_week: Union[Unset, AuBusinessExportModelDayOfWeek]
        if isinstance(_end_of_week, Unset):
            end_of_week = UNSET
        else:
            end_of_week = AuBusinessExportModelDayOfWeek(_end_of_week)

        initial_financial_year_start = d.pop("initialFinancialYearStart", UNSET)

        managers_can_edit_roster_budgets = d.pop("managersCanEditRosterBudgets", UNSET)

        budget_warning_percent = d.pop("budgetWarningPercent", UNSET)

        _budget_entry_method = d.pop("budgetEntryMethod", UNSET)
        budget_entry_method: Union[Unset, AuBusinessExportModelBudgetEntryMethodEnum]
        if isinstance(_budget_entry_method, Unset):
            budget_entry_method = UNSET
        else:
            budget_entry_method = AuBusinessExportModelBudgetEntryMethodEnum(_budget_entry_method)

        address_line_1 = d.pop("addressLine1", UNSET)

        address_line_2 = d.pop("addressLine2", UNSET)

        post_code = d.pop("postCode", UNSET)

        white_label_name = d.pop("whiteLabelName", UNSET)

        white_label_id = d.pop("whiteLabelId", UNSET)

        promo_code = d.pop("promoCode", UNSET)

        _date_created = d.pop("dateCreated", UNSET)
        date_created: Union[Unset, datetime.datetime]
        if isinstance(_date_created, Unset):
            date_created = UNSET
        else:
            date_created = isoparse(_date_created)

        _leave_accrual_start_date_type = d.pop("leaveAccrualStartDateType", UNSET)
        leave_accrual_start_date_type: Union[Unset, AuBusinessExportModelLeaveAccrualStartDateType]
        if isinstance(_leave_accrual_start_date_type, Unset):
            leave_accrual_start_date_type = UNSET
        else:
            leave_accrual_start_date_type = AuBusinessExportModelLeaveAccrualStartDateType(
                _leave_accrual_start_date_type
            )

        _leave_year_start = d.pop("leaveYearStart", UNSET)
        leave_year_start: Union[Unset, datetime.datetime]
        if isinstance(_leave_year_start, Unset):
            leave_year_start = UNSET
        else:
            leave_year_start = isoparse(_leave_year_start)

        _source = d.pop("source", UNSET)
        source: Union[Unset, AuBusinessExportModelNullableExternalService]
        if isinstance(_source, Unset):
            source = UNSET
        else:
            source = AuBusinessExportModelNullableExternalService(_source)

        _number_of_employees = d.pop("numberOfEmployees", UNSET)
        number_of_employees: Union[Unset, AuBusinessExportModelNullableNumberOfEmployeesRangeEnum]
        if isinstance(_number_of_employees, Unset):
            number_of_employees = UNSET
        else:
            number_of_employees = AuBusinessExportModelNullableNumberOfEmployeesRangeEnum(_number_of_employees)

        industry_name = d.pop("industryName", UNSET)

        _pay_cycle_frequency = d.pop("payCycleFrequency", UNSET)
        pay_cycle_frequency: Union[Unset, AuBusinessExportModelNullablePayCycleFrequencyEnum]
        if isinstance(_pay_cycle_frequency, Unset):
            pay_cycle_frequency = UNSET
        else:
            pay_cycle_frequency = AuBusinessExportModelNullablePayCycleFrequencyEnum(_pay_cycle_frequency)

        au_business_export_model = cls(
            abn=abn,
            suburb=suburb,
            state=state,
            management_software_id=management_software_id,
            sbr_software_provider=sbr_software_provider,
            sbr_software_id=sbr_software_id,
            is_foreign_entity=is_foreign_entity,
            foreign_entity_country=foreign_entity_country,
            default_super_rate=default_super_rate,
            id=id,
            name=name,
            region=region,
            legal_name=legal_name,
            contact_name=contact_name,
            contact_email_address=contact_email_address,
            contact_phone_number=contact_phone_number,
            contact_fax_number=contact_fax_number,
            external_id=external_id,
            standard_hours_per_day=standard_hours_per_day,
            journal_service=journal_service,
            end_of_week=end_of_week,
            initial_financial_year_start=initial_financial_year_start,
            managers_can_edit_roster_budgets=managers_can_edit_roster_budgets,
            budget_warning_percent=budget_warning_percent,
            budget_entry_method=budget_entry_method,
            address_line_1=address_line_1,
            address_line_2=address_line_2,
            post_code=post_code,
            white_label_name=white_label_name,
            white_label_id=white_label_id,
            promo_code=promo_code,
            date_created=date_created,
            leave_accrual_start_date_type=leave_accrual_start_date_type,
            leave_year_start=leave_year_start,
            source=source,
            number_of_employees=number_of_employees,
            industry_name=industry_name,
            pay_cycle_frequency=pay_cycle_frequency,
        )

        au_business_export_model.additional_properties = d
        return au_business_export_model

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
