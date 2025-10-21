import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="EmployeeDetailsAuditReportApiModel")


@_attrs_define
class EmployeeDetailsAuditReportApiModel:
    """
    Attributes:
        employee_id (Union[Unset, int]):
        first_name (Union[Unset, str]):
        surname (Union[Unset, str]):
        external_id (Union[Unset, str]):
        timestamp_utc (Union[Unset, datetime.datetime]):
        timestamp_local (Union[Unset, datetime.datetime]):
        section (Union[Unset, str]):
        field_name (Union[Unset, str]):
        old_value (Union[Unset, str]):
        new_value (Union[Unset, str]):
        user_name (Union[Unset, str]):
        channel (Union[Unset, str]):
    """

    employee_id: Union[Unset, int] = UNSET
    first_name: Union[Unset, str] = UNSET
    surname: Union[Unset, str] = UNSET
    external_id: Union[Unset, str] = UNSET
    timestamp_utc: Union[Unset, datetime.datetime] = UNSET
    timestamp_local: Union[Unset, datetime.datetime] = UNSET
    section: Union[Unset, str] = UNSET
    field_name: Union[Unset, str] = UNSET
    old_value: Union[Unset, str] = UNSET
    new_value: Union[Unset, str] = UNSET
    user_name: Union[Unset, str] = UNSET
    channel: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        employee_id = self.employee_id

        first_name = self.first_name

        surname = self.surname

        external_id = self.external_id

        timestamp_utc: Union[Unset, str] = UNSET
        if not isinstance(self.timestamp_utc, Unset):
            timestamp_utc = self.timestamp_utc.isoformat()

        timestamp_local: Union[Unset, str] = UNSET
        if not isinstance(self.timestamp_local, Unset):
            timestamp_local = self.timestamp_local.isoformat()

        section = self.section

        field_name = self.field_name

        old_value = self.old_value

        new_value = self.new_value

        user_name = self.user_name

        channel = self.channel

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if first_name is not UNSET:
            field_dict["firstName"] = first_name
        if surname is not UNSET:
            field_dict["surname"] = surname
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if timestamp_utc is not UNSET:
            field_dict["timestampUtc"] = timestamp_utc
        if timestamp_local is not UNSET:
            field_dict["timestampLocal"] = timestamp_local
        if section is not UNSET:
            field_dict["section"] = section
        if field_name is not UNSET:
            field_dict["fieldName"] = field_name
        if old_value is not UNSET:
            field_dict["oldValue"] = old_value
        if new_value is not UNSET:
            field_dict["newValue"] = new_value
        if user_name is not UNSET:
            field_dict["userName"] = user_name
        if channel is not UNSET:
            field_dict["channel"] = channel

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        employee_id = d.pop("employeeId", UNSET)

        first_name = d.pop("firstName", UNSET)

        surname = d.pop("surname", UNSET)

        external_id = d.pop("externalId", UNSET)

        _timestamp_utc = d.pop("timestampUtc", UNSET)
        timestamp_utc: Union[Unset, datetime.datetime]
        if isinstance(_timestamp_utc, Unset):
            timestamp_utc = UNSET
        else:
            timestamp_utc = isoparse(_timestamp_utc)

        _timestamp_local = d.pop("timestampLocal", UNSET)
        timestamp_local: Union[Unset, datetime.datetime]
        if isinstance(_timestamp_local, Unset):
            timestamp_local = UNSET
        else:
            timestamp_local = isoparse(_timestamp_local)

        section = d.pop("section", UNSET)

        field_name = d.pop("fieldName", UNSET)

        old_value = d.pop("oldValue", UNSET)

        new_value = d.pop("newValue", UNSET)

        user_name = d.pop("userName", UNSET)

        channel = d.pop("channel", UNSET)

        employee_details_audit_report_api_model = cls(
            employee_id=employee_id,
            first_name=first_name,
            surname=surname,
            external_id=external_id,
            timestamp_utc=timestamp_utc,
            timestamp_local=timestamp_local,
            section=section,
            field_name=field_name,
            old_value=old_value,
            new_value=new_value,
            user_name=user_name,
            channel=channel,
        )

        employee_details_audit_report_api_model.additional_properties = d
        return employee_details_audit_report_api_model

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
