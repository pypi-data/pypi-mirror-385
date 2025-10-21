import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="TimesheetBreakViewModel")


@_attrs_define
class TimesheetBreakViewModel:
    """
    Attributes:
        id (Union[Unset, int]):
        start (Union[Unset, datetime.datetime]):
        end (Union[Unset, datetime.datetime]):
        submitted_start (Union[Unset, datetime.datetime]):
        submitted_end (Union[Unset, datetime.datetime]):
        is_paid_break (Union[Unset, bool]):
        formatted_start (Union[Unset, str]):
        formatted_end (Union[Unset, str]):
    """

    id: Union[Unset, int] = UNSET
    start: Union[Unset, datetime.datetime] = UNSET
    end: Union[Unset, datetime.datetime] = UNSET
    submitted_start: Union[Unset, datetime.datetime] = UNSET
    submitted_end: Union[Unset, datetime.datetime] = UNSET
    is_paid_break: Union[Unset, bool] = UNSET
    formatted_start: Union[Unset, str] = UNSET
    formatted_end: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        start: Union[Unset, str] = UNSET
        if not isinstance(self.start, Unset):
            start = self.start.isoformat()

        end: Union[Unset, str] = UNSET
        if not isinstance(self.end, Unset):
            end = self.end.isoformat()

        submitted_start: Union[Unset, str] = UNSET
        if not isinstance(self.submitted_start, Unset):
            submitted_start = self.submitted_start.isoformat()

        submitted_end: Union[Unset, str] = UNSET
        if not isinstance(self.submitted_end, Unset):
            submitted_end = self.submitted_end.isoformat()

        is_paid_break = self.is_paid_break

        formatted_start = self.formatted_start

        formatted_end = self.formatted_end

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if start is not UNSET:
            field_dict["start"] = start
        if end is not UNSET:
            field_dict["end"] = end
        if submitted_start is not UNSET:
            field_dict["submittedStart"] = submitted_start
        if submitted_end is not UNSET:
            field_dict["submittedEnd"] = submitted_end
        if is_paid_break is not UNSET:
            field_dict["isPaidBreak"] = is_paid_break
        if formatted_start is not UNSET:
            field_dict["formattedStart"] = formatted_start
        if formatted_end is not UNSET:
            field_dict["formattedEnd"] = formatted_end

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        _start = d.pop("start", UNSET)
        start: Union[Unset, datetime.datetime]
        if isinstance(_start, Unset):
            start = UNSET
        else:
            start = isoparse(_start)

        _end = d.pop("end", UNSET)
        end: Union[Unset, datetime.datetime]
        if isinstance(_end, Unset):
            end = UNSET
        else:
            end = isoparse(_end)

        _submitted_start = d.pop("submittedStart", UNSET)
        submitted_start: Union[Unset, datetime.datetime]
        if isinstance(_submitted_start, Unset):
            submitted_start = UNSET
        else:
            submitted_start = isoparse(_submitted_start)

        _submitted_end = d.pop("submittedEnd", UNSET)
        submitted_end: Union[Unset, datetime.datetime]
        if isinstance(_submitted_end, Unset):
            submitted_end = UNSET
        else:
            submitted_end = isoparse(_submitted_end)

        is_paid_break = d.pop("isPaidBreak", UNSET)

        formatted_start = d.pop("formattedStart", UNSET)

        formatted_end = d.pop("formattedEnd", UNSET)

        timesheet_break_view_model = cls(
            id=id,
            start=start,
            end=end,
            submitted_start=submitted_start,
            submitted_end=submitted_end,
            is_paid_break=is_paid_break,
            formatted_start=formatted_start,
            formatted_end=formatted_end,
        )

        timesheet_break_view_model.additional_properties = d
        return timesheet_break_view_model

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
