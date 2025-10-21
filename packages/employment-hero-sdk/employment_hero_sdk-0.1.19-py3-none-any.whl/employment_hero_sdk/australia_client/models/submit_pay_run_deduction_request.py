from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.submit_pay_run_deduction_request_id_type import SubmitPayRunDeductionRequestIdType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.submit_pay_run_deduction_request_dictionary_string_list_1 import (
        SubmitPayRunDeductionRequestDictionaryStringList1,
    )


T = TypeVar("T", bound="SubmitPayRunDeductionRequest")


@_attrs_define
class SubmitPayRunDeductionRequest:
    """
    Attributes:
        deduction_category_id_type (Union[Unset, SubmitPayRunDeductionRequestIdType]):
        deductions (Union[Unset, SubmitPayRunDeductionRequestDictionaryStringList1]):
        pay_run_id (Union[Unset, int]):
        employee_id_type (Union[Unset, SubmitPayRunDeductionRequestIdType]):
        replace_existing (Union[Unset, bool]):
        suppress_calculations (Union[Unset, bool]):
    """

    deduction_category_id_type: Union[Unset, SubmitPayRunDeductionRequestIdType] = UNSET
    deductions: Union[Unset, "SubmitPayRunDeductionRequestDictionaryStringList1"] = UNSET
    pay_run_id: Union[Unset, int] = UNSET
    employee_id_type: Union[Unset, SubmitPayRunDeductionRequestIdType] = UNSET
    replace_existing: Union[Unset, bool] = UNSET
    suppress_calculations: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        deduction_category_id_type: Union[Unset, str] = UNSET
        if not isinstance(self.deduction_category_id_type, Unset):
            deduction_category_id_type = self.deduction_category_id_type.value

        deductions: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.deductions, Unset):
            deductions = self.deductions.to_dict()

        pay_run_id = self.pay_run_id

        employee_id_type: Union[Unset, str] = UNSET
        if not isinstance(self.employee_id_type, Unset):
            employee_id_type = self.employee_id_type.value

        replace_existing = self.replace_existing

        suppress_calculations = self.suppress_calculations

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if deduction_category_id_type is not UNSET:
            field_dict["deductionCategoryIdType"] = deduction_category_id_type
        if deductions is not UNSET:
            field_dict["deductions"] = deductions
        if pay_run_id is not UNSET:
            field_dict["payRunId"] = pay_run_id
        if employee_id_type is not UNSET:
            field_dict["employeeIdType"] = employee_id_type
        if replace_existing is not UNSET:
            field_dict["replaceExisting"] = replace_existing
        if suppress_calculations is not UNSET:
            field_dict["suppressCalculations"] = suppress_calculations

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.submit_pay_run_deduction_request_dictionary_string_list_1 import (
            SubmitPayRunDeductionRequestDictionaryStringList1,
        )

        d = src_dict.copy()
        _deduction_category_id_type = d.pop("deductionCategoryIdType", UNSET)
        deduction_category_id_type: Union[Unset, SubmitPayRunDeductionRequestIdType]
        if isinstance(_deduction_category_id_type, Unset):
            deduction_category_id_type = UNSET
        else:
            deduction_category_id_type = SubmitPayRunDeductionRequestIdType(_deduction_category_id_type)

        _deductions = d.pop("deductions", UNSET)
        deductions: Union[Unset, SubmitPayRunDeductionRequestDictionaryStringList1]
        if isinstance(_deductions, Unset):
            deductions = UNSET
        else:
            deductions = SubmitPayRunDeductionRequestDictionaryStringList1.from_dict(_deductions)

        pay_run_id = d.pop("payRunId", UNSET)

        _employee_id_type = d.pop("employeeIdType", UNSET)
        employee_id_type: Union[Unset, SubmitPayRunDeductionRequestIdType]
        if isinstance(_employee_id_type, Unset):
            employee_id_type = UNSET
        else:
            employee_id_type = SubmitPayRunDeductionRequestIdType(_employee_id_type)

        replace_existing = d.pop("replaceExisting", UNSET)

        suppress_calculations = d.pop("suppressCalculations", UNSET)

        submit_pay_run_deduction_request = cls(
            deduction_category_id_type=deduction_category_id_type,
            deductions=deductions,
            pay_run_id=pay_run_id,
            employee_id_type=employee_id_type,
            replace_existing=replace_existing,
            suppress_calculations=suppress_calculations,
        )

        submit_pay_run_deduction_request.additional_properties = d
        return submit_pay_run_deduction_request

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
