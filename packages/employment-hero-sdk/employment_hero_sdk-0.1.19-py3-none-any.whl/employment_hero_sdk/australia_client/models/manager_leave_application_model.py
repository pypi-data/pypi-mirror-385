import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="ManagerLeaveApplicationModel")


@_attrs_define
class ManagerLeaveApplicationModel:
    """
    Attributes:
        from_date (datetime.datetime): Required
        to_date (datetime.datetime): Required
        leave_category_id (int): Required
        attachment (Union[Unset, str]):
        attachment_id (Union[Unset, int]):
        filename (Union[Unset, str]):
        hours (Union[Unset, float]):
        units (Union[Unset, float]):
        id (Union[Unset, int]):
        notes (Union[Unset, str]):
    """

    from_date: datetime.datetime
    to_date: datetime.datetime
    leave_category_id: int
    attachment: Union[Unset, str] = UNSET
    attachment_id: Union[Unset, int] = UNSET
    filename: Union[Unset, str] = UNSET
    hours: Union[Unset, float] = UNSET
    units: Union[Unset, float] = UNSET
    id: Union[Unset, int] = UNSET
    notes: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from_date = self.from_date.isoformat()

        to_date = self.to_date.isoformat()

        leave_category_id = self.leave_category_id

        attachment = self.attachment

        attachment_id = self.attachment_id

        filename = self.filename

        hours = self.hours

        units = self.units

        id = self.id

        notes = self.notes

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "fromDate": from_date,
                "toDate": to_date,
                "leaveCategoryId": leave_category_id,
            }
        )
        if attachment is not UNSET:
            field_dict["attachment"] = attachment
        if attachment_id is not UNSET:
            field_dict["attachmentId"] = attachment_id
        if filename is not UNSET:
            field_dict["filename"] = filename
        if hours is not UNSET:
            field_dict["hours"] = hours
        if units is not UNSET:
            field_dict["units"] = units
        if id is not UNSET:
            field_dict["id"] = id
        if notes is not UNSET:
            field_dict["notes"] = notes

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        from_date = isoparse(d.pop("fromDate"))

        to_date = isoparse(d.pop("toDate"))

        leave_category_id = d.pop("leaveCategoryId")

        attachment = d.pop("attachment", UNSET)

        attachment_id = d.pop("attachmentId", UNSET)

        filename = d.pop("filename", UNSET)

        hours = d.pop("hours", UNSET)

        units = d.pop("units", UNSET)

        id = d.pop("id", UNSET)

        notes = d.pop("notes", UNSET)

        manager_leave_application_model = cls(
            from_date=from_date,
            to_date=to_date,
            leave_category_id=leave_category_id,
            attachment=attachment,
            attachment_id=attachment_id,
            filename=filename,
            hours=hours,
            units=units,
            id=id,
            notes=notes,
        )

        manager_leave_application_model.additional_properties = d
        return manager_leave_application_model

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
