from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.standard_hours_day_model_nullable_work_day_type import StandardHoursDayModelNullableWorkDayType
from ..types import UNSET, Unset

T = TypeVar("T", bound="StandardHoursDayModel")


@_attrs_define
class StandardHoursDayModel:
    """
    Attributes:
        id (Union[Unset, int]):
        week (Union[Unset, int]):
        day_of_week (Union[Unset, int]):
        day_name (Union[Unset, str]):
        start_time (Union[Unset, str]):
        end_time (Union[Unset, str]):
        break_start_time (Union[Unset, str]):
        break_end_time (Union[Unset, str]):
        location_id (Union[Unset, int]):
        work_type_id (Union[Unset, int]):
        hours (Union[Unset, float]):
        work_day_type (Union[Unset, StandardHoursDayModelNullableWorkDayType]):
    """

    id: Union[Unset, int] = UNSET
    week: Union[Unset, int] = UNSET
    day_of_week: Union[Unset, int] = UNSET
    day_name: Union[Unset, str] = UNSET
    start_time: Union[Unset, str] = UNSET
    end_time: Union[Unset, str] = UNSET
    break_start_time: Union[Unset, str] = UNSET
    break_end_time: Union[Unset, str] = UNSET
    location_id: Union[Unset, int] = UNSET
    work_type_id: Union[Unset, int] = UNSET
    hours: Union[Unset, float] = UNSET
    work_day_type: Union[Unset, StandardHoursDayModelNullableWorkDayType] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        week = self.week

        day_of_week = self.day_of_week

        day_name = self.day_name

        start_time = self.start_time

        end_time = self.end_time

        break_start_time = self.break_start_time

        break_end_time = self.break_end_time

        location_id = self.location_id

        work_type_id = self.work_type_id

        hours = self.hours

        work_day_type: Union[Unset, str] = UNSET
        if not isinstance(self.work_day_type, Unset):
            work_day_type = self.work_day_type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if week is not UNSET:
            field_dict["week"] = week
        if day_of_week is not UNSET:
            field_dict["dayOfWeek"] = day_of_week
        if day_name is not UNSET:
            field_dict["dayName"] = day_name
        if start_time is not UNSET:
            field_dict["startTime"] = start_time
        if end_time is not UNSET:
            field_dict["endTime"] = end_time
        if break_start_time is not UNSET:
            field_dict["breakStartTime"] = break_start_time
        if break_end_time is not UNSET:
            field_dict["breakEndTime"] = break_end_time
        if location_id is not UNSET:
            field_dict["locationId"] = location_id
        if work_type_id is not UNSET:
            field_dict["workTypeId"] = work_type_id
        if hours is not UNSET:
            field_dict["hours"] = hours
        if work_day_type is not UNSET:
            field_dict["workDayType"] = work_day_type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        week = d.pop("week", UNSET)

        day_of_week = d.pop("dayOfWeek", UNSET)

        day_name = d.pop("dayName", UNSET)

        start_time = d.pop("startTime", UNSET)

        end_time = d.pop("endTime", UNSET)

        break_start_time = d.pop("breakStartTime", UNSET)

        break_end_time = d.pop("breakEndTime", UNSET)

        location_id = d.pop("locationId", UNSET)

        work_type_id = d.pop("workTypeId", UNSET)

        hours = d.pop("hours", UNSET)

        _work_day_type = d.pop("workDayType", UNSET)
        work_day_type: Union[Unset, StandardHoursDayModelNullableWorkDayType]
        if isinstance(_work_day_type, Unset):
            work_day_type = UNSET
        else:
            work_day_type = StandardHoursDayModelNullableWorkDayType(_work_day_type)

        standard_hours_day_model = cls(
            id=id,
            week=week,
            day_of_week=day_of_week,
            day_name=day_name,
            start_time=start_time,
            end_time=end_time,
            break_start_time=break_start_time,
            break_end_time=break_end_time,
            location_id=location_id,
            work_type_id=work_type_id,
            hours=hours,
            work_day_type=work_day_type,
        )

        standard_hours_day_model.additional_properties = d
        return standard_hours_day_model

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
