import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.leave_balances_report_request_model_leave_report_display_enum import (
    LeaveBalancesReportRequestModelLeaveReportDisplayEnum,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="LeaveBalancesReportRequestModel")


@_attrs_define
class LeaveBalancesReportRequestModel:
    """
    Attributes:
        location_id (Union[Unset, int]):
        leave_type_id (Union[Unset, int]):
        group_by (Union[Unset, LeaveBalancesReportRequestModelLeaveReportDisplayEnum]):
        employing_entity_id (Union[Unset, int]):
        as_at_date (Union[Unset, datetime.datetime]):
    """

    location_id: Union[Unset, int] = UNSET
    leave_type_id: Union[Unset, int] = UNSET
    group_by: Union[Unset, LeaveBalancesReportRequestModelLeaveReportDisplayEnum] = UNSET
    employing_entity_id: Union[Unset, int] = UNSET
    as_at_date: Union[Unset, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        location_id = self.location_id

        leave_type_id = self.leave_type_id

        group_by: Union[Unset, str] = UNSET
        if not isinstance(self.group_by, Unset):
            group_by = self.group_by.value

        employing_entity_id = self.employing_entity_id

        as_at_date: Union[Unset, str] = UNSET
        if not isinstance(self.as_at_date, Unset):
            as_at_date = self.as_at_date.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if location_id is not UNSET:
            field_dict["locationId"] = location_id
        if leave_type_id is not UNSET:
            field_dict["leaveTypeId"] = leave_type_id
        if group_by is not UNSET:
            field_dict["groupBy"] = group_by
        if employing_entity_id is not UNSET:
            field_dict["employingEntityId"] = employing_entity_id
        if as_at_date is not UNSET:
            field_dict["asAtDate"] = as_at_date

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        location_id = d.pop("locationId", UNSET)

        leave_type_id = d.pop("leaveTypeId", UNSET)

        _group_by = d.pop("groupBy", UNSET)
        group_by: Union[Unset, LeaveBalancesReportRequestModelLeaveReportDisplayEnum]
        if isinstance(_group_by, Unset):
            group_by = UNSET
        else:
            group_by = LeaveBalancesReportRequestModelLeaveReportDisplayEnum(_group_by)

        employing_entity_id = d.pop("employingEntityId", UNSET)

        _as_at_date = d.pop("asAtDate", UNSET)
        as_at_date: Union[Unset, datetime.datetime]
        if isinstance(_as_at_date, Unset):
            as_at_date = UNSET
        else:
            as_at_date = isoparse(_as_at_date)

        leave_balances_report_request_model = cls(
            location_id=location_id,
            leave_type_id=leave_type_id,
            group_by=group_by,
            employing_entity_id=employing_entity_id,
            as_at_date=as_at_date,
        )

        leave_balances_report_request_model.additional_properties = d
        return leave_balances_report_request_model

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
