import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.employee_partial_edit_model_employee_starter_type_enum import (
    EmployeePartialEditModelEmployeeStarterTypeEnum,
)
from ..models.employee_partial_edit_model_employee_timesheet_setting import (
    EmployeePartialEditModelEmployeeTimesheetSetting,
)
from ..models.employee_partial_edit_model_external_service import EmployeePartialEditModelExternalService
from ..models.employee_partial_edit_model_nullable_address_type_enum import (
    EmployeePartialEditModelNullableAddressTypeEnum,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.bank_account_edit_model import BankAccountEditModel
    from ..models.employee_partial_edit_model_i_dictionary_string_string import (
        EmployeePartialEditModelIDictionaryStringString,
    )


T = TypeVar("T", bound="EmployeePartialEditModel")


@_attrs_define
class EmployeePartialEditModel:
    """
    Attributes:
        id (Union[Unset, int]):
        anniversary_date (Union[Unset, datetime.datetime]):
        external_id (Union[Unset, str]):
        start_date (Union[Unset, datetime.datetime]):
        end_date (Union[Unset, datetime.datetime]):
        business_id (Union[Unset, int]):
        tax_file_number (Union[Unset, str]):
        tax_file_number_masked (Union[Unset, str]):
        bank_accounts (Union[Unset, List['BankAccountEditModel']]):
        external_reference_id (Union[Unset, str]):
        payroll_id (Union[Unset, str]):
        employee_starter_type (Union[Unset, EmployeePartialEditModelEmployeeStarterTypeEnum]):
        source (Union[Unset, EmployeePartialEditModelExternalService]):
        tags_string (Union[Unset, str]):
        timesheet_setting (Union[Unset, EmployeePartialEditModelEmployeeTimesheetSetting]):
        termination_reason (Union[Unset, str]):
        portable_long_service_leave_id (Union[Unset, str]):
        include_in_portable_long_service_leave_report (Union[Unset, bool]):
        title_id (Union[Unset, int]):
        first_name (Union[Unset, str]):
        other_name (Union[Unset, str]):
        middle_name (Union[Unset, str]):
        surname (Union[Unset, str]):
        previous_surname (Union[Unset, str]):
        legal_name (Union[Unset, str]):
        date_of_birth (Union[Unset, datetime.datetime]):
        gender (Union[Unset, str]):
        residential_street_address (Union[Unset, str]):
        residential_address_line_2 (Union[Unset, str]):
        residential_suburb_id (Union[Unset, int]):
        residential_suburb (Union[Unset, str]):
        residential_state (Union[Unset, str]):
        residential_postcode (Union[Unset, str]):
        residential_country (Union[Unset, str]):
        residential_country_id (Union[Unset, str]):
        is_overseas_residential_address (Union[Unset, bool]):
        residential_address_type (Union[Unset, EmployeePartialEditModelNullableAddressTypeEnum]):
        residential_block_number (Union[Unset, str]):
        residential_level_number (Union[Unset, str]):
        residential_unit_number (Union[Unset, str]):
        residential_street_name (Union[Unset, str]):
        residential_address_line_3 (Union[Unset, str]):
        postal_street_address (Union[Unset, str]):
        postal_address_line_2 (Union[Unset, str]):
        postal_suburb_id (Union[Unset, int]):
        postal_suburb (Union[Unset, str]):
        postal_state (Union[Unset, str]):
        postal_postcode (Union[Unset, str]):
        postal_country (Union[Unset, str]):
        postal_country_id (Union[Unset, str]):
        is_overseas_postal_address (Union[Unset, bool]):
        postal_address_type (Union[Unset, EmployeePartialEditModelNullableAddressTypeEnum]):
        postal_block_number (Union[Unset, str]):
        postal_level_number (Union[Unset, str]):
        postal_unit_number (Union[Unset, str]):
        postal_street_name (Union[Unset, str]):
        postal_address_line_3 (Union[Unset, str]):
        is_postal_address_same_as_residential (Union[Unset, bool]):
        email (Union[Unset, str]):
        home_phone (Union[Unset, str]):
        work_phone (Union[Unset, str]):
        mobile_phone (Union[Unset, str]):
        residential_address_mdm_id (Union[Unset, str]):
        residential_address_mdm_version (Union[Unset, int]):
        residential_address_mdm_schema_version (Union[Unset, str]):
        postal_address_mdm_id (Union[Unset, str]):
        postal_address_mdm_version (Union[Unset, int]):
        postal_address_mdm_schema_version (Union[Unset, str]):
        triggered_from_mdm (Union[Unset, bool]):
        send_to_mdm (Union[Unset, bool]):
        ignore_fields (Union[Unset, EmployeePartialEditModelIDictionaryStringString]):
        mdm_sync_user (Union[Unset, bool]):
    """

    id: Union[Unset, int] = UNSET
    anniversary_date: Union[Unset, datetime.datetime] = UNSET
    external_id: Union[Unset, str] = UNSET
    start_date: Union[Unset, datetime.datetime] = UNSET
    end_date: Union[Unset, datetime.datetime] = UNSET
    business_id: Union[Unset, int] = UNSET
    tax_file_number: Union[Unset, str] = UNSET
    tax_file_number_masked: Union[Unset, str] = UNSET
    bank_accounts: Union[Unset, List["BankAccountEditModel"]] = UNSET
    external_reference_id: Union[Unset, str] = UNSET
    payroll_id: Union[Unset, str] = UNSET
    employee_starter_type: Union[Unset, EmployeePartialEditModelEmployeeStarterTypeEnum] = UNSET
    source: Union[Unset, EmployeePartialEditModelExternalService] = UNSET
    tags_string: Union[Unset, str] = UNSET
    timesheet_setting: Union[Unset, EmployeePartialEditModelEmployeeTimesheetSetting] = UNSET
    termination_reason: Union[Unset, str] = UNSET
    portable_long_service_leave_id: Union[Unset, str] = UNSET
    include_in_portable_long_service_leave_report: Union[Unset, bool] = UNSET
    title_id: Union[Unset, int] = UNSET
    first_name: Union[Unset, str] = UNSET
    other_name: Union[Unset, str] = UNSET
    middle_name: Union[Unset, str] = UNSET
    surname: Union[Unset, str] = UNSET
    previous_surname: Union[Unset, str] = UNSET
    legal_name: Union[Unset, str] = UNSET
    date_of_birth: Union[Unset, datetime.datetime] = UNSET
    gender: Union[Unset, str] = UNSET
    residential_street_address: Union[Unset, str] = UNSET
    residential_address_line_2: Union[Unset, str] = UNSET
    residential_suburb_id: Union[Unset, int] = UNSET
    residential_suburb: Union[Unset, str] = UNSET
    residential_state: Union[Unset, str] = UNSET
    residential_postcode: Union[Unset, str] = UNSET
    residential_country: Union[Unset, str] = UNSET
    residential_country_id: Union[Unset, str] = UNSET
    is_overseas_residential_address: Union[Unset, bool] = UNSET
    residential_address_type: Union[Unset, EmployeePartialEditModelNullableAddressTypeEnum] = UNSET
    residential_block_number: Union[Unset, str] = UNSET
    residential_level_number: Union[Unset, str] = UNSET
    residential_unit_number: Union[Unset, str] = UNSET
    residential_street_name: Union[Unset, str] = UNSET
    residential_address_line_3: Union[Unset, str] = UNSET
    postal_street_address: Union[Unset, str] = UNSET
    postal_address_line_2: Union[Unset, str] = UNSET
    postal_suburb_id: Union[Unset, int] = UNSET
    postal_suburb: Union[Unset, str] = UNSET
    postal_state: Union[Unset, str] = UNSET
    postal_postcode: Union[Unset, str] = UNSET
    postal_country: Union[Unset, str] = UNSET
    postal_country_id: Union[Unset, str] = UNSET
    is_overseas_postal_address: Union[Unset, bool] = UNSET
    postal_address_type: Union[Unset, EmployeePartialEditModelNullableAddressTypeEnum] = UNSET
    postal_block_number: Union[Unset, str] = UNSET
    postal_level_number: Union[Unset, str] = UNSET
    postal_unit_number: Union[Unset, str] = UNSET
    postal_street_name: Union[Unset, str] = UNSET
    postal_address_line_3: Union[Unset, str] = UNSET
    is_postal_address_same_as_residential: Union[Unset, bool] = UNSET
    email: Union[Unset, str] = UNSET
    home_phone: Union[Unset, str] = UNSET
    work_phone: Union[Unset, str] = UNSET
    mobile_phone: Union[Unset, str] = UNSET
    residential_address_mdm_id: Union[Unset, str] = UNSET
    residential_address_mdm_version: Union[Unset, int] = UNSET
    residential_address_mdm_schema_version: Union[Unset, str] = UNSET
    postal_address_mdm_id: Union[Unset, str] = UNSET
    postal_address_mdm_version: Union[Unset, int] = UNSET
    postal_address_mdm_schema_version: Union[Unset, str] = UNSET
    triggered_from_mdm: Union[Unset, bool] = UNSET
    send_to_mdm: Union[Unset, bool] = UNSET
    ignore_fields: Union[Unset, "EmployeePartialEditModelIDictionaryStringString"] = UNSET
    mdm_sync_user: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        anniversary_date: Union[Unset, str] = UNSET
        if not isinstance(self.anniversary_date, Unset):
            anniversary_date = self.anniversary_date.isoformat()

        external_id = self.external_id

        start_date: Union[Unset, str] = UNSET
        if not isinstance(self.start_date, Unset):
            start_date = self.start_date.isoformat()

        end_date: Union[Unset, str] = UNSET
        if not isinstance(self.end_date, Unset):
            end_date = self.end_date.isoformat()

        business_id = self.business_id

        tax_file_number = self.tax_file_number

        tax_file_number_masked = self.tax_file_number_masked

        bank_accounts: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.bank_accounts, Unset):
            bank_accounts = []
            for bank_accounts_item_data in self.bank_accounts:
                bank_accounts_item = bank_accounts_item_data.to_dict()
                bank_accounts.append(bank_accounts_item)

        external_reference_id = self.external_reference_id

        payroll_id = self.payroll_id

        employee_starter_type: Union[Unset, str] = UNSET
        if not isinstance(self.employee_starter_type, Unset):
            employee_starter_type = self.employee_starter_type.value

        source: Union[Unset, str] = UNSET
        if not isinstance(self.source, Unset):
            source = self.source.value

        tags_string = self.tags_string

        timesheet_setting: Union[Unset, str] = UNSET
        if not isinstance(self.timesheet_setting, Unset):
            timesheet_setting = self.timesheet_setting.value

        termination_reason = self.termination_reason

        portable_long_service_leave_id = self.portable_long_service_leave_id

        include_in_portable_long_service_leave_report = self.include_in_portable_long_service_leave_report

        title_id = self.title_id

        first_name = self.first_name

        other_name = self.other_name

        middle_name = self.middle_name

        surname = self.surname

        previous_surname = self.previous_surname

        legal_name = self.legal_name

        date_of_birth: Union[Unset, str] = UNSET
        if not isinstance(self.date_of_birth, Unset):
            date_of_birth = self.date_of_birth.isoformat()

        gender = self.gender

        residential_street_address = self.residential_street_address

        residential_address_line_2 = self.residential_address_line_2

        residential_suburb_id = self.residential_suburb_id

        residential_suburb = self.residential_suburb

        residential_state = self.residential_state

        residential_postcode = self.residential_postcode

        residential_country = self.residential_country

        residential_country_id = self.residential_country_id

        is_overseas_residential_address = self.is_overseas_residential_address

        residential_address_type: Union[Unset, str] = UNSET
        if not isinstance(self.residential_address_type, Unset):
            residential_address_type = self.residential_address_type.value

        residential_block_number = self.residential_block_number

        residential_level_number = self.residential_level_number

        residential_unit_number = self.residential_unit_number

        residential_street_name = self.residential_street_name

        residential_address_line_3 = self.residential_address_line_3

        postal_street_address = self.postal_street_address

        postal_address_line_2 = self.postal_address_line_2

        postal_suburb_id = self.postal_suburb_id

        postal_suburb = self.postal_suburb

        postal_state = self.postal_state

        postal_postcode = self.postal_postcode

        postal_country = self.postal_country

        postal_country_id = self.postal_country_id

        is_overseas_postal_address = self.is_overseas_postal_address

        postal_address_type: Union[Unset, str] = UNSET
        if not isinstance(self.postal_address_type, Unset):
            postal_address_type = self.postal_address_type.value

        postal_block_number = self.postal_block_number

        postal_level_number = self.postal_level_number

        postal_unit_number = self.postal_unit_number

        postal_street_name = self.postal_street_name

        postal_address_line_3 = self.postal_address_line_3

        is_postal_address_same_as_residential = self.is_postal_address_same_as_residential

        email = self.email

        home_phone = self.home_phone

        work_phone = self.work_phone

        mobile_phone = self.mobile_phone

        residential_address_mdm_id = self.residential_address_mdm_id

        residential_address_mdm_version = self.residential_address_mdm_version

        residential_address_mdm_schema_version = self.residential_address_mdm_schema_version

        postal_address_mdm_id = self.postal_address_mdm_id

        postal_address_mdm_version = self.postal_address_mdm_version

        postal_address_mdm_schema_version = self.postal_address_mdm_schema_version

        triggered_from_mdm = self.triggered_from_mdm

        send_to_mdm = self.send_to_mdm

        ignore_fields: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.ignore_fields, Unset):
            ignore_fields = self.ignore_fields.to_dict()

        mdm_sync_user = self.mdm_sync_user

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if anniversary_date is not UNSET:
            field_dict["anniversaryDate"] = anniversary_date
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if start_date is not UNSET:
            field_dict["startDate"] = start_date
        if end_date is not UNSET:
            field_dict["endDate"] = end_date
        if business_id is not UNSET:
            field_dict["businessId"] = business_id
        if tax_file_number is not UNSET:
            field_dict["taxFileNumber"] = tax_file_number
        if tax_file_number_masked is not UNSET:
            field_dict["taxFileNumberMasked"] = tax_file_number_masked
        if bank_accounts is not UNSET:
            field_dict["bankAccounts"] = bank_accounts
        if external_reference_id is not UNSET:
            field_dict["externalReferenceId"] = external_reference_id
        if payroll_id is not UNSET:
            field_dict["payrollId"] = payroll_id
        if employee_starter_type is not UNSET:
            field_dict["employeeStarterType"] = employee_starter_type
        if source is not UNSET:
            field_dict["source"] = source
        if tags_string is not UNSET:
            field_dict["tagsString"] = tags_string
        if timesheet_setting is not UNSET:
            field_dict["timesheetSetting"] = timesheet_setting
        if termination_reason is not UNSET:
            field_dict["terminationReason"] = termination_reason
        if portable_long_service_leave_id is not UNSET:
            field_dict["portableLongServiceLeaveId"] = portable_long_service_leave_id
        if include_in_portable_long_service_leave_report is not UNSET:
            field_dict["includeInPortableLongServiceLeaveReport"] = include_in_portable_long_service_leave_report
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
        if legal_name is not UNSET:
            field_dict["legalName"] = legal_name
        if date_of_birth is not UNSET:
            field_dict["dateOfBirth"] = date_of_birth
        if gender is not UNSET:
            field_dict["gender"] = gender
        if residential_street_address is not UNSET:
            field_dict["residentialStreetAddress"] = residential_street_address
        if residential_address_line_2 is not UNSET:
            field_dict["residentialAddressLine2"] = residential_address_line_2
        if residential_suburb_id is not UNSET:
            field_dict["residentialSuburbId"] = residential_suburb_id
        if residential_suburb is not UNSET:
            field_dict["residentialSuburb"] = residential_suburb
        if residential_state is not UNSET:
            field_dict["residentialState"] = residential_state
        if residential_postcode is not UNSET:
            field_dict["residentialPostcode"] = residential_postcode
        if residential_country is not UNSET:
            field_dict["residentialCountry"] = residential_country
        if residential_country_id is not UNSET:
            field_dict["residentialCountryId"] = residential_country_id
        if is_overseas_residential_address is not UNSET:
            field_dict["isOverseasResidentialAddress"] = is_overseas_residential_address
        if residential_address_type is not UNSET:
            field_dict["residentialAddressType"] = residential_address_type
        if residential_block_number is not UNSET:
            field_dict["residentialBlockNumber"] = residential_block_number
        if residential_level_number is not UNSET:
            field_dict["residentialLevelNumber"] = residential_level_number
        if residential_unit_number is not UNSET:
            field_dict["residentialUnitNumber"] = residential_unit_number
        if residential_street_name is not UNSET:
            field_dict["residentialStreetName"] = residential_street_name
        if residential_address_line_3 is not UNSET:
            field_dict["residentialAddressLine3"] = residential_address_line_3
        if postal_street_address is not UNSET:
            field_dict["postalStreetAddress"] = postal_street_address
        if postal_address_line_2 is not UNSET:
            field_dict["postalAddressLine2"] = postal_address_line_2
        if postal_suburb_id is not UNSET:
            field_dict["postalSuburbId"] = postal_suburb_id
        if postal_suburb is not UNSET:
            field_dict["postalSuburb"] = postal_suburb
        if postal_state is not UNSET:
            field_dict["postalState"] = postal_state
        if postal_postcode is not UNSET:
            field_dict["postalPostcode"] = postal_postcode
        if postal_country is not UNSET:
            field_dict["postalCountry"] = postal_country
        if postal_country_id is not UNSET:
            field_dict["postalCountryId"] = postal_country_id
        if is_overseas_postal_address is not UNSET:
            field_dict["isOverseasPostalAddress"] = is_overseas_postal_address
        if postal_address_type is not UNSET:
            field_dict["postalAddressType"] = postal_address_type
        if postal_block_number is not UNSET:
            field_dict["postalBlockNumber"] = postal_block_number
        if postal_level_number is not UNSET:
            field_dict["postalLevelNumber"] = postal_level_number
        if postal_unit_number is not UNSET:
            field_dict["postalUnitNumber"] = postal_unit_number
        if postal_street_name is not UNSET:
            field_dict["postalStreetName"] = postal_street_name
        if postal_address_line_3 is not UNSET:
            field_dict["postalAddressLine3"] = postal_address_line_3
        if is_postal_address_same_as_residential is not UNSET:
            field_dict["isPostalAddressSameAsResidential"] = is_postal_address_same_as_residential
        if email is not UNSET:
            field_dict["email"] = email
        if home_phone is not UNSET:
            field_dict["homePhone"] = home_phone
        if work_phone is not UNSET:
            field_dict["workPhone"] = work_phone
        if mobile_phone is not UNSET:
            field_dict["mobilePhone"] = mobile_phone
        if residential_address_mdm_id is not UNSET:
            field_dict["residentialAddress_MdmId"] = residential_address_mdm_id
        if residential_address_mdm_version is not UNSET:
            field_dict["residentialAddress_MdmVersion"] = residential_address_mdm_version
        if residential_address_mdm_schema_version is not UNSET:
            field_dict["residentialAddress_MdmSchemaVersion"] = residential_address_mdm_schema_version
        if postal_address_mdm_id is not UNSET:
            field_dict["postalAddress_MdmId"] = postal_address_mdm_id
        if postal_address_mdm_version is not UNSET:
            field_dict["postalAddress_MdmVersion"] = postal_address_mdm_version
        if postal_address_mdm_schema_version is not UNSET:
            field_dict["postalAddress_MdmSchemaVersion"] = postal_address_mdm_schema_version
        if triggered_from_mdm is not UNSET:
            field_dict["triggeredFromMdm"] = triggered_from_mdm
        if send_to_mdm is not UNSET:
            field_dict["sendToMdm"] = send_to_mdm
        if ignore_fields is not UNSET:
            field_dict["ignoreFields"] = ignore_fields
        if mdm_sync_user is not UNSET:
            field_dict["mdmSyncUser"] = mdm_sync_user

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.bank_account_edit_model import BankAccountEditModel
        from ..models.employee_partial_edit_model_i_dictionary_string_string import (
            EmployeePartialEditModelIDictionaryStringString,
        )

        d = src_dict.copy()
        id = d.pop("id", UNSET)

        _anniversary_date = d.pop("anniversaryDate", UNSET)
        anniversary_date: Union[Unset, datetime.datetime]
        if isinstance(_anniversary_date, Unset):
            anniversary_date = UNSET
        else:
            anniversary_date = isoparse(_anniversary_date)

        external_id = d.pop("externalId", UNSET)

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

        business_id = d.pop("businessId", UNSET)

        tax_file_number = d.pop("taxFileNumber", UNSET)

        tax_file_number_masked = d.pop("taxFileNumberMasked", UNSET)

        bank_accounts = []
        _bank_accounts = d.pop("bankAccounts", UNSET)
        for bank_accounts_item_data in _bank_accounts or []:
            bank_accounts_item = BankAccountEditModel.from_dict(bank_accounts_item_data)

            bank_accounts.append(bank_accounts_item)

        external_reference_id = d.pop("externalReferenceId", UNSET)

        payroll_id = d.pop("payrollId", UNSET)

        _employee_starter_type = d.pop("employeeStarterType", UNSET)
        employee_starter_type: Union[Unset, EmployeePartialEditModelEmployeeStarterTypeEnum]
        if isinstance(_employee_starter_type, Unset):
            employee_starter_type = UNSET
        else:
            employee_starter_type = EmployeePartialEditModelEmployeeStarterTypeEnum(_employee_starter_type)

        _source = d.pop("source", UNSET)
        source: Union[Unset, EmployeePartialEditModelExternalService]
        if isinstance(_source, Unset):
            source = UNSET
        else:
            source = EmployeePartialEditModelExternalService(_source)

        tags_string = d.pop("tagsString", UNSET)

        _timesheet_setting = d.pop("timesheetSetting", UNSET)
        timesheet_setting: Union[Unset, EmployeePartialEditModelEmployeeTimesheetSetting]
        if isinstance(_timesheet_setting, Unset):
            timesheet_setting = UNSET
        else:
            timesheet_setting = EmployeePartialEditModelEmployeeTimesheetSetting(_timesheet_setting)

        termination_reason = d.pop("terminationReason", UNSET)

        portable_long_service_leave_id = d.pop("portableLongServiceLeaveId", UNSET)

        include_in_portable_long_service_leave_report = d.pop("includeInPortableLongServiceLeaveReport", UNSET)

        title_id = d.pop("titleId", UNSET)

        first_name = d.pop("firstName", UNSET)

        other_name = d.pop("otherName", UNSET)

        middle_name = d.pop("middleName", UNSET)

        surname = d.pop("surname", UNSET)

        previous_surname = d.pop("previousSurname", UNSET)

        legal_name = d.pop("legalName", UNSET)

        _date_of_birth = d.pop("dateOfBirth", UNSET)
        date_of_birth: Union[Unset, datetime.datetime]
        if isinstance(_date_of_birth, Unset):
            date_of_birth = UNSET
        else:
            date_of_birth = isoparse(_date_of_birth)

        gender = d.pop("gender", UNSET)

        residential_street_address = d.pop("residentialStreetAddress", UNSET)

        residential_address_line_2 = d.pop("residentialAddressLine2", UNSET)

        residential_suburb_id = d.pop("residentialSuburbId", UNSET)

        residential_suburb = d.pop("residentialSuburb", UNSET)

        residential_state = d.pop("residentialState", UNSET)

        residential_postcode = d.pop("residentialPostcode", UNSET)

        residential_country = d.pop("residentialCountry", UNSET)

        residential_country_id = d.pop("residentialCountryId", UNSET)

        is_overseas_residential_address = d.pop("isOverseasResidentialAddress", UNSET)

        _residential_address_type = d.pop("residentialAddressType", UNSET)
        residential_address_type: Union[Unset, EmployeePartialEditModelNullableAddressTypeEnum]
        if isinstance(_residential_address_type, Unset):
            residential_address_type = UNSET
        else:
            residential_address_type = EmployeePartialEditModelNullableAddressTypeEnum(_residential_address_type)

        residential_block_number = d.pop("residentialBlockNumber", UNSET)

        residential_level_number = d.pop("residentialLevelNumber", UNSET)

        residential_unit_number = d.pop("residentialUnitNumber", UNSET)

        residential_street_name = d.pop("residentialStreetName", UNSET)

        residential_address_line_3 = d.pop("residentialAddressLine3", UNSET)

        postal_street_address = d.pop("postalStreetAddress", UNSET)

        postal_address_line_2 = d.pop("postalAddressLine2", UNSET)

        postal_suburb_id = d.pop("postalSuburbId", UNSET)

        postal_suburb = d.pop("postalSuburb", UNSET)

        postal_state = d.pop("postalState", UNSET)

        postal_postcode = d.pop("postalPostcode", UNSET)

        postal_country = d.pop("postalCountry", UNSET)

        postal_country_id = d.pop("postalCountryId", UNSET)

        is_overseas_postal_address = d.pop("isOverseasPostalAddress", UNSET)

        _postal_address_type = d.pop("postalAddressType", UNSET)
        postal_address_type: Union[Unset, EmployeePartialEditModelNullableAddressTypeEnum]
        if isinstance(_postal_address_type, Unset):
            postal_address_type = UNSET
        else:
            postal_address_type = EmployeePartialEditModelNullableAddressTypeEnum(_postal_address_type)

        postal_block_number = d.pop("postalBlockNumber", UNSET)

        postal_level_number = d.pop("postalLevelNumber", UNSET)

        postal_unit_number = d.pop("postalUnitNumber", UNSET)

        postal_street_name = d.pop("postalStreetName", UNSET)

        postal_address_line_3 = d.pop("postalAddressLine3", UNSET)

        is_postal_address_same_as_residential = d.pop("isPostalAddressSameAsResidential", UNSET)

        email = d.pop("email", UNSET)

        home_phone = d.pop("homePhone", UNSET)

        work_phone = d.pop("workPhone", UNSET)

        mobile_phone = d.pop("mobilePhone", UNSET)

        residential_address_mdm_id = d.pop("residentialAddress_MdmId", UNSET)

        residential_address_mdm_version = d.pop("residentialAddress_MdmVersion", UNSET)

        residential_address_mdm_schema_version = d.pop("residentialAddress_MdmSchemaVersion", UNSET)

        postal_address_mdm_id = d.pop("postalAddress_MdmId", UNSET)

        postal_address_mdm_version = d.pop("postalAddress_MdmVersion", UNSET)

        postal_address_mdm_schema_version = d.pop("postalAddress_MdmSchemaVersion", UNSET)

        triggered_from_mdm = d.pop("triggeredFromMdm", UNSET)

        send_to_mdm = d.pop("sendToMdm", UNSET)

        _ignore_fields = d.pop("ignoreFields", UNSET)
        ignore_fields: Union[Unset, EmployeePartialEditModelIDictionaryStringString]
        if isinstance(_ignore_fields, Unset):
            ignore_fields = UNSET
        else:
            ignore_fields = EmployeePartialEditModelIDictionaryStringString.from_dict(_ignore_fields)

        mdm_sync_user = d.pop("mdmSyncUser", UNSET)

        employee_partial_edit_model = cls(
            id=id,
            anniversary_date=anniversary_date,
            external_id=external_id,
            start_date=start_date,
            end_date=end_date,
            business_id=business_id,
            tax_file_number=tax_file_number,
            tax_file_number_masked=tax_file_number_masked,
            bank_accounts=bank_accounts,
            external_reference_id=external_reference_id,
            payroll_id=payroll_id,
            employee_starter_type=employee_starter_type,
            source=source,
            tags_string=tags_string,
            timesheet_setting=timesheet_setting,
            termination_reason=termination_reason,
            portable_long_service_leave_id=portable_long_service_leave_id,
            include_in_portable_long_service_leave_report=include_in_portable_long_service_leave_report,
            title_id=title_id,
            first_name=first_name,
            other_name=other_name,
            middle_name=middle_name,
            surname=surname,
            previous_surname=previous_surname,
            legal_name=legal_name,
            date_of_birth=date_of_birth,
            gender=gender,
            residential_street_address=residential_street_address,
            residential_address_line_2=residential_address_line_2,
            residential_suburb_id=residential_suburb_id,
            residential_suburb=residential_suburb,
            residential_state=residential_state,
            residential_postcode=residential_postcode,
            residential_country=residential_country,
            residential_country_id=residential_country_id,
            is_overseas_residential_address=is_overseas_residential_address,
            residential_address_type=residential_address_type,
            residential_block_number=residential_block_number,
            residential_level_number=residential_level_number,
            residential_unit_number=residential_unit_number,
            residential_street_name=residential_street_name,
            residential_address_line_3=residential_address_line_3,
            postal_street_address=postal_street_address,
            postal_address_line_2=postal_address_line_2,
            postal_suburb_id=postal_suburb_id,
            postal_suburb=postal_suburb,
            postal_state=postal_state,
            postal_postcode=postal_postcode,
            postal_country=postal_country,
            postal_country_id=postal_country_id,
            is_overseas_postal_address=is_overseas_postal_address,
            postal_address_type=postal_address_type,
            postal_block_number=postal_block_number,
            postal_level_number=postal_level_number,
            postal_unit_number=postal_unit_number,
            postal_street_name=postal_street_name,
            postal_address_line_3=postal_address_line_3,
            is_postal_address_same_as_residential=is_postal_address_same_as_residential,
            email=email,
            home_phone=home_phone,
            work_phone=work_phone,
            mobile_phone=mobile_phone,
            residential_address_mdm_id=residential_address_mdm_id,
            residential_address_mdm_version=residential_address_mdm_version,
            residential_address_mdm_schema_version=residential_address_mdm_schema_version,
            postal_address_mdm_id=postal_address_mdm_id,
            postal_address_mdm_version=postal_address_mdm_version,
            postal_address_mdm_schema_version=postal_address_mdm_schema_version,
            triggered_from_mdm=triggered_from_mdm,
            send_to_mdm=send_to_mdm,
            ignore_fields=ignore_fields,
            mdm_sync_user=mdm_sync_user,
        )

        employee_partial_edit_model.additional_properties = d
        return employee_partial_edit_model

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
