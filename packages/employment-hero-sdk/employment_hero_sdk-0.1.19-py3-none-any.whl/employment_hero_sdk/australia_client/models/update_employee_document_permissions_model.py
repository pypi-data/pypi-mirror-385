import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateEmployeeDocumentPermissionsModel")


@_attrs_define
class UpdateEmployeeDocumentPermissionsModel:
    """
    Attributes:
        id (Union[Unset, int]):
        visible (Union[Unset, bool]):
        requires_employee_acknowledgement (Union[Unset, bool]):
        send_notification_to_employee (Union[Unset, bool]):
        send_notification_immediately (Union[Unset, bool]):
        send_initial_notification_on (Union[Unset, datetime.datetime]):
        send_reminder_every_x_days (Union[Unset, int]):
    """

    id: Union[Unset, int] = UNSET
    visible: Union[Unset, bool] = UNSET
    requires_employee_acknowledgement: Union[Unset, bool] = UNSET
    send_notification_to_employee: Union[Unset, bool] = UNSET
    send_notification_immediately: Union[Unset, bool] = UNSET
    send_initial_notification_on: Union[Unset, datetime.datetime] = UNSET
    send_reminder_every_x_days: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        visible = self.visible

        requires_employee_acknowledgement = self.requires_employee_acknowledgement

        send_notification_to_employee = self.send_notification_to_employee

        send_notification_immediately = self.send_notification_immediately

        send_initial_notification_on: Union[Unset, str] = UNSET
        if not isinstance(self.send_initial_notification_on, Unset):
            send_initial_notification_on = self.send_initial_notification_on.isoformat()

        send_reminder_every_x_days = self.send_reminder_every_x_days

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if visible is not UNSET:
            field_dict["visible"] = visible
        if requires_employee_acknowledgement is not UNSET:
            field_dict["requiresEmployeeAcknowledgement"] = requires_employee_acknowledgement
        if send_notification_to_employee is not UNSET:
            field_dict["sendNotificationToEmployee"] = send_notification_to_employee
        if send_notification_immediately is not UNSET:
            field_dict["sendNotificationImmediately"] = send_notification_immediately
        if send_initial_notification_on is not UNSET:
            field_dict["sendInitialNotificationOn"] = send_initial_notification_on
        if send_reminder_every_x_days is not UNSET:
            field_dict["sendReminderEveryXDays"] = send_reminder_every_x_days

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        visible = d.pop("visible", UNSET)

        requires_employee_acknowledgement = d.pop("requiresEmployeeAcknowledgement", UNSET)

        send_notification_to_employee = d.pop("sendNotificationToEmployee", UNSET)

        send_notification_immediately = d.pop("sendNotificationImmediately", UNSET)

        _send_initial_notification_on = d.pop("sendInitialNotificationOn", UNSET)
        send_initial_notification_on: Union[Unset, datetime.datetime]
        if isinstance(_send_initial_notification_on, Unset):
            send_initial_notification_on = UNSET
        else:
            send_initial_notification_on = isoparse(_send_initial_notification_on)

        send_reminder_every_x_days = d.pop("sendReminderEveryXDays", UNSET)

        update_employee_document_permissions_model = cls(
            id=id,
            visible=visible,
            requires_employee_acknowledgement=requires_employee_acknowledgement,
            send_notification_to_employee=send_notification_to_employee,
            send_notification_immediately=send_notification_immediately,
            send_initial_notification_on=send_initial_notification_on,
            send_reminder_every_x_days=send_reminder_every_x_days,
        )

        update_employee_document_permissions_model.additional_properties = d
        return update_employee_document_permissions_model

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
