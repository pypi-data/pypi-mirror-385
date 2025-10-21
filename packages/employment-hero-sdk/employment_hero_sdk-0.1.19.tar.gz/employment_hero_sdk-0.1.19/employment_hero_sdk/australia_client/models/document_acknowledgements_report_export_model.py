import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="DocumentAcknowledgementsReportExportModel")


@_attrs_define
class DocumentAcknowledgementsReportExportModel:
    """
    Attributes:
        status (Union[Unset, str]):
        document_name (Union[Unset, str]):
        employee_id (Union[Unset, int]):
        first_name (Union[Unset, str]):
        surname (Union[Unset, str]):
        external_id (Union[Unset, str]):
        last_notification (Union[Unset, datetime.datetime]):
        location_name (Union[Unset, str]):
    """

    status: Union[Unset, str] = UNSET
    document_name: Union[Unset, str] = UNSET
    employee_id: Union[Unset, int] = UNSET
    first_name: Union[Unset, str] = UNSET
    surname: Union[Unset, str] = UNSET
    external_id: Union[Unset, str] = UNSET
    last_notification: Union[Unset, datetime.datetime] = UNSET
    location_name: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        status = self.status

        document_name = self.document_name

        employee_id = self.employee_id

        first_name = self.first_name

        surname = self.surname

        external_id = self.external_id

        last_notification: Union[Unset, str] = UNSET
        if not isinstance(self.last_notification, Unset):
            last_notification = self.last_notification.isoformat()

        location_name = self.location_name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if status is not UNSET:
            field_dict["status"] = status
        if document_name is not UNSET:
            field_dict["documentName"] = document_name
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if first_name is not UNSET:
            field_dict["firstName"] = first_name
        if surname is not UNSET:
            field_dict["surname"] = surname
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if last_notification is not UNSET:
            field_dict["lastNotification"] = last_notification
        if location_name is not UNSET:
            field_dict["locationName"] = location_name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        status = d.pop("status", UNSET)

        document_name = d.pop("documentName", UNSET)

        employee_id = d.pop("employeeId", UNSET)

        first_name = d.pop("firstName", UNSET)

        surname = d.pop("surname", UNSET)

        external_id = d.pop("externalId", UNSET)

        _last_notification = d.pop("lastNotification", UNSET)
        last_notification: Union[Unset, datetime.datetime]
        if isinstance(_last_notification, Unset):
            last_notification = UNSET
        else:
            last_notification = isoparse(_last_notification)

        location_name = d.pop("locationName", UNSET)

        document_acknowledgements_report_export_model = cls(
            status=status,
            document_name=document_name,
            employee_id=employee_id,
            first_name=first_name,
            surname=surname,
            external_id=external_id,
            last_notification=last_notification,
            location_name=location_name,
        )

        document_acknowledgements_report_export_model.additional_properties = d
        return document_acknowledgements_report_export_model

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
