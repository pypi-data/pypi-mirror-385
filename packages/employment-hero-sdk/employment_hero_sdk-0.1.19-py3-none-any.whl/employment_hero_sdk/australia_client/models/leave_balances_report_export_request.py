import datetime
from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.leave_balances_report_export_request_date_type_enum import LeaveBalancesReportExportRequestDateTypeEnum
from ..models.leave_balances_report_export_request_leave_report_display_enum import (
    LeaveBalancesReportExportRequestLeaveReportDisplayEnum,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="LeaveBalancesReportExportRequest")


@_attrs_define
class LeaveBalancesReportExportRequest:
    """
    Attributes:
        filter_type (Union[Unset, LeaveBalancesReportExportRequestDateTypeEnum]):
        as_at_date (Union[Unset, datetime.datetime]):
        pay_run_id (Union[Unset, int]):
        group_by (Union[Unset, LeaveBalancesReportExportRequestLeaveReportDisplayEnum]):
        location_id (Union[Unset, int]):
        leave_type_ids (Union[Unset, List[int]]):
        employing_entity_id (Union[Unset, int]):
        hide_leave_values (Union[Unset, bool]):
    """

    filter_type: Union[Unset, LeaveBalancesReportExportRequestDateTypeEnum] = UNSET
    as_at_date: Union[Unset, datetime.datetime] = UNSET
    pay_run_id: Union[Unset, int] = UNSET
    group_by: Union[Unset, LeaveBalancesReportExportRequestLeaveReportDisplayEnum] = UNSET
    location_id: Union[Unset, int] = UNSET
    leave_type_ids: Union[Unset, List[int]] = UNSET
    employing_entity_id: Union[Unset, int] = UNSET
    hide_leave_values: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        filter_type: Union[Unset, str] = UNSET
        if not isinstance(self.filter_type, Unset):
            filter_type = self.filter_type.value

        as_at_date: Union[Unset, str] = UNSET
        if not isinstance(self.as_at_date, Unset):
            as_at_date = self.as_at_date.isoformat()

        pay_run_id = self.pay_run_id

        group_by: Union[Unset, str] = UNSET
        if not isinstance(self.group_by, Unset):
            group_by = self.group_by.value

        location_id = self.location_id

        leave_type_ids: Union[Unset, List[int]] = UNSET
        if not isinstance(self.leave_type_ids, Unset):
            leave_type_ids = self.leave_type_ids

        employing_entity_id = self.employing_entity_id

        hide_leave_values = self.hide_leave_values

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if filter_type is not UNSET:
            field_dict["filterType"] = filter_type
        if as_at_date is not UNSET:
            field_dict["asAtDate"] = as_at_date
        if pay_run_id is not UNSET:
            field_dict["payRunId"] = pay_run_id
        if group_by is not UNSET:
            field_dict["groupBy"] = group_by
        if location_id is not UNSET:
            field_dict["locationId"] = location_id
        if leave_type_ids is not UNSET:
            field_dict["leaveTypeIds"] = leave_type_ids
        if employing_entity_id is not UNSET:
            field_dict["employingEntityId"] = employing_entity_id
        if hide_leave_values is not UNSET:
            field_dict["hideLeaveValues"] = hide_leave_values

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _filter_type = d.pop("filterType", UNSET)
        filter_type: Union[Unset, LeaveBalancesReportExportRequestDateTypeEnum]
        if isinstance(_filter_type, Unset):
            filter_type = UNSET
        else:
            filter_type = LeaveBalancesReportExportRequestDateTypeEnum(_filter_type)

        _as_at_date = d.pop("asAtDate", UNSET)
        as_at_date: Union[Unset, datetime.datetime]
        if isinstance(_as_at_date, Unset):
            as_at_date = UNSET
        else:
            as_at_date = isoparse(_as_at_date)

        pay_run_id = d.pop("payRunId", UNSET)

        _group_by = d.pop("groupBy", UNSET)
        group_by: Union[Unset, LeaveBalancesReportExportRequestLeaveReportDisplayEnum]
        if isinstance(_group_by, Unset):
            group_by = UNSET
        else:
            group_by = LeaveBalancesReportExportRequestLeaveReportDisplayEnum(_group_by)

        location_id = d.pop("locationId", UNSET)

        leave_type_ids = cast(List[int], d.pop("leaveTypeIds", UNSET))

        employing_entity_id = d.pop("employingEntityId", UNSET)

        hide_leave_values = d.pop("hideLeaveValues", UNSET)

        leave_balances_report_export_request = cls(
            filter_type=filter_type,
            as_at_date=as_at_date,
            pay_run_id=pay_run_id,
            group_by=group_by,
            location_id=location_id,
            leave_type_ids=leave_type_ids,
            employing_entity_id=employing_entity_id,
            hide_leave_values=hide_leave_values,
        )

        leave_balances_report_export_request.additional_properties = d
        return leave_balances_report_export_request

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
