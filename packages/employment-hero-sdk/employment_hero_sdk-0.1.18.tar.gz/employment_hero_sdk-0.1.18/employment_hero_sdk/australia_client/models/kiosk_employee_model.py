import datetime
from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.kiosk_employee_model_time_attendance_status import KioskEmployeeModelTimeAttendanceStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="KioskEmployeeModel")


@_attrs_define
class KioskEmployeeModel:
    """
    Attributes:
        pin_expired (Union[Unset, bool]):
        employee_id (Union[Unset, int]):
        first_name (Union[Unset, str]):
        surname (Union[Unset, str]):
        name (Union[Unset, str]):
        has_email (Union[Unset, bool]):
        profile_image_url (Union[Unset, str]):
        mobile_number (Union[Unset, str]):
        status (Union[Unset, KioskEmployeeModelTimeAttendanceStatus]):
        long_shift (Union[Unset, bool]):
        clock_on_time_utc (Union[Unset, datetime.datetime]):
        break_start_time_utc (Union[Unset, datetime.datetime]):
        recorded_time_utc (Union[Unset, datetime.datetime]):
        current_shift_id (Union[Unset, int]):
        employee_group_ids (Union[Unset, List[int]]):
        employee_start_date (Union[Unset, datetime.datetime]):
    """

    pin_expired: Union[Unset, bool] = UNSET
    employee_id: Union[Unset, int] = UNSET
    first_name: Union[Unset, str] = UNSET
    surname: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    has_email: Union[Unset, bool] = UNSET
    profile_image_url: Union[Unset, str] = UNSET
    mobile_number: Union[Unset, str] = UNSET
    status: Union[Unset, KioskEmployeeModelTimeAttendanceStatus] = UNSET
    long_shift: Union[Unset, bool] = UNSET
    clock_on_time_utc: Union[Unset, datetime.datetime] = UNSET
    break_start_time_utc: Union[Unset, datetime.datetime] = UNSET
    recorded_time_utc: Union[Unset, datetime.datetime] = UNSET
    current_shift_id: Union[Unset, int] = UNSET
    employee_group_ids: Union[Unset, List[int]] = UNSET
    employee_start_date: Union[Unset, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        pin_expired = self.pin_expired

        employee_id = self.employee_id

        first_name = self.first_name

        surname = self.surname

        name = self.name

        has_email = self.has_email

        profile_image_url = self.profile_image_url

        mobile_number = self.mobile_number

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        long_shift = self.long_shift

        clock_on_time_utc: Union[Unset, str] = UNSET
        if not isinstance(self.clock_on_time_utc, Unset):
            clock_on_time_utc = self.clock_on_time_utc.isoformat()

        break_start_time_utc: Union[Unset, str] = UNSET
        if not isinstance(self.break_start_time_utc, Unset):
            break_start_time_utc = self.break_start_time_utc.isoformat()

        recorded_time_utc: Union[Unset, str] = UNSET
        if not isinstance(self.recorded_time_utc, Unset):
            recorded_time_utc = self.recorded_time_utc.isoformat()

        current_shift_id = self.current_shift_id

        employee_group_ids: Union[Unset, List[int]] = UNSET
        if not isinstance(self.employee_group_ids, Unset):
            employee_group_ids = self.employee_group_ids

        employee_start_date: Union[Unset, str] = UNSET
        if not isinstance(self.employee_start_date, Unset):
            employee_start_date = self.employee_start_date.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if pin_expired is not UNSET:
            field_dict["pinExpired"] = pin_expired
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if first_name is not UNSET:
            field_dict["firstName"] = first_name
        if surname is not UNSET:
            field_dict["surname"] = surname
        if name is not UNSET:
            field_dict["name"] = name
        if has_email is not UNSET:
            field_dict["hasEmail"] = has_email
        if profile_image_url is not UNSET:
            field_dict["profileImageUrl"] = profile_image_url
        if mobile_number is not UNSET:
            field_dict["mobileNumber"] = mobile_number
        if status is not UNSET:
            field_dict["status"] = status
        if long_shift is not UNSET:
            field_dict["longShift"] = long_shift
        if clock_on_time_utc is not UNSET:
            field_dict["clockOnTimeUtc"] = clock_on_time_utc
        if break_start_time_utc is not UNSET:
            field_dict["breakStartTimeUtc"] = break_start_time_utc
        if recorded_time_utc is not UNSET:
            field_dict["recordedTimeUtc"] = recorded_time_utc
        if current_shift_id is not UNSET:
            field_dict["currentShiftId"] = current_shift_id
        if employee_group_ids is not UNSET:
            field_dict["employeeGroupIds"] = employee_group_ids
        if employee_start_date is not UNSET:
            field_dict["employeeStartDate"] = employee_start_date

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        pin_expired = d.pop("pinExpired", UNSET)

        employee_id = d.pop("employeeId", UNSET)

        first_name = d.pop("firstName", UNSET)

        surname = d.pop("surname", UNSET)

        name = d.pop("name", UNSET)

        has_email = d.pop("hasEmail", UNSET)

        profile_image_url = d.pop("profileImageUrl", UNSET)

        mobile_number = d.pop("mobileNumber", UNSET)

        _status = d.pop("status", UNSET)
        status: Union[Unset, KioskEmployeeModelTimeAttendanceStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = KioskEmployeeModelTimeAttendanceStatus(_status)

        long_shift = d.pop("longShift", UNSET)

        _clock_on_time_utc = d.pop("clockOnTimeUtc", UNSET)
        clock_on_time_utc: Union[Unset, datetime.datetime]
        if isinstance(_clock_on_time_utc, Unset):
            clock_on_time_utc = UNSET
        else:
            clock_on_time_utc = isoparse(_clock_on_time_utc)

        _break_start_time_utc = d.pop("breakStartTimeUtc", UNSET)
        break_start_time_utc: Union[Unset, datetime.datetime]
        if isinstance(_break_start_time_utc, Unset):
            break_start_time_utc = UNSET
        else:
            break_start_time_utc = isoparse(_break_start_time_utc)

        _recorded_time_utc = d.pop("recordedTimeUtc", UNSET)
        recorded_time_utc: Union[Unset, datetime.datetime]
        if isinstance(_recorded_time_utc, Unset):
            recorded_time_utc = UNSET
        else:
            recorded_time_utc = isoparse(_recorded_time_utc)

        current_shift_id = d.pop("currentShiftId", UNSET)

        employee_group_ids = cast(List[int], d.pop("employeeGroupIds", UNSET))

        _employee_start_date = d.pop("employeeStartDate", UNSET)
        employee_start_date: Union[Unset, datetime.datetime]
        if isinstance(_employee_start_date, Unset):
            employee_start_date = UNSET
        else:
            employee_start_date = isoparse(_employee_start_date)

        kiosk_employee_model = cls(
            pin_expired=pin_expired,
            employee_id=employee_id,
            first_name=first_name,
            surname=surname,
            name=name,
            has_email=has_email,
            profile_image_url=profile_image_url,
            mobile_number=mobile_number,
            status=status,
            long_shift=long_shift,
            clock_on_time_utc=clock_on_time_utc,
            break_start_time_utc=break_start_time_utc,
            recorded_time_utc=recorded_time_utc,
            current_shift_id=current_shift_id,
            employee_group_ids=employee_group_ids,
            employee_start_date=employee_start_date,
        )

        kiosk_employee_model.additional_properties = d
        return kiosk_employee_model

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
