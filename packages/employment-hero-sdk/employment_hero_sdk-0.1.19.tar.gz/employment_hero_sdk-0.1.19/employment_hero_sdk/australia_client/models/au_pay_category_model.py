from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.au_pay_category_model_au_pay_category_type import AuPayCategoryModelAuPayCategoryType
from ..models.au_pay_category_model_nullable_midpoint_rounding import AuPayCategoryModelNullableMidpointRounding
from ..models.au_pay_category_model_nullable_pay_category_payment_summary_classification import (
    AuPayCategoryModelNullablePayCategoryPaymentSummaryClassification,
)
from ..models.au_pay_category_model_rate_unit_enum import AuPayCategoryModelRateUnitEnum
from ..types import UNSET, Unset

T = TypeVar("T", bound="AuPayCategoryModel")


@_attrs_define
class AuPayCategoryModel:
    """
    Attributes:
        payment_summary_classification (Union[Unset,
            AuPayCategoryModelNullablePayCategoryPaymentSummaryClassification]):
        allowance_description (Union[Unset, str]):
        default_super_rate (Union[Unset, float]):
        super_expense_mapping_code (Union[Unset, str]):
        super_liability_mapping_code (Union[Unset, str]):
        is_payroll_tax_exempt (Union[Unset, bool]):
        award_name (Union[Unset, str]):
        award_id (Union[Unset, int]):
        pay_category_type (Union[Unset, AuPayCategoryModelAuPayCategoryType]):
        id (Union[Unset, int]):
        parent_id (Union[Unset, int]):
        name (Union[Unset, str]):
        rate_unit (Union[Unset, AuPayCategoryModelRateUnitEnum]):
        accrues_leave (Union[Unset, bool]):
        rate_loading_percent (Union[Unset, float]):
        penalty_loading_percent (Union[Unset, float]):
        is_tax_exempt (Union[Unset, bool]):
        external_id (Union[Unset, str]):
        source (Union[Unset, str]):
        general_ledger_mapping_code (Union[Unset, str]):
        is_system_pay_category (Union[Unset, bool]):
        number_of_decimal_places (Union[Unset, int]):
        rounding_method (Union[Unset, AuPayCategoryModelNullableMidpointRounding]):
        hide_units_on_pay_slip (Union[Unset, bool]):
        is_primary (Union[Unset, bool]):
    """

    payment_summary_classification: Union[Unset, AuPayCategoryModelNullablePayCategoryPaymentSummaryClassification] = (
        UNSET
    )
    allowance_description: Union[Unset, str] = UNSET
    default_super_rate: Union[Unset, float] = UNSET
    super_expense_mapping_code: Union[Unset, str] = UNSET
    super_liability_mapping_code: Union[Unset, str] = UNSET
    is_payroll_tax_exempt: Union[Unset, bool] = UNSET
    award_name: Union[Unset, str] = UNSET
    award_id: Union[Unset, int] = UNSET
    pay_category_type: Union[Unset, AuPayCategoryModelAuPayCategoryType] = UNSET
    id: Union[Unset, int] = UNSET
    parent_id: Union[Unset, int] = UNSET
    name: Union[Unset, str] = UNSET
    rate_unit: Union[Unset, AuPayCategoryModelRateUnitEnum] = UNSET
    accrues_leave: Union[Unset, bool] = UNSET
    rate_loading_percent: Union[Unset, float] = UNSET
    penalty_loading_percent: Union[Unset, float] = UNSET
    is_tax_exempt: Union[Unset, bool] = UNSET
    external_id: Union[Unset, str] = UNSET
    source: Union[Unset, str] = UNSET
    general_ledger_mapping_code: Union[Unset, str] = UNSET
    is_system_pay_category: Union[Unset, bool] = UNSET
    number_of_decimal_places: Union[Unset, int] = UNSET
    rounding_method: Union[Unset, AuPayCategoryModelNullableMidpointRounding] = UNSET
    hide_units_on_pay_slip: Union[Unset, bool] = UNSET
    is_primary: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        payment_summary_classification: Union[Unset, str] = UNSET
        if not isinstance(self.payment_summary_classification, Unset):
            payment_summary_classification = self.payment_summary_classification.value

        allowance_description = self.allowance_description

        default_super_rate = self.default_super_rate

        super_expense_mapping_code = self.super_expense_mapping_code

        super_liability_mapping_code = self.super_liability_mapping_code

        is_payroll_tax_exempt = self.is_payroll_tax_exempt

        award_name = self.award_name

        award_id = self.award_id

        pay_category_type: Union[Unset, str] = UNSET
        if not isinstance(self.pay_category_type, Unset):
            pay_category_type = self.pay_category_type.value

        id = self.id

        parent_id = self.parent_id

        name = self.name

        rate_unit: Union[Unset, str] = UNSET
        if not isinstance(self.rate_unit, Unset):
            rate_unit = self.rate_unit.value

        accrues_leave = self.accrues_leave

        rate_loading_percent = self.rate_loading_percent

        penalty_loading_percent = self.penalty_loading_percent

        is_tax_exempt = self.is_tax_exempt

        external_id = self.external_id

        source = self.source

        general_ledger_mapping_code = self.general_ledger_mapping_code

        is_system_pay_category = self.is_system_pay_category

        number_of_decimal_places = self.number_of_decimal_places

        rounding_method: Union[Unset, str] = UNSET
        if not isinstance(self.rounding_method, Unset):
            rounding_method = self.rounding_method.value

        hide_units_on_pay_slip = self.hide_units_on_pay_slip

        is_primary = self.is_primary

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if payment_summary_classification is not UNSET:
            field_dict["paymentSummaryClassification"] = payment_summary_classification
        if allowance_description is not UNSET:
            field_dict["allowanceDescription"] = allowance_description
        if default_super_rate is not UNSET:
            field_dict["defaultSuperRate"] = default_super_rate
        if super_expense_mapping_code is not UNSET:
            field_dict["superExpenseMappingCode"] = super_expense_mapping_code
        if super_liability_mapping_code is not UNSET:
            field_dict["superLiabilityMappingCode"] = super_liability_mapping_code
        if is_payroll_tax_exempt is not UNSET:
            field_dict["isPayrollTaxExempt"] = is_payroll_tax_exempt
        if award_name is not UNSET:
            field_dict["awardName"] = award_name
        if award_id is not UNSET:
            field_dict["awardId"] = award_id
        if pay_category_type is not UNSET:
            field_dict["payCategoryType"] = pay_category_type
        if id is not UNSET:
            field_dict["id"] = id
        if parent_id is not UNSET:
            field_dict["parentId"] = parent_id
        if name is not UNSET:
            field_dict["name"] = name
        if rate_unit is not UNSET:
            field_dict["rateUnit"] = rate_unit
        if accrues_leave is not UNSET:
            field_dict["accruesLeave"] = accrues_leave
        if rate_loading_percent is not UNSET:
            field_dict["rateLoadingPercent"] = rate_loading_percent
        if penalty_loading_percent is not UNSET:
            field_dict["penaltyLoadingPercent"] = penalty_loading_percent
        if is_tax_exempt is not UNSET:
            field_dict["isTaxExempt"] = is_tax_exempt
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if source is not UNSET:
            field_dict["source"] = source
        if general_ledger_mapping_code is not UNSET:
            field_dict["generalLedgerMappingCode"] = general_ledger_mapping_code
        if is_system_pay_category is not UNSET:
            field_dict["isSystemPayCategory"] = is_system_pay_category
        if number_of_decimal_places is not UNSET:
            field_dict["numberOfDecimalPlaces"] = number_of_decimal_places
        if rounding_method is not UNSET:
            field_dict["roundingMethod"] = rounding_method
        if hide_units_on_pay_slip is not UNSET:
            field_dict["hideUnitsOnPaySlip"] = hide_units_on_pay_slip
        if is_primary is not UNSET:
            field_dict["isPrimary"] = is_primary

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _payment_summary_classification = d.pop("paymentSummaryClassification", UNSET)
        payment_summary_classification: Union[Unset, AuPayCategoryModelNullablePayCategoryPaymentSummaryClassification]
        if isinstance(_payment_summary_classification, Unset):
            payment_summary_classification = UNSET
        else:
            payment_summary_classification = AuPayCategoryModelNullablePayCategoryPaymentSummaryClassification(
                _payment_summary_classification
            )

        allowance_description = d.pop("allowanceDescription", UNSET)

        default_super_rate = d.pop("defaultSuperRate", UNSET)

        super_expense_mapping_code = d.pop("superExpenseMappingCode", UNSET)

        super_liability_mapping_code = d.pop("superLiabilityMappingCode", UNSET)

        is_payroll_tax_exempt = d.pop("isPayrollTaxExempt", UNSET)

        award_name = d.pop("awardName", UNSET)

        award_id = d.pop("awardId", UNSET)

        _pay_category_type = d.pop("payCategoryType", UNSET)
        pay_category_type: Union[Unset, AuPayCategoryModelAuPayCategoryType]
        if isinstance(_pay_category_type, Unset):
            pay_category_type = UNSET
        else:
            pay_category_type = AuPayCategoryModelAuPayCategoryType(_pay_category_type)

        id = d.pop("id", UNSET)

        parent_id = d.pop("parentId", UNSET)

        name = d.pop("name", UNSET)

        _rate_unit = d.pop("rateUnit", UNSET)
        rate_unit: Union[Unset, AuPayCategoryModelRateUnitEnum]
        if isinstance(_rate_unit, Unset):
            rate_unit = UNSET
        else:
            rate_unit = AuPayCategoryModelRateUnitEnum(_rate_unit)

        accrues_leave = d.pop("accruesLeave", UNSET)

        rate_loading_percent = d.pop("rateLoadingPercent", UNSET)

        penalty_loading_percent = d.pop("penaltyLoadingPercent", UNSET)

        is_tax_exempt = d.pop("isTaxExempt", UNSET)

        external_id = d.pop("externalId", UNSET)

        source = d.pop("source", UNSET)

        general_ledger_mapping_code = d.pop("generalLedgerMappingCode", UNSET)

        is_system_pay_category = d.pop("isSystemPayCategory", UNSET)

        number_of_decimal_places = d.pop("numberOfDecimalPlaces", UNSET)

        _rounding_method = d.pop("roundingMethod", UNSET)
        rounding_method: Union[Unset, AuPayCategoryModelNullableMidpointRounding]
        if isinstance(_rounding_method, Unset):
            rounding_method = UNSET
        else:
            rounding_method = AuPayCategoryModelNullableMidpointRounding(_rounding_method)

        hide_units_on_pay_slip = d.pop("hideUnitsOnPaySlip", UNSET)

        is_primary = d.pop("isPrimary", UNSET)

        au_pay_category_model = cls(
            payment_summary_classification=payment_summary_classification,
            allowance_description=allowance_description,
            default_super_rate=default_super_rate,
            super_expense_mapping_code=super_expense_mapping_code,
            super_liability_mapping_code=super_liability_mapping_code,
            is_payroll_tax_exempt=is_payroll_tax_exempt,
            award_name=award_name,
            award_id=award_id,
            pay_category_type=pay_category_type,
            id=id,
            parent_id=parent_id,
            name=name,
            rate_unit=rate_unit,
            accrues_leave=accrues_leave,
            rate_loading_percent=rate_loading_percent,
            penalty_loading_percent=penalty_loading_percent,
            is_tax_exempt=is_tax_exempt,
            external_id=external_id,
            source=source,
            general_ledger_mapping_code=general_ledger_mapping_code,
            is_system_pay_category=is_system_pay_category,
            number_of_decimal_places=number_of_decimal_places,
            rounding_method=rounding_method,
            hide_units_on_pay_slip=hide_units_on_pay_slip,
            is_primary=is_primary,
        )

        au_pay_category_model.additional_properties = d
        return au_pay_category_model

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
