import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="ShiftSwappingReportExportModel")


@_attrs_define
class ShiftSwappingReportExportModel:
    """
    Attributes:
        from_employee_id (Union[Unset, int]):
        from_employee_name (Union[Unset, str]):
        to_employee_id (Union[Unset, int]):
        to_employee_name (Union[Unset, str]):
        start (Union[Unset, datetime.datetime]):
        start_time (Union[Unset, str]):
        end (Union[Unset, datetime.datetime]):
        end_time (Union[Unset, str]):
        location_id (Union[Unset, str]):
        location (Union[Unset, str]):
        work_type_id (Union[Unset, str]):
        work_type (Union[Unset, str]):
        status (Union[Unset, str]):
        old_cost (Union[Unset, float]):
        new_cost (Union[Unset, float]):
    """

    from_employee_id: Union[Unset, int] = UNSET
    from_employee_name: Union[Unset, str] = UNSET
    to_employee_id: Union[Unset, int] = UNSET
    to_employee_name: Union[Unset, str] = UNSET
    start: Union[Unset, datetime.datetime] = UNSET
    start_time: Union[Unset, str] = UNSET
    end: Union[Unset, datetime.datetime] = UNSET
    end_time: Union[Unset, str] = UNSET
    location_id: Union[Unset, str] = UNSET
    location: Union[Unset, str] = UNSET
    work_type_id: Union[Unset, str] = UNSET
    work_type: Union[Unset, str] = UNSET
    status: Union[Unset, str] = UNSET
    old_cost: Union[Unset, float] = UNSET
    new_cost: Union[Unset, float] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from_employee_id = self.from_employee_id

        from_employee_name = self.from_employee_name

        to_employee_id = self.to_employee_id

        to_employee_name = self.to_employee_name

        start: Union[Unset, str] = UNSET
        if not isinstance(self.start, Unset):
            start = self.start.isoformat()

        start_time = self.start_time

        end: Union[Unset, str] = UNSET
        if not isinstance(self.end, Unset):
            end = self.end.isoformat()

        end_time = self.end_time

        location_id = self.location_id

        location = self.location

        work_type_id = self.work_type_id

        work_type = self.work_type

        status = self.status

        old_cost = self.old_cost

        new_cost = self.new_cost

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if from_employee_id is not UNSET:
            field_dict["fromEmployeeId"] = from_employee_id
        if from_employee_name is not UNSET:
            field_dict["fromEmployeeName"] = from_employee_name
        if to_employee_id is not UNSET:
            field_dict["toEmployeeId"] = to_employee_id
        if to_employee_name is not UNSET:
            field_dict["toEmployeeName"] = to_employee_name
        if start is not UNSET:
            field_dict["start"] = start
        if start_time is not UNSET:
            field_dict["startTime"] = start_time
        if end is not UNSET:
            field_dict["end"] = end
        if end_time is not UNSET:
            field_dict["endTime"] = end_time
        if location_id is not UNSET:
            field_dict["locationId"] = location_id
        if location is not UNSET:
            field_dict["location"] = location
        if work_type_id is not UNSET:
            field_dict["workTypeId"] = work_type_id
        if work_type is not UNSET:
            field_dict["workType"] = work_type
        if status is not UNSET:
            field_dict["status"] = status
        if old_cost is not UNSET:
            field_dict["oldCost"] = old_cost
        if new_cost is not UNSET:
            field_dict["newCost"] = new_cost

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        from_employee_id = d.pop("fromEmployeeId", UNSET)

        from_employee_name = d.pop("fromEmployeeName", UNSET)

        to_employee_id = d.pop("toEmployeeId", UNSET)

        to_employee_name = d.pop("toEmployeeName", UNSET)

        _start = d.pop("start", UNSET)
        start: Union[Unset, datetime.datetime]
        if isinstance(_start, Unset):
            start = UNSET
        else:
            start = isoparse(_start)

        start_time = d.pop("startTime", UNSET)

        _end = d.pop("end", UNSET)
        end: Union[Unset, datetime.datetime]
        if isinstance(_end, Unset):
            end = UNSET
        else:
            end = isoparse(_end)

        end_time = d.pop("endTime", UNSET)

        location_id = d.pop("locationId", UNSET)

        location = d.pop("location", UNSET)

        work_type_id = d.pop("workTypeId", UNSET)

        work_type = d.pop("workType", UNSET)

        status = d.pop("status", UNSET)

        old_cost = d.pop("oldCost", UNSET)

        new_cost = d.pop("newCost", UNSET)

        shift_swapping_report_export_model = cls(
            from_employee_id=from_employee_id,
            from_employee_name=from_employee_name,
            to_employee_id=to_employee_id,
            to_employee_name=to_employee_name,
            start=start,
            start_time=start_time,
            end=end,
            end_time=end_time,
            location_id=location_id,
            location=location,
            work_type_id=work_type_id,
            work_type=work_type,
            status=status,
            old_cost=old_cost,
            new_cost=new_cost,
        )

        shift_swapping_report_export_model.additional_properties = d
        return shift_swapping_report_export_model

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
