import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.tasks_report_request_model_tasks_report_status_enum import TasksReportRequestModelTasksReportStatusEnum
from ..types import UNSET, Unset

T = TypeVar("T", bound="TasksReportRequestModel")


@_attrs_define
class TasksReportRequestModel:
    """
    Attributes:
        employee_id (Union[Unset, int]):
        pay_run_id (Union[Unset, int]):
        from_date (Union[Unset, datetime.datetime]):
        to_date (Union[Unset, datetime.datetime]):
        pay_schedule_id (Union[Unset, int]):
        status (Union[Unset, TasksReportRequestModelTasksReportStatusEnum]):
    """

    employee_id: Union[Unset, int] = UNSET
    pay_run_id: Union[Unset, int] = UNSET
    from_date: Union[Unset, datetime.datetime] = UNSET
    to_date: Union[Unset, datetime.datetime] = UNSET
    pay_schedule_id: Union[Unset, int] = UNSET
    status: Union[Unset, TasksReportRequestModelTasksReportStatusEnum] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        employee_id = self.employee_id

        pay_run_id = self.pay_run_id

        from_date: Union[Unset, str] = UNSET
        if not isinstance(self.from_date, Unset):
            from_date = self.from_date.isoformat()

        to_date: Union[Unset, str] = UNSET
        if not isinstance(self.to_date, Unset):
            to_date = self.to_date.isoformat()

        pay_schedule_id = self.pay_schedule_id

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if pay_run_id is not UNSET:
            field_dict["payRunId"] = pay_run_id
        if from_date is not UNSET:
            field_dict["fromDate"] = from_date
        if to_date is not UNSET:
            field_dict["toDate"] = to_date
        if pay_schedule_id is not UNSET:
            field_dict["payScheduleId"] = pay_schedule_id
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        employee_id = d.pop("employeeId", UNSET)

        pay_run_id = d.pop("payRunId", UNSET)

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

        pay_schedule_id = d.pop("payScheduleId", UNSET)

        _status = d.pop("status", UNSET)
        status: Union[Unset, TasksReportRequestModelTasksReportStatusEnum]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = TasksReportRequestModelTasksReportStatusEnum(_status)

        tasks_report_request_model = cls(
            employee_id=employee_id,
            pay_run_id=pay_run_id,
            from_date=from_date,
            to_date=to_date,
            pay_schedule_id=pay_schedule_id,
            status=status,
        )

        tasks_report_request_model.additional_properties = d
        return tasks_report_request_model

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
