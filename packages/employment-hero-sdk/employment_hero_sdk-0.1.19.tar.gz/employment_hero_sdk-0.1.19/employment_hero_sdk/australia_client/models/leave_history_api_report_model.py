import datetime
from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="LeaveHistoryApiReportModel")


@_attrs_define
class LeaveHistoryApiReportModel:
    """
    Attributes:
        from_date (Union[Unset, datetime.datetime]):
        to_date (Union[Unset, datetime.datetime]):
        pay_schedule_id (Union[Unset, int]):
        location_id (Union[Unset, int]):
        employee_id (Union[Unset, List[str]]):
        leave_category_id (Union[Unset, int]):
        employing_entity_id (Union[Unset, int]):
    """

    from_date: Union[Unset, datetime.datetime] = UNSET
    to_date: Union[Unset, datetime.datetime] = UNSET
    pay_schedule_id: Union[Unset, int] = UNSET
    location_id: Union[Unset, int] = UNSET
    employee_id: Union[Unset, List[str]] = UNSET
    leave_category_id: Union[Unset, int] = UNSET
    employing_entity_id: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from_date: Union[Unset, str] = UNSET
        if not isinstance(self.from_date, Unset):
            from_date = self.from_date.isoformat()

        to_date: Union[Unset, str] = UNSET
        if not isinstance(self.to_date, Unset):
            to_date = self.to_date.isoformat()

        pay_schedule_id = self.pay_schedule_id

        location_id = self.location_id

        employee_id: Union[Unset, List[str]] = UNSET
        if not isinstance(self.employee_id, Unset):
            employee_id = self.employee_id

        leave_category_id = self.leave_category_id

        employing_entity_id = self.employing_entity_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if from_date is not UNSET:
            field_dict["fromDate"] = from_date
        if to_date is not UNSET:
            field_dict["toDate"] = to_date
        if pay_schedule_id is not UNSET:
            field_dict["payScheduleId"] = pay_schedule_id
        if location_id is not UNSET:
            field_dict["locationId"] = location_id
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if leave_category_id is not UNSET:
            field_dict["leaveCategoryId"] = leave_category_id
        if employing_entity_id is not UNSET:
            field_dict["employingEntityId"] = employing_entity_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
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

        location_id = d.pop("locationId", UNSET)

        employee_id = cast(List[str], d.pop("employeeId", UNSET))

        leave_category_id = d.pop("leaveCategoryId", UNSET)

        employing_entity_id = d.pop("employingEntityId", UNSET)

        leave_history_api_report_model = cls(
            from_date=from_date,
            to_date=to_date,
            pay_schedule_id=pay_schedule_id,
            location_id=location_id,
            employee_id=employee_id,
            leave_category_id=leave_category_id,
            employing_entity_id=employing_entity_id,
        )

        leave_history_api_report_model.additional_properties = d
        return leave_history_api_report_model

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
