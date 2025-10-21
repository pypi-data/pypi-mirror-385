from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.report_access_model_report_access_type import ReportAccessModelReportAccessType
from ..models.report_access_model_report_enum import ReportAccessModelReportEnum
from ..types import UNSET, Unset

T = TypeVar("T", bound="ReportAccessModel")


@_attrs_define
class ReportAccessModel:
    """
    Attributes:
        access_type (Union[Unset, ReportAccessModelReportAccessType]):
        specific_reports (Union[Unset, ReportAccessModelReportEnum]): Comma separated list of ReportEnum.
        no_reporting_restriction (Union[Unset, bool]):
    """

    access_type: Union[Unset, ReportAccessModelReportAccessType] = UNSET
    specific_reports: Union[Unset, ReportAccessModelReportEnum] = UNSET
    no_reporting_restriction: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        access_type: Union[Unset, str] = UNSET
        if not isinstance(self.access_type, Unset):
            access_type = self.access_type.value

        specific_reports: Union[Unset, str] = UNSET
        if not isinstance(self.specific_reports, Unset):
            specific_reports = self.specific_reports.value

        no_reporting_restriction = self.no_reporting_restriction

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if access_type is not UNSET:
            field_dict["accessType"] = access_type
        if specific_reports is not UNSET:
            field_dict["specificReports"] = specific_reports
        if no_reporting_restriction is not UNSET:
            field_dict["noReportingRestriction"] = no_reporting_restriction

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _access_type = d.pop("accessType", UNSET)
        access_type: Union[Unset, ReportAccessModelReportAccessType]
        if isinstance(_access_type, Unset):
            access_type = UNSET
        else:
            access_type = ReportAccessModelReportAccessType(_access_type)

        _specific_reports = d.pop("specificReports", UNSET)
        specific_reports: Union[Unset, ReportAccessModelReportEnum]
        if isinstance(_specific_reports, Unset):
            specific_reports = UNSET
        else:
            specific_reports = ReportAccessModelReportEnum(_specific_reports)

        no_reporting_restriction = d.pop("noReportingRestriction", UNSET)

        report_access_model = cls(
            access_type=access_type,
            specific_reports=specific_reports,
            no_reporting_restriction=no_reporting_restriction,
        )

        report_access_model.additional_properties = d
        return report_access_model

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
