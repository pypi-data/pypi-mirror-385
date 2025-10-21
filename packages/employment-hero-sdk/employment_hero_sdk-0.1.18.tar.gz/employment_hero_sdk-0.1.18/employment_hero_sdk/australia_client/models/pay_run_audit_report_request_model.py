from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PayRunAuditReportRequestModel")


@_attrs_define
class PayRunAuditReportRequestModel:
    """
    Attributes:
        single_employee_worksheet (Union[Unset, bool]):
        show_all_summary_details (Union[Unset, bool]):
        show_all_employee_details (Union[Unset, bool]):
    """

    single_employee_worksheet: Union[Unset, bool] = UNSET
    show_all_summary_details: Union[Unset, bool] = UNSET
    show_all_employee_details: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        single_employee_worksheet = self.single_employee_worksheet

        show_all_summary_details = self.show_all_summary_details

        show_all_employee_details = self.show_all_employee_details

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if single_employee_worksheet is not UNSET:
            field_dict["singleEmployeeWorksheet"] = single_employee_worksheet
        if show_all_summary_details is not UNSET:
            field_dict["showAllSummaryDetails"] = show_all_summary_details
        if show_all_employee_details is not UNSET:
            field_dict["showAllEmployeeDetails"] = show_all_employee_details

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        single_employee_worksheet = d.pop("singleEmployeeWorksheet", UNSET)

        show_all_summary_details = d.pop("showAllSummaryDetails", UNSET)

        show_all_employee_details = d.pop("showAllEmployeeDetails", UNSET)

        pay_run_audit_report_request_model = cls(
            single_employee_worksheet=single_employee_worksheet,
            show_all_summary_details=show_all_summary_details,
            show_all_employee_details=show_all_employee_details,
        )

        pay_run_audit_report_request_model.additional_properties = d
        return pay_run_audit_report_request_model

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
