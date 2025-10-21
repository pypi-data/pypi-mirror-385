import datetime
from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.report_leave_liability_request_model_date_type_enum import ReportLeaveLiabilityRequestModelDateTypeEnum
from ..models.report_leave_liability_request_model_nullable_leave_report_display_enum import (
    ReportLeaveLiabilityRequestModelNullableLeaveReportDisplayEnum,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="ReportLeaveLiabilityRequestModel")


@_attrs_define
class ReportLeaveLiabilityRequestModel:
    """
    Attributes:
        job_id (Union[Unset, str]):  Example: 00000000-0000-0000-0000-000000000000.
        filter_type (Union[Unset, ReportLeaveLiabilityRequestModelDateTypeEnum]):
        location_id (Union[Unset, int]):
        leave_type_id (Union[Unset, int]):
        include_approved_leave (Union[Unset, bool]):
        as_at_date (Union[Unset, datetime.datetime]):
        employing_entity_id (Union[Unset, int]):
        pay_run_id (Union[Unset, int]):
        leave_type_ids (Union[Unset, List[int]]):
        group_by (Union[Unset, ReportLeaveLiabilityRequestModelNullableLeaveReportDisplayEnum]):
    """

    job_id: Union[Unset, str] = UNSET
    filter_type: Union[Unset, ReportLeaveLiabilityRequestModelDateTypeEnum] = UNSET
    location_id: Union[Unset, int] = UNSET
    leave_type_id: Union[Unset, int] = UNSET
    include_approved_leave: Union[Unset, bool] = UNSET
    as_at_date: Union[Unset, datetime.datetime] = UNSET
    employing_entity_id: Union[Unset, int] = UNSET
    pay_run_id: Union[Unset, int] = UNSET
    leave_type_ids: Union[Unset, List[int]] = UNSET
    group_by: Union[Unset, ReportLeaveLiabilityRequestModelNullableLeaveReportDisplayEnum] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        job_id = self.job_id

        filter_type: Union[Unset, str] = UNSET
        if not isinstance(self.filter_type, Unset):
            filter_type = self.filter_type.value

        location_id = self.location_id

        leave_type_id = self.leave_type_id

        include_approved_leave = self.include_approved_leave

        as_at_date: Union[Unset, str] = UNSET
        if not isinstance(self.as_at_date, Unset):
            as_at_date = self.as_at_date.isoformat()

        employing_entity_id = self.employing_entity_id

        pay_run_id = self.pay_run_id

        leave_type_ids: Union[Unset, List[int]] = UNSET
        if not isinstance(self.leave_type_ids, Unset):
            leave_type_ids = self.leave_type_ids

        group_by: Union[Unset, str] = UNSET
        if not isinstance(self.group_by, Unset):
            group_by = self.group_by.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if job_id is not UNSET:
            field_dict["jobId"] = job_id
        if filter_type is not UNSET:
            field_dict["filterType"] = filter_type
        if location_id is not UNSET:
            field_dict["locationId"] = location_id
        if leave_type_id is not UNSET:
            field_dict["leaveTypeId"] = leave_type_id
        if include_approved_leave is not UNSET:
            field_dict["includeApprovedLeave"] = include_approved_leave
        if as_at_date is not UNSET:
            field_dict["asAtDate"] = as_at_date
        if employing_entity_id is not UNSET:
            field_dict["employingEntityId"] = employing_entity_id
        if pay_run_id is not UNSET:
            field_dict["payRunId"] = pay_run_id
        if leave_type_ids is not UNSET:
            field_dict["leaveTypeIds"] = leave_type_ids
        if group_by is not UNSET:
            field_dict["groupBy"] = group_by

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        job_id = d.pop("jobId", UNSET)

        _filter_type = d.pop("filterType", UNSET)
        filter_type: Union[Unset, ReportLeaveLiabilityRequestModelDateTypeEnum]
        if isinstance(_filter_type, Unset):
            filter_type = UNSET
        else:
            filter_type = ReportLeaveLiabilityRequestModelDateTypeEnum(_filter_type)

        location_id = d.pop("locationId", UNSET)

        leave_type_id = d.pop("leaveTypeId", UNSET)

        include_approved_leave = d.pop("includeApprovedLeave", UNSET)

        _as_at_date = d.pop("asAtDate", UNSET)
        as_at_date: Union[Unset, datetime.datetime]
        if isinstance(_as_at_date, Unset):
            as_at_date = UNSET
        else:
            as_at_date = isoparse(_as_at_date)

        employing_entity_id = d.pop("employingEntityId", UNSET)

        pay_run_id = d.pop("payRunId", UNSET)

        leave_type_ids = cast(List[int], d.pop("leaveTypeIds", UNSET))

        _group_by = d.pop("groupBy", UNSET)
        group_by: Union[Unset, ReportLeaveLiabilityRequestModelNullableLeaveReportDisplayEnum]
        if isinstance(_group_by, Unset):
            group_by = UNSET
        else:
            group_by = ReportLeaveLiabilityRequestModelNullableLeaveReportDisplayEnum(_group_by)

        report_leave_liability_request_model = cls(
            job_id=job_id,
            filter_type=filter_type,
            location_id=location_id,
            leave_type_id=leave_type_id,
            include_approved_leave=include_approved_leave,
            as_at_date=as_at_date,
            employing_entity_id=employing_entity_id,
            pay_run_id=pay_run_id,
            leave_type_ids=leave_type_ids,
            group_by=group_by,
        )

        report_leave_liability_request_model.additional_properties = d
        return report_leave_liability_request_model

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
