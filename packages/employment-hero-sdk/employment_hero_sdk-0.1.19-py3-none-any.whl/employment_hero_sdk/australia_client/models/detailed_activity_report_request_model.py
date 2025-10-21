import datetime
from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.detailed_activity_report_request_model_date_type_enum import (
    DetailedActivityReportRequestModelDateTypeEnum,
)
from ..models.detailed_activity_report_request_model_earnings_report_display_enum import (
    DetailedActivityReportRequestModelEarningsReportDisplayEnum,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="DetailedActivityReportRequestModel")


@_attrs_define
class DetailedActivityReportRequestModel:
    """
    Attributes:
        from_date (Union[Unset, datetime.datetime]):
        to_date (Union[Unset, datetime.datetime]):
        group_by (Union[Unset, DetailedActivityReportRequestModelEarningsReportDisplayEnum]):
        filter_type (Union[Unset, DetailedActivityReportRequestModelDateTypeEnum]):
        pay_run_id (Union[Unset, int]):
        pay_schedule_id (Union[Unset, int]):
        locations_ids (Union[Unset, List[int]]):
        employee_ids (Union[Unset, List[int]]):
        include_post_tax_deductions (Union[Unset, bool]):
        show_location_totals_only (Union[Unset, bool]):
        include_employee_pay_run_breakdown (Union[Unset, bool]):
    """

    from_date: Union[Unset, datetime.datetime] = UNSET
    to_date: Union[Unset, datetime.datetime] = UNSET
    group_by: Union[Unset, DetailedActivityReportRequestModelEarningsReportDisplayEnum] = UNSET
    filter_type: Union[Unset, DetailedActivityReportRequestModelDateTypeEnum] = UNSET
    pay_run_id: Union[Unset, int] = UNSET
    pay_schedule_id: Union[Unset, int] = UNSET
    locations_ids: Union[Unset, List[int]] = UNSET
    employee_ids: Union[Unset, List[int]] = UNSET
    include_post_tax_deductions: Union[Unset, bool] = UNSET
    show_location_totals_only: Union[Unset, bool] = UNSET
    include_employee_pay_run_breakdown: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from_date: Union[Unset, str] = UNSET
        if not isinstance(self.from_date, Unset):
            from_date = self.from_date.isoformat()

        to_date: Union[Unset, str] = UNSET
        if not isinstance(self.to_date, Unset):
            to_date = self.to_date.isoformat()

        group_by: Union[Unset, str] = UNSET
        if not isinstance(self.group_by, Unset):
            group_by = self.group_by.value

        filter_type: Union[Unset, str] = UNSET
        if not isinstance(self.filter_type, Unset):
            filter_type = self.filter_type.value

        pay_run_id = self.pay_run_id

        pay_schedule_id = self.pay_schedule_id

        locations_ids: Union[Unset, List[int]] = UNSET
        if not isinstance(self.locations_ids, Unset):
            locations_ids = self.locations_ids

        employee_ids: Union[Unset, List[int]] = UNSET
        if not isinstance(self.employee_ids, Unset):
            employee_ids = self.employee_ids

        include_post_tax_deductions = self.include_post_tax_deductions

        show_location_totals_only = self.show_location_totals_only

        include_employee_pay_run_breakdown = self.include_employee_pay_run_breakdown

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if from_date is not UNSET:
            field_dict["fromDate"] = from_date
        if to_date is not UNSET:
            field_dict["toDate"] = to_date
        if group_by is not UNSET:
            field_dict["groupBy"] = group_by
        if filter_type is not UNSET:
            field_dict["filterType"] = filter_type
        if pay_run_id is not UNSET:
            field_dict["payRunId"] = pay_run_id
        if pay_schedule_id is not UNSET:
            field_dict["payScheduleId"] = pay_schedule_id
        if locations_ids is not UNSET:
            field_dict["locationsIds"] = locations_ids
        if employee_ids is not UNSET:
            field_dict["employeeIds"] = employee_ids
        if include_post_tax_deductions is not UNSET:
            field_dict["includePostTaxDeductions"] = include_post_tax_deductions
        if show_location_totals_only is not UNSET:
            field_dict["showLocationTotalsOnly"] = show_location_totals_only
        if include_employee_pay_run_breakdown is not UNSET:
            field_dict["includeEmployeePayRunBreakdown"] = include_employee_pay_run_breakdown

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

        _group_by = d.pop("groupBy", UNSET)
        group_by: Union[Unset, DetailedActivityReportRequestModelEarningsReportDisplayEnum]
        if isinstance(_group_by, Unset):
            group_by = UNSET
        else:
            group_by = DetailedActivityReportRequestModelEarningsReportDisplayEnum(_group_by)

        _filter_type = d.pop("filterType", UNSET)
        filter_type: Union[Unset, DetailedActivityReportRequestModelDateTypeEnum]
        if isinstance(_filter_type, Unset):
            filter_type = UNSET
        else:
            filter_type = DetailedActivityReportRequestModelDateTypeEnum(_filter_type)

        pay_run_id = d.pop("payRunId", UNSET)

        pay_schedule_id = d.pop("payScheduleId", UNSET)

        locations_ids = cast(List[int], d.pop("locationsIds", UNSET))

        employee_ids = cast(List[int], d.pop("employeeIds", UNSET))

        include_post_tax_deductions = d.pop("includePostTaxDeductions", UNSET)

        show_location_totals_only = d.pop("showLocationTotalsOnly", UNSET)

        include_employee_pay_run_breakdown = d.pop("includeEmployeePayRunBreakdown", UNSET)

        detailed_activity_report_request_model = cls(
            from_date=from_date,
            to_date=to_date,
            group_by=group_by,
            filter_type=filter_type,
            pay_run_id=pay_run_id,
            pay_schedule_id=pay_schedule_id,
            locations_ids=locations_ids,
            employee_ids=employee_ids,
            include_post_tax_deductions=include_post_tax_deductions,
            show_location_totals_only=show_location_totals_only,
            include_employee_pay_run_breakdown=include_employee_pay_run_breakdown,
        )

        detailed_activity_report_request_model.additional_properties = d
        return detailed_activity_report_request_model

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
