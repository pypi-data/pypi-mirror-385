from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.submit_pay_run_super_adjustment_request_id_type import SubmitPayRunSuperAdjustmentRequestIdType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.submit_pay_run_super_adjustment_request_dictionary_string_list_1 import (
        SubmitPayRunSuperAdjustmentRequestDictionaryStringList1,
    )


T = TypeVar("T", bound="SubmitPayRunSuperAdjustmentRequest")


@_attrs_define
class SubmitPayRunSuperAdjustmentRequest:
    """
    Attributes:
        super_adjustments (Union[Unset, SubmitPayRunSuperAdjustmentRequestDictionaryStringList1]):
        pay_run_id (Union[Unset, int]):
        employee_id_type (Union[Unset, SubmitPayRunSuperAdjustmentRequestIdType]):
        replace_existing (Union[Unset, bool]):
        suppress_calculations (Union[Unset, bool]):
    """

    super_adjustments: Union[Unset, "SubmitPayRunSuperAdjustmentRequestDictionaryStringList1"] = UNSET
    pay_run_id: Union[Unset, int] = UNSET
    employee_id_type: Union[Unset, SubmitPayRunSuperAdjustmentRequestIdType] = UNSET
    replace_existing: Union[Unset, bool] = UNSET
    suppress_calculations: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        super_adjustments: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.super_adjustments, Unset):
            super_adjustments = self.super_adjustments.to_dict()

        pay_run_id = self.pay_run_id

        employee_id_type: Union[Unset, str] = UNSET
        if not isinstance(self.employee_id_type, Unset):
            employee_id_type = self.employee_id_type.value

        replace_existing = self.replace_existing

        suppress_calculations = self.suppress_calculations

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if super_adjustments is not UNSET:
            field_dict["superAdjustments"] = super_adjustments
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
        from ..models.submit_pay_run_super_adjustment_request_dictionary_string_list_1 import (
            SubmitPayRunSuperAdjustmentRequestDictionaryStringList1,
        )

        d = src_dict.copy()
        _super_adjustments = d.pop("superAdjustments", UNSET)
        super_adjustments: Union[Unset, SubmitPayRunSuperAdjustmentRequestDictionaryStringList1]
        if isinstance(_super_adjustments, Unset):
            super_adjustments = UNSET
        else:
            super_adjustments = SubmitPayRunSuperAdjustmentRequestDictionaryStringList1.from_dict(_super_adjustments)

        pay_run_id = d.pop("payRunId", UNSET)

        _employee_id_type = d.pop("employeeIdType", UNSET)
        employee_id_type: Union[Unset, SubmitPayRunSuperAdjustmentRequestIdType]
        if isinstance(_employee_id_type, Unset):
            employee_id_type = UNSET
        else:
            employee_id_type = SubmitPayRunSuperAdjustmentRequestIdType(_employee_id_type)

        replace_existing = d.pop("replaceExisting", UNSET)

        suppress_calculations = d.pop("suppressCalculations", UNSET)

        submit_pay_run_super_adjustment_request = cls(
            super_adjustments=super_adjustments,
            pay_run_id=pay_run_id,
            employee_id_type=employee_id_type,
            replace_existing=replace_existing,
            suppress_calculations=suppress_calculations,
        )

        submit_pay_run_super_adjustment_request.additional_properties = d
        return submit_pay_run_super_adjustment_request

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
