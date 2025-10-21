import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.employee_group_item_model import EmployeeGroupItemModel
    from ..models.location_item_model import LocationItemModel


T = TypeVar("T", bound="DocumentModel")


@_attrs_define
class DocumentModel:
    """
    Attributes:
        id (Union[Unset, int]):
        friendly_name (Union[Unset, str]):
        date_created (Union[Unset, datetime.datetime]):
        visible_to_all_employees (Union[Unset, bool]):
        selected_groups (Union[Unset, List['EmployeeGroupItemModel']]):
        selected_locations (Union[Unset, List['LocationItemModel']]):
        requires_employee_acknowledgement (Union[Unset, bool]):
        send_notification_to_employee (Union[Unset, bool]):
        send_notification_immediately (Union[Unset, bool]):
        send_initial_notification_on (Union[Unset, datetime.datetime]):
        send_reminder_every_x_days (Union[Unset, int]):
    """

    id: Union[Unset, int] = UNSET
    friendly_name: Union[Unset, str] = UNSET
    date_created: Union[Unset, datetime.datetime] = UNSET
    visible_to_all_employees: Union[Unset, bool] = UNSET
    selected_groups: Union[Unset, List["EmployeeGroupItemModel"]] = UNSET
    selected_locations: Union[Unset, List["LocationItemModel"]] = UNSET
    requires_employee_acknowledgement: Union[Unset, bool] = UNSET
    send_notification_to_employee: Union[Unset, bool] = UNSET
    send_notification_immediately: Union[Unset, bool] = UNSET
    send_initial_notification_on: Union[Unset, datetime.datetime] = UNSET
    send_reminder_every_x_days: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        friendly_name = self.friendly_name

        date_created: Union[Unset, str] = UNSET
        if not isinstance(self.date_created, Unset):
            date_created = self.date_created.isoformat()

        visible_to_all_employees = self.visible_to_all_employees

        selected_groups: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.selected_groups, Unset):
            selected_groups = []
            for selected_groups_item_data in self.selected_groups:
                selected_groups_item = selected_groups_item_data.to_dict()
                selected_groups.append(selected_groups_item)

        selected_locations: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.selected_locations, Unset):
            selected_locations = []
            for selected_locations_item_data in self.selected_locations:
                selected_locations_item = selected_locations_item_data.to_dict()
                selected_locations.append(selected_locations_item)

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
        if friendly_name is not UNSET:
            field_dict["friendlyName"] = friendly_name
        if date_created is not UNSET:
            field_dict["dateCreated"] = date_created
        if visible_to_all_employees is not UNSET:
            field_dict["visibleToAllEmployees"] = visible_to_all_employees
        if selected_groups is not UNSET:
            field_dict["selectedGroups"] = selected_groups
        if selected_locations is not UNSET:
            field_dict["selectedLocations"] = selected_locations
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
        from ..models.employee_group_item_model import EmployeeGroupItemModel
        from ..models.location_item_model import LocationItemModel

        d = src_dict.copy()
        id = d.pop("id", UNSET)

        friendly_name = d.pop("friendlyName", UNSET)

        _date_created = d.pop("dateCreated", UNSET)
        date_created: Union[Unset, datetime.datetime]
        if isinstance(_date_created, Unset):
            date_created = UNSET
        else:
            date_created = isoparse(_date_created)

        visible_to_all_employees = d.pop("visibleToAllEmployees", UNSET)

        selected_groups = []
        _selected_groups = d.pop("selectedGroups", UNSET)
        for selected_groups_item_data in _selected_groups or []:
            selected_groups_item = EmployeeGroupItemModel.from_dict(selected_groups_item_data)

            selected_groups.append(selected_groups_item)

        selected_locations = []
        _selected_locations = d.pop("selectedLocations", UNSET)
        for selected_locations_item_data in _selected_locations or []:
            selected_locations_item = LocationItemModel.from_dict(selected_locations_item_data)

            selected_locations.append(selected_locations_item)

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

        document_model = cls(
            id=id,
            friendly_name=friendly_name,
            date_created=date_created,
            visible_to_all_employees=visible_to_all_employees,
            selected_groups=selected_groups,
            selected_locations=selected_locations,
            requires_employee_acknowledgement=requires_employee_acknowledgement,
            send_notification_to_employee=send_notification_to_employee,
            send_notification_immediately=send_notification_immediately,
            send_initial_notification_on=send_initial_notification_on,
            send_reminder_every_x_days=send_reminder_every_x_days,
        )

        document_model.additional_properties = d
        return document_model

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
