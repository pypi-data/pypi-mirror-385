import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.super_contributions_report_request_model_contributions_service_type import (
    SuperContributionsReportRequestModelContributionsServiceType,
)
from ..models.super_contributions_report_request_model_date_type_enum import (
    SuperContributionsReportRequestModelDateTypeEnum,
)
from ..models.super_contributions_report_request_model_nullable_super_contribution_type import (
    SuperContributionsReportRequestModelNullableSuperContributionType,
)
from ..models.super_contributions_report_request_model_super_contributions_report_export_type_enum import (
    SuperContributionsReportRequestModelSuperContributionsReportExportTypeEnum,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="SuperContributionsReportRequestModel")


@_attrs_define
class SuperContributionsReportRequestModel:
    """
    Attributes:
        super_contributions_report_export_type (Union[Unset,
            SuperContributionsReportRequestModelSuperContributionsReportExportTypeEnum]):
        filter_type (Union[Unset, SuperContributionsReportRequestModelDateTypeEnum]):
        super_batch_id (Union[Unset, int]):
        employee_id (Union[Unset, int]):
        contribution_type (Union[Unset, SuperContributionsReportRequestModelNullableSuperContributionType]):
        group_by (Union[Unset, SuperContributionsReportRequestModelContributionsServiceType]):
        fund_per_page (Union[Unset, bool]):
        pay_schedule_id (Union[Unset, int]):
        include_post_tax_deductions (Union[Unset, bool]):
        from_date (Union[Unset, datetime.datetime]):
        to_date (Union[Unset, datetime.datetime]):
        location_id (Union[Unset, int]):
        employing_entity_id (Union[Unset, int]):
    """

    super_contributions_report_export_type: Union[
        Unset, SuperContributionsReportRequestModelSuperContributionsReportExportTypeEnum
    ] = UNSET
    filter_type: Union[Unset, SuperContributionsReportRequestModelDateTypeEnum] = UNSET
    super_batch_id: Union[Unset, int] = UNSET
    employee_id: Union[Unset, int] = UNSET
    contribution_type: Union[Unset, SuperContributionsReportRequestModelNullableSuperContributionType] = UNSET
    group_by: Union[Unset, SuperContributionsReportRequestModelContributionsServiceType] = UNSET
    fund_per_page: Union[Unset, bool] = UNSET
    pay_schedule_id: Union[Unset, int] = UNSET
    include_post_tax_deductions: Union[Unset, bool] = UNSET
    from_date: Union[Unset, datetime.datetime] = UNSET
    to_date: Union[Unset, datetime.datetime] = UNSET
    location_id: Union[Unset, int] = UNSET
    employing_entity_id: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        super_contributions_report_export_type: Union[Unset, str] = UNSET
        if not isinstance(self.super_contributions_report_export_type, Unset):
            super_contributions_report_export_type = self.super_contributions_report_export_type.value

        filter_type: Union[Unset, str] = UNSET
        if not isinstance(self.filter_type, Unset):
            filter_type = self.filter_type.value

        super_batch_id = self.super_batch_id

        employee_id = self.employee_id

        contribution_type: Union[Unset, str] = UNSET
        if not isinstance(self.contribution_type, Unset):
            contribution_type = self.contribution_type.value

        group_by: Union[Unset, str] = UNSET
        if not isinstance(self.group_by, Unset):
            group_by = self.group_by.value

        fund_per_page = self.fund_per_page

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
        if super_contributions_report_export_type is not UNSET:
            field_dict["superContributionsReportExportType"] = super_contributions_report_export_type
        if filter_type is not UNSET:
            field_dict["filterType"] = filter_type
        if super_batch_id is not UNSET:
            field_dict["superBatchId"] = super_batch_id
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if contribution_type is not UNSET:
            field_dict["contributionType"] = contribution_type
        if group_by is not UNSET:
            field_dict["groupBy"] = group_by
        if fund_per_page is not UNSET:
            field_dict["fundPerPage"] = fund_per_page
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
        _super_contributions_report_export_type = d.pop("superContributionsReportExportType", UNSET)
        super_contributions_report_export_type: Union[
            Unset, SuperContributionsReportRequestModelSuperContributionsReportExportTypeEnum
        ]
        if isinstance(_super_contributions_report_export_type, Unset):
            super_contributions_report_export_type = UNSET
        else:
            super_contributions_report_export_type = (
                SuperContributionsReportRequestModelSuperContributionsReportExportTypeEnum(
                    _super_contributions_report_export_type
                )
            )

        _filter_type = d.pop("filterType", UNSET)
        filter_type: Union[Unset, SuperContributionsReportRequestModelDateTypeEnum]
        if isinstance(_filter_type, Unset):
            filter_type = UNSET
        else:
            filter_type = SuperContributionsReportRequestModelDateTypeEnum(_filter_type)

        super_batch_id = d.pop("superBatchId", UNSET)

        employee_id = d.pop("employeeId", UNSET)

        _contribution_type = d.pop("contributionType", UNSET)
        contribution_type: Union[Unset, SuperContributionsReportRequestModelNullableSuperContributionType]
        if isinstance(_contribution_type, Unset):
            contribution_type = UNSET
        else:
            contribution_type = SuperContributionsReportRequestModelNullableSuperContributionType(_contribution_type)

        _group_by = d.pop("groupBy", UNSET)
        group_by: Union[Unset, SuperContributionsReportRequestModelContributionsServiceType]
        if isinstance(_group_by, Unset):
            group_by = UNSET
        else:
            group_by = SuperContributionsReportRequestModelContributionsServiceType(_group_by)

        fund_per_page = d.pop("fundPerPage", UNSET)

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

        super_contributions_report_request_model = cls(
            super_contributions_report_export_type=super_contributions_report_export_type,
            filter_type=filter_type,
            super_batch_id=super_batch_id,
            employee_id=employee_id,
            contribution_type=contribution_type,
            group_by=group_by,
            fund_per_page=fund_per_page,
            pay_schedule_id=pay_schedule_id,
            include_post_tax_deductions=include_post_tax_deductions,
            from_date=from_date,
            to_date=to_date,
            location_id=location_id,
            employing_entity_id=employing_entity_id,
        )

        super_contributions_report_request_model.additional_properties = d
        return super_contributions_report_request_model

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
