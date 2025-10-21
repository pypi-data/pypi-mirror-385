import datetime
from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateDocumentPermissionsModel")


@_attrs_define
class UpdateDocumentPermissionsModel:
    """
    Attributes:
        id (Union[Unset, int]):
        visible_to_all (Union[Unset, bool]):
        employee_groups (Union[Unset, List[int]]):
        locations (Union[Unset, List[int]]):
        requires_employee_acknowledgement (Union[Unset, bool]):
        send_notification_to_employee (Union[Unset, bool]):
        send_notification_immediately (Union[Unset, bool]):
        send_initial_notification_on (Union[Unset, datetime.datetime]):
        send_reminder_every_x_days (Union[Unset, int]):
    """

    id: Union[Unset, int] = UNSET
    visible_to_all: Union[Unset, bool] = UNSET
    employee_groups: Union[Unset, List[int]] = UNSET
    locations: Union[Unset, List[int]] = UNSET
    requires_employee_acknowledgement: Union[Unset, bool] = UNSET
    send_notification_to_employee: Union[Unset, bool] = UNSET
    send_notification_immediately: Union[Unset, bool] = UNSET
    send_initial_notification_on: Union[Unset, datetime.datetime] = UNSET
    send_reminder_every_x_days: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        visible_to_all = self.visible_to_all

        employee_groups: Union[Unset, List[int]] = UNSET
        if not isinstance(self.employee_groups, Unset):
            employee_groups = self.employee_groups

        locations: Union[Unset, List[int]] = UNSET
        if not isinstance(self.locations, Unset):
            locations = self.locations

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
        if visible_to_all is not UNSET:
            field_dict["visibleToAll"] = visible_to_all
        if employee_groups is not UNSET:
            field_dict["employeeGroups"] = employee_groups
        if locations is not UNSET:
            field_dict["locations"] = locations
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

        visible_to_all = d.pop("visibleToAll", UNSET)

        employee_groups = cast(List[int], d.pop("employeeGroups", UNSET))

        locations = cast(List[int], d.pop("locations", UNSET))

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

        update_document_permissions_model = cls(
            id=id,
            visible_to_all=visible_to_all,
            employee_groups=employee_groups,
            locations=locations,
            requires_employee_acknowledgement=requires_employee_acknowledgement,
            send_notification_to_employee=send_notification_to_employee,
            send_notification_immediately=send_notification_immediately,
            send_initial_notification_on=send_initial_notification_on,
            send_reminder_every_x_days=send_reminder_every_x_days,
        )

        update_document_permissions_model.additional_properties = d
        return update_document_permissions_model

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
