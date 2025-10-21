import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="TimeAndAttendanceBreakModel")


@_attrs_define
class TimeAndAttendanceBreakModel:
    """
    Attributes:
        start_time_utc (Union[Unset, datetime.datetime]):
        start_time_local (Union[Unset, datetime.datetime]):
        end_time_utc (Union[Unset, datetime.datetime]):
        end_time_local (Union[Unset, datetime.datetime]):
        is_paid_break (Union[Unset, bool]):
    """

    start_time_utc: Union[Unset, datetime.datetime] = UNSET
    start_time_local: Union[Unset, datetime.datetime] = UNSET
    end_time_utc: Union[Unset, datetime.datetime] = UNSET
    end_time_local: Union[Unset, datetime.datetime] = UNSET
    is_paid_break: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        start_time_utc: Union[Unset, str] = UNSET
        if not isinstance(self.start_time_utc, Unset):
            start_time_utc = self.start_time_utc.isoformat()

        start_time_local: Union[Unset, str] = UNSET
        if not isinstance(self.start_time_local, Unset):
            start_time_local = self.start_time_local.isoformat()

        end_time_utc: Union[Unset, str] = UNSET
        if not isinstance(self.end_time_utc, Unset):
            end_time_utc = self.end_time_utc.isoformat()

        end_time_local: Union[Unset, str] = UNSET
        if not isinstance(self.end_time_local, Unset):
            end_time_local = self.end_time_local.isoformat()

        is_paid_break = self.is_paid_break

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if start_time_utc is not UNSET:
            field_dict["startTimeUtc"] = start_time_utc
        if start_time_local is not UNSET:
            field_dict["startTimeLocal"] = start_time_local
        if end_time_utc is not UNSET:
            field_dict["endTimeUtc"] = end_time_utc
        if end_time_local is not UNSET:
            field_dict["endTimeLocal"] = end_time_local
        if is_paid_break is not UNSET:
            field_dict["isPaidBreak"] = is_paid_break

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _start_time_utc = d.pop("startTimeUtc", UNSET)
        start_time_utc: Union[Unset, datetime.datetime]
        if isinstance(_start_time_utc, Unset):
            start_time_utc = UNSET
        else:
            start_time_utc = isoparse(_start_time_utc)

        _start_time_local = d.pop("startTimeLocal", UNSET)
        start_time_local: Union[Unset, datetime.datetime]
        if isinstance(_start_time_local, Unset):
            start_time_local = UNSET
        else:
            start_time_local = isoparse(_start_time_local)

        _end_time_utc = d.pop("endTimeUtc", UNSET)
        end_time_utc: Union[Unset, datetime.datetime]
        if isinstance(_end_time_utc, Unset):
            end_time_utc = UNSET
        else:
            end_time_utc = isoparse(_end_time_utc)

        _end_time_local = d.pop("endTimeLocal", UNSET)
        end_time_local: Union[Unset, datetime.datetime]
        if isinstance(_end_time_local, Unset):
            end_time_local = UNSET
        else:
            end_time_local = isoparse(_end_time_local)

        is_paid_break = d.pop("isPaidBreak", UNSET)

        time_and_attendance_break_model = cls(
            start_time_utc=start_time_utc,
            start_time_local=start_time_local,
            end_time_utc=end_time_utc,
            end_time_local=end_time_local,
            is_paid_break=is_paid_break,
        )

        time_and_attendance_break_model.additional_properties = d
        return time_and_attendance_break_model

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
