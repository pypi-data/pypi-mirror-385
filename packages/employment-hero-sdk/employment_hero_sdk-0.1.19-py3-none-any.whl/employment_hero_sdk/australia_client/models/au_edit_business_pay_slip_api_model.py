from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.au_edit_business_pay_slip_api_model_pay_slip_super_contribution_processing_frequency_text_option import (
    AuEditBusinessPaySlipApiModelPaySlipSuperContributionProcessingFrequencyTextOption,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="AuEditBusinessPaySlipApiModel")


@_attrs_define
class AuEditBusinessPaySlipApiModel:
    """
    Attributes:
        super_contribution_processing_frequency_text_option (Union[Unset,
            AuEditBusinessPaySlipApiModelPaySlipSuperContributionProcessingFrequencyTextOption]):
        show_classification (Union[Unset, bool]):
        show_base_pay_rate (Union[Unset, bool]):
        show_employee_id (Union[Unset, bool]):
        show_rate_for_annual_earnings (Union[Unset, bool]):
        id (Union[Unset, int]):
        email_from (Union[Unset, str]):
        email_body_message (Union[Unset, str]):
        show_leave_accruals (Union[Unset, bool]):
        show_line_notes (Union[Unset, bool]):
        show_location_in_line_notes (Union[Unset, bool]):
        alphabetise_pay_categories (Union[Unset, bool]):
        show_employee_external_id (Union[Unset, bool]):
        employees_must_login_to_download_payslips (Union[Unset, bool]):
    """

    super_contribution_processing_frequency_text_option: Union[
        Unset, AuEditBusinessPaySlipApiModelPaySlipSuperContributionProcessingFrequencyTextOption
    ] = UNSET
    show_classification: Union[Unset, bool] = UNSET
    show_base_pay_rate: Union[Unset, bool] = UNSET
    show_employee_id: Union[Unset, bool] = UNSET
    show_rate_for_annual_earnings: Union[Unset, bool] = UNSET
    id: Union[Unset, int] = UNSET
    email_from: Union[Unset, str] = UNSET
    email_body_message: Union[Unset, str] = UNSET
    show_leave_accruals: Union[Unset, bool] = UNSET
    show_line_notes: Union[Unset, bool] = UNSET
    show_location_in_line_notes: Union[Unset, bool] = UNSET
    alphabetise_pay_categories: Union[Unset, bool] = UNSET
    show_employee_external_id: Union[Unset, bool] = UNSET
    employees_must_login_to_download_payslips: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        super_contribution_processing_frequency_text_option: Union[Unset, str] = UNSET
        if not isinstance(self.super_contribution_processing_frequency_text_option, Unset):
            super_contribution_processing_frequency_text_option = (
                self.super_contribution_processing_frequency_text_option.value
            )

        show_classification = self.show_classification

        show_base_pay_rate = self.show_base_pay_rate

        show_employee_id = self.show_employee_id

        show_rate_for_annual_earnings = self.show_rate_for_annual_earnings

        id = self.id

        email_from = self.email_from

        email_body_message = self.email_body_message

        show_leave_accruals = self.show_leave_accruals

        show_line_notes = self.show_line_notes

        show_location_in_line_notes = self.show_location_in_line_notes

        alphabetise_pay_categories = self.alphabetise_pay_categories

        show_employee_external_id = self.show_employee_external_id

        employees_must_login_to_download_payslips = self.employees_must_login_to_download_payslips

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if super_contribution_processing_frequency_text_option is not UNSET:
            field_dict["superContributionProcessingFrequencyTextOption"] = (
                super_contribution_processing_frequency_text_option
            )
        if show_classification is not UNSET:
            field_dict["showClassification"] = show_classification
        if show_base_pay_rate is not UNSET:
            field_dict["showBasePayRate"] = show_base_pay_rate
        if show_employee_id is not UNSET:
            field_dict["showEmployeeId"] = show_employee_id
        if show_rate_for_annual_earnings is not UNSET:
            field_dict["showRateForAnnualEarnings"] = show_rate_for_annual_earnings
        if id is not UNSET:
            field_dict["id"] = id
        if email_from is not UNSET:
            field_dict["emailFrom"] = email_from
        if email_body_message is not UNSET:
            field_dict["emailBodyMessage"] = email_body_message
        if show_leave_accruals is not UNSET:
            field_dict["showLeaveAccruals"] = show_leave_accruals
        if show_line_notes is not UNSET:
            field_dict["showLineNotes"] = show_line_notes
        if show_location_in_line_notes is not UNSET:
            field_dict["showLocationInLineNotes"] = show_location_in_line_notes
        if alphabetise_pay_categories is not UNSET:
            field_dict["alphabetisePayCategories"] = alphabetise_pay_categories
        if show_employee_external_id is not UNSET:
            field_dict["showEmployeeExternalId"] = show_employee_external_id
        if employees_must_login_to_download_payslips is not UNSET:
            field_dict["employeesMustLoginToDownloadPayslips"] = employees_must_login_to_download_payslips

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _super_contribution_processing_frequency_text_option = d.pop(
            "superContributionProcessingFrequencyTextOption", UNSET
        )
        super_contribution_processing_frequency_text_option: Union[
            Unset, AuEditBusinessPaySlipApiModelPaySlipSuperContributionProcessingFrequencyTextOption
        ]
        if isinstance(_super_contribution_processing_frequency_text_option, Unset):
            super_contribution_processing_frequency_text_option = UNSET
        else:
            super_contribution_processing_frequency_text_option = (
                AuEditBusinessPaySlipApiModelPaySlipSuperContributionProcessingFrequencyTextOption(
                    _super_contribution_processing_frequency_text_option
                )
            )

        show_classification = d.pop("showClassification", UNSET)

        show_base_pay_rate = d.pop("showBasePayRate", UNSET)

        show_employee_id = d.pop("showEmployeeId", UNSET)

        show_rate_for_annual_earnings = d.pop("showRateForAnnualEarnings", UNSET)

        id = d.pop("id", UNSET)

        email_from = d.pop("emailFrom", UNSET)

        email_body_message = d.pop("emailBodyMessage", UNSET)

        show_leave_accruals = d.pop("showLeaveAccruals", UNSET)

        show_line_notes = d.pop("showLineNotes", UNSET)

        show_location_in_line_notes = d.pop("showLocationInLineNotes", UNSET)

        alphabetise_pay_categories = d.pop("alphabetisePayCategories", UNSET)

        show_employee_external_id = d.pop("showEmployeeExternalId", UNSET)

        employees_must_login_to_download_payslips = d.pop("employeesMustLoginToDownloadPayslips", UNSET)

        au_edit_business_pay_slip_api_model = cls(
            super_contribution_processing_frequency_text_option=super_contribution_processing_frequency_text_option,
            show_classification=show_classification,
            show_base_pay_rate=show_base_pay_rate,
            show_employee_id=show_employee_id,
            show_rate_for_annual_earnings=show_rate_for_annual_earnings,
            id=id,
            email_from=email_from,
            email_body_message=email_body_message,
            show_leave_accruals=show_leave_accruals,
            show_line_notes=show_line_notes,
            show_location_in_line_notes=show_location_in_line_notes,
            alphabetise_pay_categories=alphabetise_pay_categories,
            show_employee_external_id=show_employee_external_id,
            employees_must_login_to_download_payslips=employees_must_login_to_download_payslips,
        )

        au_edit_business_pay_slip_api_model.additional_properties = d
        return au_edit_business_pay_slip_api_model

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
