import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="EmployeeDocumentModel")


@_attrs_define
class EmployeeDocumentModel:
    """
    Attributes:
        id (Union[Unset, int]):
        friendly_name (Union[Unset, str]):
        date_created (Union[Unset, datetime.datetime]):
        visible (Union[Unset, bool]):
        leave_request_id (Union[Unset, int]):
        timesheet_line_id (Union[Unset, int]):
    """

    id: Union[Unset, int] = UNSET
    friendly_name: Union[Unset, str] = UNSET
    date_created: Union[Unset, datetime.datetime] = UNSET
    visible: Union[Unset, bool] = UNSET
    leave_request_id: Union[Unset, int] = UNSET
    timesheet_line_id: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        friendly_name = self.friendly_name

        date_created: Union[Unset, str] = UNSET
        if not isinstance(self.date_created, Unset):
            date_created = self.date_created.isoformat()

        visible = self.visible

        leave_request_id = self.leave_request_id

        timesheet_line_id = self.timesheet_line_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if friendly_name is not UNSET:
            field_dict["friendlyName"] = friendly_name
        if date_created is not UNSET:
            field_dict["dateCreated"] = date_created
        if visible is not UNSET:
            field_dict["visible"] = visible
        if leave_request_id is not UNSET:
            field_dict["leaveRequestId"] = leave_request_id
        if timesheet_line_id is not UNSET:
            field_dict["timesheetLineId"] = timesheet_line_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        friendly_name = d.pop("friendlyName", UNSET)

        _date_created = d.pop("dateCreated", UNSET)
        date_created: Union[Unset, datetime.datetime]
        if isinstance(_date_created, Unset):
            date_created = UNSET
        else:
            date_created = isoparse(_date_created)

        visible = d.pop("visible", UNSET)

        leave_request_id = d.pop("leaveRequestId", UNSET)

        timesheet_line_id = d.pop("timesheetLineId", UNSET)

        employee_document_model = cls(
            id=id,
            friendly_name=friendly_name,
            date_created=date_created,
            visible=visible,
            leave_request_id=leave_request_id,
            timesheet_line_id=timesheet_line_id,
        )

        employee_document_model.additional_properties = d
        return employee_document_model

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
