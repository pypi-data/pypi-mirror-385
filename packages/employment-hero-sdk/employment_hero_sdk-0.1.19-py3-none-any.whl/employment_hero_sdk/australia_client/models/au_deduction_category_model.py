from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.au_deduction_category_model_deduction_category_payment_summary_classification import (
    AuDeductionCategoryModelDeductionCategoryPaymentSummaryClassification,
)
from ..models.au_deduction_category_model_external_service import AuDeductionCategoryModelExternalService
from ..models.au_deduction_category_model_sgc_calculation_impact_enum import (
    AuDeductionCategoryModelSGCCalculationImpactEnum,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="AuDeductionCategoryModel")


@_attrs_define
class AuDeductionCategoryModel:
    """
    Attributes:
        tax_exempt (Union[Unset, bool]):
        expense_general_ledger_mapping_code (Union[Unset, str]):
        liability_general_ledger_mapping_code (Union[Unset, str]):
        sgc_calculation_impact (Union[Unset, AuDeductionCategoryModelSGCCalculationImpactEnum]):
        payment_summary_classification (Union[Unset,
            AuDeductionCategoryModelDeductionCategoryPaymentSummaryClassification]):
        is_resc (Union[Unset, bool]):
        id (Union[Unset, int]):
        name (Union[Unset, str]):
        source (Union[Unset, AuDeductionCategoryModelExternalService]):
        external_id (Union[Unset, str]):
        is_system (Union[Unset, bool]):
    """

    tax_exempt: Union[Unset, bool] = UNSET
    expense_general_ledger_mapping_code: Union[Unset, str] = UNSET
    liability_general_ledger_mapping_code: Union[Unset, str] = UNSET
    sgc_calculation_impact: Union[Unset, AuDeductionCategoryModelSGCCalculationImpactEnum] = UNSET
    payment_summary_classification: Union[
        Unset, AuDeductionCategoryModelDeductionCategoryPaymentSummaryClassification
    ] = UNSET
    is_resc: Union[Unset, bool] = UNSET
    id: Union[Unset, int] = UNSET
    name: Union[Unset, str] = UNSET
    source: Union[Unset, AuDeductionCategoryModelExternalService] = UNSET
    external_id: Union[Unset, str] = UNSET
    is_system: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        tax_exempt = self.tax_exempt

        expense_general_ledger_mapping_code = self.expense_general_ledger_mapping_code

        liability_general_ledger_mapping_code = self.liability_general_ledger_mapping_code

        sgc_calculation_impact: Union[Unset, str] = UNSET
        if not isinstance(self.sgc_calculation_impact, Unset):
            sgc_calculation_impact = self.sgc_calculation_impact.value

        payment_summary_classification: Union[Unset, str] = UNSET
        if not isinstance(self.payment_summary_classification, Unset):
            payment_summary_classification = self.payment_summary_classification.value

        is_resc = self.is_resc

        id = self.id

        name = self.name

        source: Union[Unset, str] = UNSET
        if not isinstance(self.source, Unset):
            source = self.source.value

        external_id = self.external_id

        is_system = self.is_system

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if tax_exempt is not UNSET:
            field_dict["taxExempt"] = tax_exempt
        if expense_general_ledger_mapping_code is not UNSET:
            field_dict["expenseGeneralLedgerMappingCode"] = expense_general_ledger_mapping_code
        if liability_general_ledger_mapping_code is not UNSET:
            field_dict["liabilityGeneralLedgerMappingCode"] = liability_general_ledger_mapping_code
        if sgc_calculation_impact is not UNSET:
            field_dict["sgcCalculationImpact"] = sgc_calculation_impact
        if payment_summary_classification is not UNSET:
            field_dict["paymentSummaryClassification"] = payment_summary_classification
        if is_resc is not UNSET:
            field_dict["isResc"] = is_resc
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if source is not UNSET:
            field_dict["source"] = source
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if is_system is not UNSET:
            field_dict["isSystem"] = is_system

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        tax_exempt = d.pop("taxExempt", UNSET)

        expense_general_ledger_mapping_code = d.pop("expenseGeneralLedgerMappingCode", UNSET)

        liability_general_ledger_mapping_code = d.pop("liabilityGeneralLedgerMappingCode", UNSET)

        _sgc_calculation_impact = d.pop("sgcCalculationImpact", UNSET)
        sgc_calculation_impact: Union[Unset, AuDeductionCategoryModelSGCCalculationImpactEnum]
        if isinstance(_sgc_calculation_impact, Unset):
            sgc_calculation_impact = UNSET
        else:
            sgc_calculation_impact = AuDeductionCategoryModelSGCCalculationImpactEnum(_sgc_calculation_impact)

        _payment_summary_classification = d.pop("paymentSummaryClassification", UNSET)
        payment_summary_classification: Union[
            Unset, AuDeductionCategoryModelDeductionCategoryPaymentSummaryClassification
        ]
        if isinstance(_payment_summary_classification, Unset):
            payment_summary_classification = UNSET
        else:
            payment_summary_classification = AuDeductionCategoryModelDeductionCategoryPaymentSummaryClassification(
                _payment_summary_classification
            )

        is_resc = d.pop("isResc", UNSET)

        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        _source = d.pop("source", UNSET)
        source: Union[Unset, AuDeductionCategoryModelExternalService]
        if isinstance(_source, Unset):
            source = UNSET
        else:
            source = AuDeductionCategoryModelExternalService(_source)

        external_id = d.pop("externalId", UNSET)

        is_system = d.pop("isSystem", UNSET)

        au_deduction_category_model = cls(
            tax_exempt=tax_exempt,
            expense_general_ledger_mapping_code=expense_general_ledger_mapping_code,
            liability_general_ledger_mapping_code=liability_general_ledger_mapping_code,
            sgc_calculation_impact=sgc_calculation_impact,
            payment_summary_classification=payment_summary_classification,
            is_resc=is_resc,
            id=id,
            name=name,
            source=source,
            external_id=external_id,
            is_system=is_system,
        )

        au_deduction_category_model.additional_properties = d
        return au_deduction_category_model

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
