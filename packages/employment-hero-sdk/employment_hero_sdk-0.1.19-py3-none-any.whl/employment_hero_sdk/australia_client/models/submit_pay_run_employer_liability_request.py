from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.submit_pay_run_employer_liability_request_id_type import SubmitPayRunEmployerLiabilityRequestIdType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.submit_pay_run_employer_liability_request_dictionary_string_list_1 import (
        SubmitPayRunEmployerLiabilityRequestDictionaryStringList1,
    )


T = TypeVar("T", bound="SubmitPayRunEmployerLiabilityRequest")


@_attrs_define
class SubmitPayRunEmployerLiabilityRequest:
    """
    Attributes:
        employer_liability_category_id_type (Union[Unset, SubmitPayRunEmployerLiabilityRequestIdType]):
        employer_liabilities (Union[Unset, SubmitPayRunEmployerLiabilityRequestDictionaryStringList1]):
        pay_run_id (Union[Unset, int]):
        employee_id_type (Union[Unset, SubmitPayRunEmployerLiabilityRequestIdType]):
        replace_existing (Union[Unset, bool]):
        suppress_calculations (Union[Unset, bool]):
    """

    employer_liability_category_id_type: Union[Unset, SubmitPayRunEmployerLiabilityRequestIdType] = UNSET
    employer_liabilities: Union[Unset, "SubmitPayRunEmployerLiabilityRequestDictionaryStringList1"] = UNSET
    pay_run_id: Union[Unset, int] = UNSET
    employee_id_type: Union[Unset, SubmitPayRunEmployerLiabilityRequestIdType] = UNSET
    replace_existing: Union[Unset, bool] = UNSET
    suppress_calculations: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        employer_liability_category_id_type: Union[Unset, str] = UNSET
        if not isinstance(self.employer_liability_category_id_type, Unset):
            employer_liability_category_id_type = self.employer_liability_category_id_type.value

        employer_liabilities: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.employer_liabilities, Unset):
            employer_liabilities = self.employer_liabilities.to_dict()

        pay_run_id = self.pay_run_id

        employee_id_type: Union[Unset, str] = UNSET
        if not isinstance(self.employee_id_type, Unset):
            employee_id_type = self.employee_id_type.value

        replace_existing = self.replace_existing

        suppress_calculations = self.suppress_calculations

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if employer_liability_category_id_type is not UNSET:
            field_dict["employerLiabilityCategoryIdType"] = employer_liability_category_id_type
        if employer_liabilities is not UNSET:
            field_dict["employerLiabilities"] = employer_liabilities
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
        from ..models.submit_pay_run_employer_liability_request_dictionary_string_list_1 import (
            SubmitPayRunEmployerLiabilityRequestDictionaryStringList1,
        )

        d = src_dict.copy()
        _employer_liability_category_id_type = d.pop("employerLiabilityCategoryIdType", UNSET)
        employer_liability_category_id_type: Union[Unset, SubmitPayRunEmployerLiabilityRequestIdType]
        if isinstance(_employer_liability_category_id_type, Unset):
            employer_liability_category_id_type = UNSET
        else:
            employer_liability_category_id_type = SubmitPayRunEmployerLiabilityRequestIdType(
                _employer_liability_category_id_type
            )

        _employer_liabilities = d.pop("employerLiabilities", UNSET)
        employer_liabilities: Union[Unset, SubmitPayRunEmployerLiabilityRequestDictionaryStringList1]
        if isinstance(_employer_liabilities, Unset):
            employer_liabilities = UNSET
        else:
            employer_liabilities = SubmitPayRunEmployerLiabilityRequestDictionaryStringList1.from_dict(
                _employer_liabilities
            )

        pay_run_id = d.pop("payRunId", UNSET)

        _employee_id_type = d.pop("employeeIdType", UNSET)
        employee_id_type: Union[Unset, SubmitPayRunEmployerLiabilityRequestIdType]
        if isinstance(_employee_id_type, Unset):
            employee_id_type = UNSET
        else:
            employee_id_type = SubmitPayRunEmployerLiabilityRequestIdType(_employee_id_type)

        replace_existing = d.pop("replaceExisting", UNSET)

        suppress_calculations = d.pop("suppressCalculations", UNSET)

        submit_pay_run_employer_liability_request = cls(
            employer_liability_category_id_type=employer_liability_category_id_type,
            employer_liabilities=employer_liabilities,
            pay_run_id=pay_run_id,
            employee_id_type=employee_id_type,
            replace_existing=replace_existing,
            suppress_calculations=suppress_calculations,
        )

        submit_pay_run_employer_liability_request.additional_properties = d
        return submit_pay_run_employer_liability_request

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
