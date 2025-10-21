import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetShiftPeriodsModel")


@_attrs_define
class GetShiftPeriodsModel:
    """
    Attributes:
        first_shift_start_time (Union[Unset, datetime.datetime]):
        last_shift_start_time (Union[Unset, datetime.datetime]):
    """

    first_shift_start_time: Union[Unset, datetime.datetime] = UNSET
    last_shift_start_time: Union[Unset, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        first_shift_start_time: Union[Unset, str] = UNSET
        if not isinstance(self.first_shift_start_time, Unset):
            first_shift_start_time = self.first_shift_start_time.isoformat()

        last_shift_start_time: Union[Unset, str] = UNSET
        if not isinstance(self.last_shift_start_time, Unset):
            last_shift_start_time = self.last_shift_start_time.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if first_shift_start_time is not UNSET:
            field_dict["firstShiftStartTime"] = first_shift_start_time
        if last_shift_start_time is not UNSET:
            field_dict["lastShiftStartTime"] = last_shift_start_time

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _first_shift_start_time = d.pop("firstShiftStartTime", UNSET)
        first_shift_start_time: Union[Unset, datetime.datetime]
        if isinstance(_first_shift_start_time, Unset):
            first_shift_start_time = UNSET
        else:
            first_shift_start_time = isoparse(_first_shift_start_time)

        _last_shift_start_time = d.pop("lastShiftStartTime", UNSET)
        last_shift_start_time: Union[Unset, datetime.datetime]
        if isinstance(_last_shift_start_time, Unset):
            last_shift_start_time = UNSET
        else:
            last_shift_start_time = isoparse(_last_shift_start_time)

        get_shift_periods_model = cls(
            first_shift_start_time=first_shift_start_time,
            last_shift_start_time=last_shift_start_time,
        )

        get_shift_periods_model.additional_properties = d
        return get_shift_periods_model

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
