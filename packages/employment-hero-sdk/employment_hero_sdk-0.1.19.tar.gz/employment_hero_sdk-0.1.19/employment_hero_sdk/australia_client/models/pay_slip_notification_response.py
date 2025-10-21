from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.pay_run_warning_result import PayRunWarningResult


T = TypeVar("T", bound="PaySlipNotificationResponse")


@_attrs_define
class PaySlipNotificationResponse:
    """
    Attributes:
        total_email_notifications_sent (Union[Unset, int]):
        total_sms_notifications_sent (Union[Unset, int]):
        errors (Union[Unset, PayRunWarningResult]):
        has_partially_sent_notifications (Union[Unset, bool]):
    """

    total_email_notifications_sent: Union[Unset, int] = UNSET
    total_sms_notifications_sent: Union[Unset, int] = UNSET
    errors: Union[Unset, "PayRunWarningResult"] = UNSET
    has_partially_sent_notifications: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        total_email_notifications_sent = self.total_email_notifications_sent

        total_sms_notifications_sent = self.total_sms_notifications_sent

        errors: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.errors, Unset):
            errors = self.errors.to_dict()

        has_partially_sent_notifications = self.has_partially_sent_notifications

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if total_email_notifications_sent is not UNSET:
            field_dict["totalEmailNotificationsSent"] = total_email_notifications_sent
        if total_sms_notifications_sent is not UNSET:
            field_dict["totalSmsNotificationsSent"] = total_sms_notifications_sent
        if errors is not UNSET:
            field_dict["errors"] = errors
        if has_partially_sent_notifications is not UNSET:
            field_dict["hasPartiallySentNotifications"] = has_partially_sent_notifications

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.pay_run_warning_result import PayRunWarningResult

        d = src_dict.copy()
        total_email_notifications_sent = d.pop("totalEmailNotificationsSent", UNSET)

        total_sms_notifications_sent = d.pop("totalSmsNotificationsSent", UNSET)

        _errors = d.pop("errors", UNSET)
        errors: Union[Unset, PayRunWarningResult]
        if isinstance(_errors, Unset):
            errors = UNSET
        else:
            errors = PayRunWarningResult.from_dict(_errors)

        has_partially_sent_notifications = d.pop("hasPartiallySentNotifications", UNSET)

        pay_slip_notification_response = cls(
            total_email_notifications_sent=total_email_notifications_sent,
            total_sms_notifications_sent=total_sms_notifications_sent,
            errors=errors,
            has_partially_sent_notifications=has_partially_sent_notifications,
        )

        pay_slip_notification_response.additional_properties = d
        return pay_slip_notification_response

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
