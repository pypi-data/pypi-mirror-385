from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PayScheduleApprovalSettingsModel")


@_attrs_define
class PayScheduleApprovalSettingsModel:
    """
    Attributes:
        require_approval (Union[Unset, bool]):
        reminder_day (Union[Unset, int]):
        notification_template (Union[Unset, str]):
        notification_subject (Union[Unset, str]):
        reminder_template (Union[Unset, str]):
        reminder_subject (Union[Unset, str]):
        send_reminder (Union[Unset, bool]):
        approvers_to_notify (Union[Unset, List[str]]):
    """

    require_approval: Union[Unset, bool] = UNSET
    reminder_day: Union[Unset, int] = UNSET
    notification_template: Union[Unset, str] = UNSET
    notification_subject: Union[Unset, str] = UNSET
    reminder_template: Union[Unset, str] = UNSET
    reminder_subject: Union[Unset, str] = UNSET
    send_reminder: Union[Unset, bool] = UNSET
    approvers_to_notify: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        require_approval = self.require_approval

        reminder_day = self.reminder_day

        notification_template = self.notification_template

        notification_subject = self.notification_subject

        reminder_template = self.reminder_template

        reminder_subject = self.reminder_subject

        send_reminder = self.send_reminder

        approvers_to_notify: Union[Unset, List[str]] = UNSET
        if not isinstance(self.approvers_to_notify, Unset):
            approvers_to_notify = self.approvers_to_notify

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if require_approval is not UNSET:
            field_dict["requireApproval"] = require_approval
        if reminder_day is not UNSET:
            field_dict["reminderDay"] = reminder_day
        if notification_template is not UNSET:
            field_dict["notificationTemplate"] = notification_template
        if notification_subject is not UNSET:
            field_dict["notificationSubject"] = notification_subject
        if reminder_template is not UNSET:
            field_dict["reminderTemplate"] = reminder_template
        if reminder_subject is not UNSET:
            field_dict["reminderSubject"] = reminder_subject
        if send_reminder is not UNSET:
            field_dict["sendReminder"] = send_reminder
        if approvers_to_notify is not UNSET:
            field_dict["approversToNotify"] = approvers_to_notify

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        require_approval = d.pop("requireApproval", UNSET)

        reminder_day = d.pop("reminderDay", UNSET)

        notification_template = d.pop("notificationTemplate", UNSET)

        notification_subject = d.pop("notificationSubject", UNSET)

        reminder_template = d.pop("reminderTemplate", UNSET)

        reminder_subject = d.pop("reminderSubject", UNSET)

        send_reminder = d.pop("sendReminder", UNSET)

        approvers_to_notify = cast(List[str], d.pop("approversToNotify", UNSET))

        pay_schedule_approval_settings_model = cls(
            require_approval=require_approval,
            reminder_day=reminder_day,
            notification_template=notification_template,
            notification_subject=notification_subject,
            reminder_template=reminder_template,
            reminder_subject=reminder_subject,
            send_reminder=send_reminder,
            approvers_to_notify=approvers_to_notify,
        )

        pay_schedule_approval_settings_model.additional_properties = d
        return pay_schedule_approval_settings_model

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
