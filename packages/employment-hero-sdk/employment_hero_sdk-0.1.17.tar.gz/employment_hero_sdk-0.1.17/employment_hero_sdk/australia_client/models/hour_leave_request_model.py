import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.attachment_model import AttachmentModel


T = TypeVar("T", bound="HourLeaveRequestModel")


@_attrs_define
class HourLeaveRequestModel:
    """
    Attributes:
        hours (Union[Unset, float]):
        automatically_approve (Union[Unset, bool]):
        employee_id (Union[Unset, int]):
        require_notes_for_leave_requests (Union[Unset, bool]):
        attachment (Union[Unset, AttachmentModel]):
        id (Union[Unset, int]):
        from_date (Union[Unset, datetime.datetime]):
        to_date (Union[Unset, datetime.datetime]):
        leave_category_id (Union[Unset, int]):
        notes (Union[Unset, str]):
    """

    hours: Union[Unset, float] = UNSET
    automatically_approve: Union[Unset, bool] = UNSET
    employee_id: Union[Unset, int] = UNSET
    require_notes_for_leave_requests: Union[Unset, bool] = UNSET
    attachment: Union[Unset, "AttachmentModel"] = UNSET
    id: Union[Unset, int] = UNSET
    from_date: Union[Unset, datetime.datetime] = UNSET
    to_date: Union[Unset, datetime.datetime] = UNSET
    leave_category_id: Union[Unset, int] = UNSET
    notes: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        hours = self.hours

        automatically_approve = self.automatically_approve

        employee_id = self.employee_id

        require_notes_for_leave_requests = self.require_notes_for_leave_requests

        attachment: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.attachment, Unset):
            attachment = self.attachment.to_dict()

        id = self.id

        from_date: Union[Unset, str] = UNSET
        if not isinstance(self.from_date, Unset):
            from_date = self.from_date.isoformat()

        to_date: Union[Unset, str] = UNSET
        if not isinstance(self.to_date, Unset):
            to_date = self.to_date.isoformat()

        leave_category_id = self.leave_category_id

        notes = self.notes

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if hours is not UNSET:
            field_dict["hours"] = hours
        if automatically_approve is not UNSET:
            field_dict["automaticallyApprove"] = automatically_approve
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if require_notes_for_leave_requests is not UNSET:
            field_dict["requireNotesForLeaveRequests"] = require_notes_for_leave_requests
        if attachment is not UNSET:
            field_dict["attachment"] = attachment
        if id is not UNSET:
            field_dict["id"] = id
        if from_date is not UNSET:
            field_dict["fromDate"] = from_date
        if to_date is not UNSET:
            field_dict["toDate"] = to_date
        if leave_category_id is not UNSET:
            field_dict["leaveCategoryId"] = leave_category_id
        if notes is not UNSET:
            field_dict["notes"] = notes

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.attachment_model import AttachmentModel

        d = src_dict.copy()
        hours = d.pop("hours", UNSET)

        automatically_approve = d.pop("automaticallyApprove", UNSET)

        employee_id = d.pop("employeeId", UNSET)

        require_notes_for_leave_requests = d.pop("requireNotesForLeaveRequests", UNSET)

        _attachment = d.pop("attachment", UNSET)
        attachment: Union[Unset, AttachmentModel]
        if isinstance(_attachment, Unset):
            attachment = UNSET
        else:
            attachment = AttachmentModel.from_dict(_attachment)

        id = d.pop("id", UNSET)

        _from_date = d.pop("fromDate", UNSET)
        from_date: Union[Unset, datetime.datetime]
        if isinstance(_from_date, Unset):
            from_date = UNSET
        else:
            from_date = isoparse(_from_date)

        _to_date = d.pop("toDate", UNSET)
        to_date: Union[Unset, datetime.datetime]
        if isinstance(_to_date, Unset):
            to_date = UNSET
        else:
            to_date = isoparse(_to_date)

        leave_category_id = d.pop("leaveCategoryId", UNSET)

        notes = d.pop("notes", UNSET)

        hour_leave_request_model = cls(
            hours=hours,
            automatically_approve=automatically_approve,
            employee_id=employee_id,
            require_notes_for_leave_requests=require_notes_for_leave_requests,
            attachment=attachment,
            id=id,
            from_date=from_date,
            to_date=to_date,
            leave_category_id=leave_category_id,
            notes=notes,
        )

        hour_leave_request_model.additional_properties = d
        return hour_leave_request_model

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
