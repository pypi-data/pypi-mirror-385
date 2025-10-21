from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.white_label_branding_model import WhiteLabelBrandingModel


T = TypeVar("T", bound="AuTimeAndAttendanceKioskModel")


@_attrs_define
class AuTimeAndAttendanceKioskModel:
    """
    Attributes:
        allow_higher_classification_selection (Union[Unset, bool]):
        id (Union[Unset, int]):
        external_id (Union[Unset, str]):
        location_id (Union[Unset, int]):
        name (Union[Unset, str]):
        time_zone (Union[Unset, str]):
        branding (Union[Unset, WhiteLabelBrandingModel]):
        is_location_required (Union[Unset, bool]):
        is_work_type_required (Union[Unset, bool]):
        restrict_locations_for_employees (Union[Unset, bool]):
        allow_employee_shift_selection (Union[Unset, bool]):
        clock_on_window_minutes (Union[Unset, int]):
        clock_off_window_minutes (Union[Unset, int]):
        iana_time_zone (Union[Unset, str]):
        is_photo_required (Union[Unset, bool]):
        can_add_employees (Union[Unset, bool]):
        available_to_all_restricted_users_with_kiosk_access (Union[Unset, bool]):
    """

    allow_higher_classification_selection: Union[Unset, bool] = UNSET
    id: Union[Unset, int] = UNSET
    external_id: Union[Unset, str] = UNSET
    location_id: Union[Unset, int] = UNSET
    name: Union[Unset, str] = UNSET
    time_zone: Union[Unset, str] = UNSET
    branding: Union[Unset, "WhiteLabelBrandingModel"] = UNSET
    is_location_required: Union[Unset, bool] = UNSET
    is_work_type_required: Union[Unset, bool] = UNSET
    restrict_locations_for_employees: Union[Unset, bool] = UNSET
    allow_employee_shift_selection: Union[Unset, bool] = UNSET
    clock_on_window_minutes: Union[Unset, int] = UNSET
    clock_off_window_minutes: Union[Unset, int] = UNSET
    iana_time_zone: Union[Unset, str] = UNSET
    is_photo_required: Union[Unset, bool] = UNSET
    can_add_employees: Union[Unset, bool] = UNSET
    available_to_all_restricted_users_with_kiosk_access: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        allow_higher_classification_selection = self.allow_higher_classification_selection

        id = self.id

        external_id = self.external_id

        location_id = self.location_id

        name = self.name

        time_zone = self.time_zone

        branding: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.branding, Unset):
            branding = self.branding.to_dict()

        is_location_required = self.is_location_required

        is_work_type_required = self.is_work_type_required

        restrict_locations_for_employees = self.restrict_locations_for_employees

        allow_employee_shift_selection = self.allow_employee_shift_selection

        clock_on_window_minutes = self.clock_on_window_minutes

        clock_off_window_minutes = self.clock_off_window_minutes

        iana_time_zone = self.iana_time_zone

        is_photo_required = self.is_photo_required

        can_add_employees = self.can_add_employees

        available_to_all_restricted_users_with_kiosk_access = self.available_to_all_restricted_users_with_kiosk_access

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if allow_higher_classification_selection is not UNSET:
            field_dict["allowHigherClassificationSelection"] = allow_higher_classification_selection
        if id is not UNSET:
            field_dict["id"] = id
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if location_id is not UNSET:
            field_dict["locationId"] = location_id
        if name is not UNSET:
            field_dict["name"] = name
        if time_zone is not UNSET:
            field_dict["timeZone"] = time_zone
        if branding is not UNSET:
            field_dict["branding"] = branding
        if is_location_required is not UNSET:
            field_dict["isLocationRequired"] = is_location_required
        if is_work_type_required is not UNSET:
            field_dict["isWorkTypeRequired"] = is_work_type_required
        if restrict_locations_for_employees is not UNSET:
            field_dict["restrictLocationsForEmployees"] = restrict_locations_for_employees
        if allow_employee_shift_selection is not UNSET:
            field_dict["allowEmployeeShiftSelection"] = allow_employee_shift_selection
        if clock_on_window_minutes is not UNSET:
            field_dict["clockOnWindowMinutes"] = clock_on_window_minutes
        if clock_off_window_minutes is not UNSET:
            field_dict["clockOffWindowMinutes"] = clock_off_window_minutes
        if iana_time_zone is not UNSET:
            field_dict["ianaTimeZone"] = iana_time_zone
        if is_photo_required is not UNSET:
            field_dict["isPhotoRequired"] = is_photo_required
        if can_add_employees is not UNSET:
            field_dict["canAddEmployees"] = can_add_employees
        if available_to_all_restricted_users_with_kiosk_access is not UNSET:
            field_dict["availableToAllRestrictedUsersWithKioskAccess"] = (
                available_to_all_restricted_users_with_kiosk_access
            )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.white_label_branding_model import WhiteLabelBrandingModel

        d = src_dict.copy()
        allow_higher_classification_selection = d.pop("allowHigherClassificationSelection", UNSET)

        id = d.pop("id", UNSET)

        external_id = d.pop("externalId", UNSET)

        location_id = d.pop("locationId", UNSET)

        name = d.pop("name", UNSET)

        time_zone = d.pop("timeZone", UNSET)

        _branding = d.pop("branding", UNSET)
        branding: Union[Unset, WhiteLabelBrandingModel]
        if isinstance(_branding, Unset):
            branding = UNSET
        else:
            branding = WhiteLabelBrandingModel.from_dict(_branding)

        is_location_required = d.pop("isLocationRequired", UNSET)

        is_work_type_required = d.pop("isWorkTypeRequired", UNSET)

        restrict_locations_for_employees = d.pop("restrictLocationsForEmployees", UNSET)

        allow_employee_shift_selection = d.pop("allowEmployeeShiftSelection", UNSET)

        clock_on_window_minutes = d.pop("clockOnWindowMinutes", UNSET)

        clock_off_window_minutes = d.pop("clockOffWindowMinutes", UNSET)

        iana_time_zone = d.pop("ianaTimeZone", UNSET)

        is_photo_required = d.pop("isPhotoRequired", UNSET)

        can_add_employees = d.pop("canAddEmployees", UNSET)

        available_to_all_restricted_users_with_kiosk_access = d.pop(
            "availableToAllRestrictedUsersWithKioskAccess", UNSET
        )

        au_time_and_attendance_kiosk_model = cls(
            allow_higher_classification_selection=allow_higher_classification_selection,
            id=id,
            external_id=external_id,
            location_id=location_id,
            name=name,
            time_zone=time_zone,
            branding=branding,
            is_location_required=is_location_required,
            is_work_type_required=is_work_type_required,
            restrict_locations_for_employees=restrict_locations_for_employees,
            allow_employee_shift_selection=allow_employee_shift_selection,
            clock_on_window_minutes=clock_on_window_minutes,
            clock_off_window_minutes=clock_off_window_minutes,
            iana_time_zone=iana_time_zone,
            is_photo_required=is_photo_required,
            can_add_employees=can_add_employees,
            available_to_all_restricted_users_with_kiosk_access=available_to_all_restricted_users_with_kiosk_access,
        )

        au_time_and_attendance_kiosk_model.additional_properties = d
        return au_time_and_attendance_kiosk_model

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
