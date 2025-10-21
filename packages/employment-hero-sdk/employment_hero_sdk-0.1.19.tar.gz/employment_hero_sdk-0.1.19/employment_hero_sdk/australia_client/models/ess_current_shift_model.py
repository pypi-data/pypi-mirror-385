import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.ess_current_shift_model_time_attendance_status import EssCurrentShiftModelTimeAttendanceStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="EssCurrentShiftModel")


@_attrs_define
class EssCurrentShiftModel:
    """
    Attributes:
        shift_id (Union[Unset, int]):
        clock_on_time_utc (Union[Unset, datetime.datetime]):
        break_start_time_utc (Union[Unset, datetime.datetime]):
        status (Union[Unset, EssCurrentShiftModelTimeAttendanceStatus]):
        long_shift (Union[Unset, bool]):
        is_paid_break (Union[Unset, bool]):
    """

    shift_id: Union[Unset, int] = UNSET
    clock_on_time_utc: Union[Unset, datetime.datetime] = UNSET
    break_start_time_utc: Union[Unset, datetime.datetime] = UNSET
    status: Union[Unset, EssCurrentShiftModelTimeAttendanceStatus] = UNSET
    long_shift: Union[Unset, bool] = UNSET
    is_paid_break: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        shift_id = self.shift_id

        clock_on_time_utc: Union[Unset, str] = UNSET
        if not isinstance(self.clock_on_time_utc, Unset):
            clock_on_time_utc = self.clock_on_time_utc.isoformat()

        break_start_time_utc: Union[Unset, str] = UNSET
        if not isinstance(self.break_start_time_utc, Unset):
            break_start_time_utc = self.break_start_time_utc.isoformat()

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        long_shift = self.long_shift

        is_paid_break = self.is_paid_break

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if shift_id is not UNSET:
            field_dict["shiftId"] = shift_id
        if clock_on_time_utc is not UNSET:
            field_dict["clockOnTimeUtc"] = clock_on_time_utc
        if break_start_time_utc is not UNSET:
            field_dict["breakStartTimeUtc"] = break_start_time_utc
        if status is not UNSET:
            field_dict["status"] = status
        if long_shift is not UNSET:
            field_dict["longShift"] = long_shift
        if is_paid_break is not UNSET:
            field_dict["isPaidBreak"] = is_paid_break

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        shift_id = d.pop("shiftId", UNSET)

        _clock_on_time_utc = d.pop("clockOnTimeUtc", UNSET)
        clock_on_time_utc: Union[Unset, datetime.datetime]
        if isinstance(_clock_on_time_utc, Unset):
            clock_on_time_utc = UNSET
        else:
            clock_on_time_utc = isoparse(_clock_on_time_utc)

        _break_start_time_utc = d.pop("breakStartTimeUtc", UNSET)
        break_start_time_utc: Union[Unset, datetime.datetime]
        if isinstance(_break_start_time_utc, Unset):
            break_start_time_utc = UNSET
        else:
            break_start_time_utc = isoparse(_break_start_time_utc)

        _status = d.pop("status", UNSET)
        status: Union[Unset, EssCurrentShiftModelTimeAttendanceStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = EssCurrentShiftModelTimeAttendanceStatus(_status)

        long_shift = d.pop("longShift", UNSET)

        is_paid_break = d.pop("isPaidBreak", UNSET)

        ess_current_shift_model = cls(
            shift_id=shift_id,
            clock_on_time_utc=clock_on_time_utc,
            break_start_time_utc=break_start_time_utc,
            status=status,
            long_shift=long_shift,
            is_paid_break=is_paid_break,
        )

        ess_current_shift_model.additional_properties = d
        return ess_current_shift_model

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
