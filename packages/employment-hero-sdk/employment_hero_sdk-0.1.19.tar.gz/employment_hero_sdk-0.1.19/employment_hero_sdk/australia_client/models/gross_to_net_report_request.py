import datetime
from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.gross_to_net_report_request_nullable_date_type_enum import GrossToNetReportRequestNullableDateTypeEnum
from ..types import UNSET, Unset

T = TypeVar("T", bound="GrossToNetReportRequest")


@_attrs_define
class GrossToNetReportRequest:
    """
    Attributes:
        employee_id (Union[Unset, int]):
        pay_category_ids (Union[Unset, List[int]]):
        group_by (Union[Unset, str]):
        pay_run_id (Union[Unset, int]):
        filter_type (Union[Unset, GrossToNetReportRequestNullableDateTypeEnum]):
        include_expenses (Union[Unset, bool]):
        pay_schedule_id (Union[Unset, int]):
        include_post_tax_deductions (Union[Unset, bool]):
        from_date (Union[Unset, datetime.datetime]):
        to_date (Union[Unset, datetime.datetime]):
        location_id (Union[Unset, int]):
        employing_entity_id (Union[Unset, int]):
    """

    employee_id: Union[Unset, int] = UNSET
    pay_category_ids: Union[Unset, List[int]] = UNSET
    group_by: Union[Unset, str] = UNSET
    pay_run_id: Union[Unset, int] = UNSET
    filter_type: Union[Unset, GrossToNetReportRequestNullableDateTypeEnum] = UNSET
    include_expenses: Union[Unset, bool] = UNSET
    pay_schedule_id: Union[Unset, int] = UNSET
    include_post_tax_deductions: Union[Unset, bool] = UNSET
    from_date: Union[Unset, datetime.datetime] = UNSET
    to_date: Union[Unset, datetime.datetime] = UNSET
    location_id: Union[Unset, int] = UNSET
    employing_entity_id: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        employee_id = self.employee_id

        pay_category_ids: Union[Unset, List[int]] = UNSET
        if not isinstance(self.pay_category_ids, Unset):
            pay_category_ids = self.pay_category_ids

        group_by = self.group_by

        pay_run_id = self.pay_run_id

        filter_type: Union[Unset, str] = UNSET
        if not isinstance(self.filter_type, Unset):
            filter_type = self.filter_type.value

        include_expenses = self.include_expenses

        pay_schedule_id = self.pay_schedule_id

        include_post_tax_deductions = self.include_post_tax_deductions

        from_date: Union[Unset, str] = UNSET
        if not isinstance(self.from_date, Unset):
            from_date = self.from_date.isoformat()

        to_date: Union[Unset, str] = UNSET
        if not isinstance(self.to_date, Unset):
            to_date = self.to_date.isoformat()

        location_id = self.location_id

        employing_entity_id = self.employing_entity_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if pay_category_ids is not UNSET:
            field_dict["payCategoryIds"] = pay_category_ids
        if group_by is not UNSET:
            field_dict["groupBy"] = group_by
        if pay_run_id is not UNSET:
            field_dict["payRunId"] = pay_run_id
        if filter_type is not UNSET:
            field_dict["filterType"] = filter_type
        if include_expenses is not UNSET:
            field_dict["includeExpenses"] = include_expenses
        if pay_schedule_id is not UNSET:
            field_dict["payScheduleId"] = pay_schedule_id
        if include_post_tax_deductions is not UNSET:
            field_dict["includePostTaxDeductions"] = include_post_tax_deductions
        if from_date is not UNSET:
            field_dict["fromDate"] = from_date
        if to_date is not UNSET:
            field_dict["toDate"] = to_date
        if location_id is not UNSET:
            field_dict["locationId"] = location_id
        if employing_entity_id is not UNSET:
            field_dict["employingEntityId"] = employing_entity_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        employee_id = d.pop("employeeId", UNSET)

        pay_category_ids = cast(List[int], d.pop("payCategoryIds", UNSET))

        group_by = d.pop("groupBy", UNSET)

        pay_run_id = d.pop("payRunId", UNSET)

        _filter_type = d.pop("filterType", UNSET)
        filter_type: Union[Unset, GrossToNetReportRequestNullableDateTypeEnum]
        if isinstance(_filter_type, Unset):
            filter_type = UNSET
        else:
            filter_type = GrossToNetReportRequestNullableDateTypeEnum(_filter_type)

        include_expenses = d.pop("includeExpenses", UNSET)

        pay_schedule_id = d.pop("payScheduleId", UNSET)

        include_post_tax_deductions = d.pop("includePostTaxDeductions", UNSET)

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

        location_id = d.pop("locationId", UNSET)

        employing_entity_id = d.pop("employingEntityId", UNSET)

        gross_to_net_report_request = cls(
            employee_id=employee_id,
            pay_category_ids=pay_category_ids,
            group_by=group_by,
            pay_run_id=pay_run_id,
            filter_type=filter_type,
            include_expenses=include_expenses,
            pay_schedule_id=pay_schedule_id,
            include_post_tax_deductions=include_post_tax_deductions,
            from_date=from_date,
            to_date=to_date,
            location_id=location_id,
            employing_entity_id=employing_entity_id,
        )

        gross_to_net_report_request.additional_properties = d
        return gross_to_net_report_request

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
