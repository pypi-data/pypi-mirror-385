import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.ess_employee_details_model_employee_details_edit_mode import (
    EssEmployeeDetailsModelEmployeeDetailsEditMode,
)
from ..models.ess_employee_details_model_employee_timesheet_setting import (
    EssEmployeeDetailsModelEmployeeTimesheetSetting,
)
from ..models.ess_employee_details_model_nullable_address_type_enum import (
    EssEmployeeDetailsModelNullableAddressTypeEnum,
)
from ..models.ess_employee_details_model_termination_reason_enum import EssEmployeeDetailsModelTerminationReasonEnum
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.employee_details_fields import EmployeeDetailsFields
    from ..models.numeric_select_list_item import NumericSelectListItem
    from ..models.select_list_item import SelectListItem
    from ..models.title_view_model import TitleViewModel


T = TypeVar("T", bound="EssEmployeeDetailsModel")


@_attrs_define
class EssEmployeeDetailsModel:
    """
    Attributes:
        timesheets_read_only (Union[Unset, bool]):
        id (Union[Unset, int]):
        title_id (Union[Unset, int]):
        first_name (Union[Unset, str]):
        other_name (Union[Unset, str]):
        middle_name (Union[Unset, str]):
        surname (Union[Unset, str]):
        previous_surname (Union[Unset, str]):
        legal_name (Union[Unset, str]):
        gender (Union[Unset, str]):
        date_of_birth (Union[Unset, datetime.datetime]):
        anniversary_date (Union[Unset, datetime.datetime]):
        external_id (Union[Unset, str]):
        residential_street_address (Union[Unset, str]):
        residential_address_line_2 (Union[Unset, str]):
        residential_suburb_id (Union[Unset, int]):
        residential_suburb (Union[Unset, str]):
        residential_state (Union[Unset, str]):
        residential_postcode (Union[Unset, str]):
        residential_country (Union[Unset, str]):
        residential_country_id (Union[Unset, str]):
        is_overseas_residential_address (Union[Unset, bool]):
        postal_street_address (Union[Unset, str]):
        postal_address_line_2 (Union[Unset, str]):
        postal_suburb_id (Union[Unset, int]):
        postal_suburb (Union[Unset, str]):
        postal_state (Union[Unset, str]):
        postal_postcode (Union[Unset, str]):
        postal_country (Union[Unset, str]):
        postal_country_id (Union[Unset, str]):
        is_overseas_postal_address (Union[Unset, bool]):
        email (Union[Unset, str]):
        home_phone (Union[Unset, str]):
        work_phone (Union[Unset, str]):
        mobile_phone (Union[Unset, str]):
        start_date (Union[Unset, datetime.datetime]):
        end_date (Union[Unset, datetime.datetime]):
        is_terminated (Union[Unset, bool]):
        is_anonymised (Union[Unset, bool]):
        external_reference_id (Union[Unset, str]):
        source (Union[Unset, int]):
        is_postal_address_same_as_residential (Union[Unset, bool]):
        titles (Union[Unset, List['TitleViewModel']]):
        edit_mode (Union[Unset, EssEmployeeDetailsModelEmployeeDetailsEditMode]):
        can_edit (Union[Unset, bool]):
        tags_string (Union[Unset, str]):
        all_tags (Union[Unset, List[str]]):
        timesheet_setting (Union[Unset, EssEmployeeDetailsModelEmployeeTimesheetSetting]):
        can_delete (Union[Unset, bool]):
        has_profile_image (Union[Unset, bool]):
        can_edit_profile_image (Union[Unset, bool]):
        bounced_email (Union[Unset, bool]):
        ird_details_current (Union[Unset, bool]):
        ird_settings_enabled (Union[Unset, bool]):
        has_connected_devices (Union[Unset, bool]):
        address_types (Union[Unset, List['SelectListItem']]):
        residential_address_type (Union[Unset, EssEmployeeDetailsModelNullableAddressTypeEnum]):
        postal_address_type (Union[Unset, EssEmployeeDetailsModelNullableAddressTypeEnum]):
        residential_block_number (Union[Unset, str]):
        postal_block_number (Union[Unset, str]):
        residential_level_number (Union[Unset, str]):
        postal_level_number (Union[Unset, str]):
        residential_unit_number (Union[Unset, str]):
        postal_unit_number (Union[Unset, str]):
        residential_street_name (Union[Unset, str]):
        postal_street_name (Union[Unset, str]):
        residential_address_line_3 (Union[Unset, str]):
        postal_address_line_3 (Union[Unset, str]):
        termination_reason (Union[Unset, EssEmployeeDetailsModelTerminationReasonEnum]):
        termination_description (Union[Unset, str]):
        termination_reasons (Union[Unset, List['NumericSelectListItem']]):
        has_sole_user (Union[Unset, bool]):
        fields (Union[Unset, EmployeeDetailsFields]):
        pending_email_update (Union[Unset, bool]):
        new_email (Union[Unset, str]):
    """

    timesheets_read_only: Union[Unset, bool] = UNSET
    id: Union[Unset, int] = UNSET
    title_id: Union[Unset, int] = UNSET
    first_name: Union[Unset, str] = UNSET
    other_name: Union[Unset, str] = UNSET
    middle_name: Union[Unset, str] = UNSET
    surname: Union[Unset, str] = UNSET
    previous_surname: Union[Unset, str] = UNSET
    legal_name: Union[Unset, str] = UNSET
    gender: Union[Unset, str] = UNSET
    date_of_birth: Union[Unset, datetime.datetime] = UNSET
    anniversary_date: Union[Unset, datetime.datetime] = UNSET
    external_id: Union[Unset, str] = UNSET
    residential_street_address: Union[Unset, str] = UNSET
    residential_address_line_2: Union[Unset, str] = UNSET
    residential_suburb_id: Union[Unset, int] = UNSET
    residential_suburb: Union[Unset, str] = UNSET
    residential_state: Union[Unset, str] = UNSET
    residential_postcode: Union[Unset, str] = UNSET
    residential_country: Union[Unset, str] = UNSET
    residential_country_id: Union[Unset, str] = UNSET
    is_overseas_residential_address: Union[Unset, bool] = UNSET
    postal_street_address: Union[Unset, str] = UNSET
    postal_address_line_2: Union[Unset, str] = UNSET
    postal_suburb_id: Union[Unset, int] = UNSET
    postal_suburb: Union[Unset, str] = UNSET
    postal_state: Union[Unset, str] = UNSET
    postal_postcode: Union[Unset, str] = UNSET
    postal_country: Union[Unset, str] = UNSET
    postal_country_id: Union[Unset, str] = UNSET
    is_overseas_postal_address: Union[Unset, bool] = UNSET
    email: Union[Unset, str] = UNSET
    home_phone: Union[Unset, str] = UNSET
    work_phone: Union[Unset, str] = UNSET
    mobile_phone: Union[Unset, str] = UNSET
    start_date: Union[Unset, datetime.datetime] = UNSET
    end_date: Union[Unset, datetime.datetime] = UNSET
    is_terminated: Union[Unset, bool] = UNSET
    is_anonymised: Union[Unset, bool] = UNSET
    external_reference_id: Union[Unset, str] = UNSET
    source: Union[Unset, int] = UNSET
    is_postal_address_same_as_residential: Union[Unset, bool] = UNSET
    titles: Union[Unset, List["TitleViewModel"]] = UNSET
    edit_mode: Union[Unset, EssEmployeeDetailsModelEmployeeDetailsEditMode] = UNSET
    can_edit: Union[Unset, bool] = UNSET
    tags_string: Union[Unset, str] = UNSET
    all_tags: Union[Unset, List[str]] = UNSET
    timesheet_setting: Union[Unset, EssEmployeeDetailsModelEmployeeTimesheetSetting] = UNSET
    can_delete: Union[Unset, bool] = UNSET
    has_profile_image: Union[Unset, bool] = UNSET
    can_edit_profile_image: Union[Unset, bool] = UNSET
    bounced_email: Union[Unset, bool] = UNSET
    ird_details_current: Union[Unset, bool] = UNSET
    ird_settings_enabled: Union[Unset, bool] = UNSET
    has_connected_devices: Union[Unset, bool] = UNSET
    address_types: Union[Unset, List["SelectListItem"]] = UNSET
    residential_address_type: Union[Unset, EssEmployeeDetailsModelNullableAddressTypeEnum] = UNSET
    postal_address_type: Union[Unset, EssEmployeeDetailsModelNullableAddressTypeEnum] = UNSET
    residential_block_number: Union[Unset, str] = UNSET
    postal_block_number: Union[Unset, str] = UNSET
    residential_level_number: Union[Unset, str] = UNSET
    postal_level_number: Union[Unset, str] = UNSET
    residential_unit_number: Union[Unset, str] = UNSET
    postal_unit_number: Union[Unset, str] = UNSET
    residential_street_name: Union[Unset, str] = UNSET
    postal_street_name: Union[Unset, str] = UNSET
    residential_address_line_3: Union[Unset, str] = UNSET
    postal_address_line_3: Union[Unset, str] = UNSET
    termination_reason: Union[Unset, EssEmployeeDetailsModelTerminationReasonEnum] = UNSET
    termination_description: Union[Unset, str] = UNSET
    termination_reasons: Union[Unset, List["NumericSelectListItem"]] = UNSET
    has_sole_user: Union[Unset, bool] = UNSET
    fields: Union[Unset, "EmployeeDetailsFields"] = UNSET
    pending_email_update: Union[Unset, bool] = UNSET
    new_email: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        timesheets_read_only = self.timesheets_read_only

        id = self.id

        title_id = self.title_id

        first_name = self.first_name

        other_name = self.other_name

        middle_name = self.middle_name

        surname = self.surname

        previous_surname = self.previous_surname

        legal_name = self.legal_name

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

        residential_suburb_id = self.residential_suburb_id

        residential_suburb = self.residential_suburb

        residential_state = self.residential_state

        residential_postcode = self.residential_postcode

        residential_country = self.residential_country

        residential_country_id = self.residential_country_id

        is_overseas_residential_address = self.is_overseas_residential_address

        postal_street_address = self.postal_street_address

        postal_address_line_2 = self.postal_address_line_2

        postal_suburb_id = self.postal_suburb_id

        postal_suburb = self.postal_suburb

        postal_state = self.postal_state

        postal_postcode = self.postal_postcode

        postal_country = self.postal_country

        postal_country_id = self.postal_country_id

        is_overseas_postal_address = self.is_overseas_postal_address

        email = self.email

        home_phone = self.home_phone

        work_phone = self.work_phone

        mobile_phone = self.mobile_phone

        start_date: Union[Unset, str] = UNSET
        if not isinstance(self.start_date, Unset):
            start_date = self.start_date.isoformat()

        end_date: Union[Unset, str] = UNSET
        if not isinstance(self.end_date, Unset):
            end_date = self.end_date.isoformat()

        is_terminated = self.is_terminated

        is_anonymised = self.is_anonymised

        external_reference_id = self.external_reference_id

        source = self.source

        is_postal_address_same_as_residential = self.is_postal_address_same_as_residential

        titles: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.titles, Unset):
            titles = []
            for titles_item_data in self.titles:
                titles_item = titles_item_data.to_dict()
                titles.append(titles_item)

        edit_mode: Union[Unset, str] = UNSET
        if not isinstance(self.edit_mode, Unset):
            edit_mode = self.edit_mode.value

        can_edit = self.can_edit

        tags_string = self.tags_string

        all_tags: Union[Unset, List[str]] = UNSET
        if not isinstance(self.all_tags, Unset):
            all_tags = self.all_tags

        timesheet_setting: Union[Unset, str] = UNSET
        if not isinstance(self.timesheet_setting, Unset):
            timesheet_setting = self.timesheet_setting.value

        can_delete = self.can_delete

        has_profile_image = self.has_profile_image

        can_edit_profile_image = self.can_edit_profile_image

        bounced_email = self.bounced_email

        ird_details_current = self.ird_details_current

        ird_settings_enabled = self.ird_settings_enabled

        has_connected_devices = self.has_connected_devices

        address_types: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.address_types, Unset):
            address_types = []
            for address_types_item_data in self.address_types:
                address_types_item = address_types_item_data.to_dict()
                address_types.append(address_types_item)

        residential_address_type: Union[Unset, str] = UNSET
        if not isinstance(self.residential_address_type, Unset):
            residential_address_type = self.residential_address_type.value

        postal_address_type: Union[Unset, str] = UNSET
        if not isinstance(self.postal_address_type, Unset):
            postal_address_type = self.postal_address_type.value

        residential_block_number = self.residential_block_number

        postal_block_number = self.postal_block_number

        residential_level_number = self.residential_level_number

        postal_level_number = self.postal_level_number

        residential_unit_number = self.residential_unit_number

        postal_unit_number = self.postal_unit_number

        residential_street_name = self.residential_street_name

        postal_street_name = self.postal_street_name

        residential_address_line_3 = self.residential_address_line_3

        postal_address_line_3 = self.postal_address_line_3

        termination_reason: Union[Unset, str] = UNSET
        if not isinstance(self.termination_reason, Unset):
            termination_reason = self.termination_reason.value

        termination_description = self.termination_description

        termination_reasons: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.termination_reasons, Unset):
            termination_reasons = []
            for termination_reasons_item_data in self.termination_reasons:
                termination_reasons_item = termination_reasons_item_data.to_dict()
                termination_reasons.append(termination_reasons_item)

        has_sole_user = self.has_sole_user

        fields: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.fields, Unset):
            fields = self.fields.to_dict()

        pending_email_update = self.pending_email_update

        new_email = self.new_email

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if timesheets_read_only is not UNSET:
            field_dict["timesheetsReadOnly"] = timesheets_read_only
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
        if legal_name is not UNSET:
            field_dict["legalName"] = legal_name
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
        if email is not UNSET:
            field_dict["email"] = email
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
        if is_terminated is not UNSET:
            field_dict["isTerminated"] = is_terminated
        if is_anonymised is not UNSET:
            field_dict["isAnonymised"] = is_anonymised
        if external_reference_id is not UNSET:
            field_dict["externalReferenceId"] = external_reference_id
        if source is not UNSET:
            field_dict["source"] = source
        if is_postal_address_same_as_residential is not UNSET:
            field_dict["isPostalAddressSameAsResidential"] = is_postal_address_same_as_residential
        if titles is not UNSET:
            field_dict["titles"] = titles
        if edit_mode is not UNSET:
            field_dict["editMode"] = edit_mode
        if can_edit is not UNSET:
            field_dict["canEdit"] = can_edit
        if tags_string is not UNSET:
            field_dict["tagsString"] = tags_string
        if all_tags is not UNSET:
            field_dict["allTags"] = all_tags
        if timesheet_setting is not UNSET:
            field_dict["timesheetSetting"] = timesheet_setting
        if can_delete is not UNSET:
            field_dict["canDelete"] = can_delete
        if has_profile_image is not UNSET:
            field_dict["hasProfileImage"] = has_profile_image
        if can_edit_profile_image is not UNSET:
            field_dict["canEditProfileImage"] = can_edit_profile_image
        if bounced_email is not UNSET:
            field_dict["bouncedEmail"] = bounced_email
        if ird_details_current is not UNSET:
            field_dict["irdDetailsCurrent"] = ird_details_current
        if ird_settings_enabled is not UNSET:
            field_dict["irdSettingsEnabled"] = ird_settings_enabled
        if has_connected_devices is not UNSET:
            field_dict["hasConnectedDevices"] = has_connected_devices
        if address_types is not UNSET:
            field_dict["addressTypes"] = address_types
        if residential_address_type is not UNSET:
            field_dict["residentialAddressType"] = residential_address_type
        if postal_address_type is not UNSET:
            field_dict["postalAddressType"] = postal_address_type
        if residential_block_number is not UNSET:
            field_dict["residentialBlockNumber"] = residential_block_number
        if postal_block_number is not UNSET:
            field_dict["postalBlockNumber"] = postal_block_number
        if residential_level_number is not UNSET:
            field_dict["residentialLevelNumber"] = residential_level_number
        if postal_level_number is not UNSET:
            field_dict["postalLevelNumber"] = postal_level_number
        if residential_unit_number is not UNSET:
            field_dict["residentialUnitNumber"] = residential_unit_number
        if postal_unit_number is not UNSET:
            field_dict["postalUnitNumber"] = postal_unit_number
        if residential_street_name is not UNSET:
            field_dict["residentialStreetName"] = residential_street_name
        if postal_street_name is not UNSET:
            field_dict["postalStreetName"] = postal_street_name
        if residential_address_line_3 is not UNSET:
            field_dict["residentialAddressLine3"] = residential_address_line_3
        if postal_address_line_3 is not UNSET:
            field_dict["postalAddressLine3"] = postal_address_line_3
        if termination_reason is not UNSET:
            field_dict["terminationReason"] = termination_reason
        if termination_description is not UNSET:
            field_dict["terminationDescription"] = termination_description
        if termination_reasons is not UNSET:
            field_dict["terminationReasons"] = termination_reasons
        if has_sole_user is not UNSET:
            field_dict["hasSoleUser"] = has_sole_user
        if fields is not UNSET:
            field_dict["fields"] = fields
        if pending_email_update is not UNSET:
            field_dict["pendingEmailUpdate"] = pending_email_update
        if new_email is not UNSET:
            field_dict["newEmail"] = new_email

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.employee_details_fields import EmployeeDetailsFields
        from ..models.numeric_select_list_item import NumericSelectListItem
        from ..models.select_list_item import SelectListItem
        from ..models.title_view_model import TitleViewModel

        d = src_dict.copy()
        timesheets_read_only = d.pop("timesheetsReadOnly", UNSET)

        id = d.pop("id", UNSET)

        title_id = d.pop("titleId", UNSET)

        first_name = d.pop("firstName", UNSET)

        other_name = d.pop("otherName", UNSET)

        middle_name = d.pop("middleName", UNSET)

        surname = d.pop("surname", UNSET)

        previous_surname = d.pop("previousSurname", UNSET)

        legal_name = d.pop("legalName", UNSET)

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

        residential_suburb_id = d.pop("residentialSuburbId", UNSET)

        residential_suburb = d.pop("residentialSuburb", UNSET)

        residential_state = d.pop("residentialState", UNSET)

        residential_postcode = d.pop("residentialPostcode", UNSET)

        residential_country = d.pop("residentialCountry", UNSET)

        residential_country_id = d.pop("residentialCountryId", UNSET)

        is_overseas_residential_address = d.pop("isOverseasResidentialAddress", UNSET)

        postal_street_address = d.pop("postalStreetAddress", UNSET)

        postal_address_line_2 = d.pop("postalAddressLine2", UNSET)

        postal_suburb_id = d.pop("postalSuburbId", UNSET)

        postal_suburb = d.pop("postalSuburb", UNSET)

        postal_state = d.pop("postalState", UNSET)

        postal_postcode = d.pop("postalPostcode", UNSET)

        postal_country = d.pop("postalCountry", UNSET)

        postal_country_id = d.pop("postalCountryId", UNSET)

        is_overseas_postal_address = d.pop("isOverseasPostalAddress", UNSET)

        email = d.pop("email", UNSET)

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

        is_terminated = d.pop("isTerminated", UNSET)

        is_anonymised = d.pop("isAnonymised", UNSET)

        external_reference_id = d.pop("externalReferenceId", UNSET)

        source = d.pop("source", UNSET)

        is_postal_address_same_as_residential = d.pop("isPostalAddressSameAsResidential", UNSET)

        titles = []
        _titles = d.pop("titles", UNSET)
        for titles_item_data in _titles or []:
            titles_item = TitleViewModel.from_dict(titles_item_data)

            titles.append(titles_item)

        _edit_mode = d.pop("editMode", UNSET)
        edit_mode: Union[Unset, EssEmployeeDetailsModelEmployeeDetailsEditMode]
        if isinstance(_edit_mode, Unset):
            edit_mode = UNSET
        else:
            edit_mode = EssEmployeeDetailsModelEmployeeDetailsEditMode(_edit_mode)

        can_edit = d.pop("canEdit", UNSET)

        tags_string = d.pop("tagsString", UNSET)

        all_tags = cast(List[str], d.pop("allTags", UNSET))

        _timesheet_setting = d.pop("timesheetSetting", UNSET)
        timesheet_setting: Union[Unset, EssEmployeeDetailsModelEmployeeTimesheetSetting]
        if isinstance(_timesheet_setting, Unset):
            timesheet_setting = UNSET
        else:
            timesheet_setting = EssEmployeeDetailsModelEmployeeTimesheetSetting(_timesheet_setting)

        can_delete = d.pop("canDelete", UNSET)

        has_profile_image = d.pop("hasProfileImage", UNSET)

        can_edit_profile_image = d.pop("canEditProfileImage", UNSET)

        bounced_email = d.pop("bouncedEmail", UNSET)

        ird_details_current = d.pop("irdDetailsCurrent", UNSET)

        ird_settings_enabled = d.pop("irdSettingsEnabled", UNSET)

        has_connected_devices = d.pop("hasConnectedDevices", UNSET)

        address_types = []
        _address_types = d.pop("addressTypes", UNSET)
        for address_types_item_data in _address_types or []:
            address_types_item = SelectListItem.from_dict(address_types_item_data)

            address_types.append(address_types_item)

        _residential_address_type = d.pop("residentialAddressType", UNSET)
        residential_address_type: Union[Unset, EssEmployeeDetailsModelNullableAddressTypeEnum]
        if isinstance(_residential_address_type, Unset):
            residential_address_type = UNSET
        else:
            residential_address_type = EssEmployeeDetailsModelNullableAddressTypeEnum(_residential_address_type)

        _postal_address_type = d.pop("postalAddressType", UNSET)
        postal_address_type: Union[Unset, EssEmployeeDetailsModelNullableAddressTypeEnum]
        if isinstance(_postal_address_type, Unset):
            postal_address_type = UNSET
        else:
            postal_address_type = EssEmployeeDetailsModelNullableAddressTypeEnum(_postal_address_type)

        residential_block_number = d.pop("residentialBlockNumber", UNSET)

        postal_block_number = d.pop("postalBlockNumber", UNSET)

        residential_level_number = d.pop("residentialLevelNumber", UNSET)

        postal_level_number = d.pop("postalLevelNumber", UNSET)

        residential_unit_number = d.pop("residentialUnitNumber", UNSET)

        postal_unit_number = d.pop("postalUnitNumber", UNSET)

        residential_street_name = d.pop("residentialStreetName", UNSET)

        postal_street_name = d.pop("postalStreetName", UNSET)

        residential_address_line_3 = d.pop("residentialAddressLine3", UNSET)

        postal_address_line_3 = d.pop("postalAddressLine3", UNSET)

        _termination_reason = d.pop("terminationReason", UNSET)
        termination_reason: Union[Unset, EssEmployeeDetailsModelTerminationReasonEnum]
        if isinstance(_termination_reason, Unset):
            termination_reason = UNSET
        else:
            termination_reason = EssEmployeeDetailsModelTerminationReasonEnum(_termination_reason)

        termination_description = d.pop("terminationDescription", UNSET)

        termination_reasons = []
        _termination_reasons = d.pop("terminationReasons", UNSET)
        for termination_reasons_item_data in _termination_reasons or []:
            termination_reasons_item = NumericSelectListItem.from_dict(termination_reasons_item_data)

            termination_reasons.append(termination_reasons_item)

        has_sole_user = d.pop("hasSoleUser", UNSET)

        _fields = d.pop("fields", UNSET)
        fields: Union[Unset, EmployeeDetailsFields]
        if isinstance(_fields, Unset):
            fields = UNSET
        else:
            fields = EmployeeDetailsFields.from_dict(_fields)

        pending_email_update = d.pop("pendingEmailUpdate", UNSET)

        new_email = d.pop("newEmail", UNSET)

        ess_employee_details_model = cls(
            timesheets_read_only=timesheets_read_only,
            id=id,
            title_id=title_id,
            first_name=first_name,
            other_name=other_name,
            middle_name=middle_name,
            surname=surname,
            previous_surname=previous_surname,
            legal_name=legal_name,
            gender=gender,
            date_of_birth=date_of_birth,
            anniversary_date=anniversary_date,
            external_id=external_id,
            residential_street_address=residential_street_address,
            residential_address_line_2=residential_address_line_2,
            residential_suburb_id=residential_suburb_id,
            residential_suburb=residential_suburb,
            residential_state=residential_state,
            residential_postcode=residential_postcode,
            residential_country=residential_country,
            residential_country_id=residential_country_id,
            is_overseas_residential_address=is_overseas_residential_address,
            postal_street_address=postal_street_address,
            postal_address_line_2=postal_address_line_2,
            postal_suburb_id=postal_suburb_id,
            postal_suburb=postal_suburb,
            postal_state=postal_state,
            postal_postcode=postal_postcode,
            postal_country=postal_country,
            postal_country_id=postal_country_id,
            is_overseas_postal_address=is_overseas_postal_address,
            email=email,
            home_phone=home_phone,
            work_phone=work_phone,
            mobile_phone=mobile_phone,
            start_date=start_date,
            end_date=end_date,
            is_terminated=is_terminated,
            is_anonymised=is_anonymised,
            external_reference_id=external_reference_id,
            source=source,
            is_postal_address_same_as_residential=is_postal_address_same_as_residential,
            titles=titles,
            edit_mode=edit_mode,
            can_edit=can_edit,
            tags_string=tags_string,
            all_tags=all_tags,
            timesheet_setting=timesheet_setting,
            can_delete=can_delete,
            has_profile_image=has_profile_image,
            can_edit_profile_image=can_edit_profile_image,
            bounced_email=bounced_email,
            ird_details_current=ird_details_current,
            ird_settings_enabled=ird_settings_enabled,
            has_connected_devices=has_connected_devices,
            address_types=address_types,
            residential_address_type=residential_address_type,
            postal_address_type=postal_address_type,
            residential_block_number=residential_block_number,
            postal_block_number=postal_block_number,
            residential_level_number=residential_level_number,
            postal_level_number=postal_level_number,
            residential_unit_number=residential_unit_number,
            postal_unit_number=postal_unit_number,
            residential_street_name=residential_street_name,
            postal_street_name=postal_street_name,
            residential_address_line_3=residential_address_line_3,
            postal_address_line_3=postal_address_line_3,
            termination_reason=termination_reason,
            termination_description=termination_description,
            termination_reasons=termination_reasons,
            has_sole_user=has_sole_user,
            fields=fields,
            pending_email_update=pending_email_update,
            new_email=new_email,
        )

        ess_employee_details_model.additional_properties = d
        return ess_employee_details_model

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
