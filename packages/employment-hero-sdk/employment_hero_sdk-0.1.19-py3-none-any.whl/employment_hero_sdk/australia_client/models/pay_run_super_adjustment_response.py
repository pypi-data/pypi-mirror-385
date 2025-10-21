from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.pay_run_super_adjustment_response_dictionary_string_list_1 import (
        PayRunSuperAdjustmentResponseDictionaryStringList1,
    )


T = TypeVar("T", bound="PayRunSuperAdjustmentResponse")


@_attrs_define
class PayRunSuperAdjustmentResponse:
    """
    Attributes:
        super_adjustments (Union[Unset, PayRunSuperAdjustmentResponseDictionaryStringList1]):
        pay_run_id (Union[Unset, int]):
    """

    super_adjustments: Union[Unset, "PayRunSuperAdjustmentResponseDictionaryStringList1"] = UNSET
    pay_run_id: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        super_adjustments: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.super_adjustments, Unset):
            super_adjustments = self.super_adjustments.to_dict()

        pay_run_id = self.pay_run_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if super_adjustments is not UNSET:
            field_dict["superAdjustments"] = super_adjustments
        if pay_run_id is not UNSET:
            field_dict["payRunId"] = pay_run_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.pay_run_super_adjustment_response_dictionary_string_list_1 import (
            PayRunSuperAdjustmentResponseDictionaryStringList1,
        )

        d = src_dict.copy()
        _super_adjustments = d.pop("superAdjustments", UNSET)
        super_adjustments: Union[Unset, PayRunSuperAdjustmentResponseDictionaryStringList1]
        if isinstance(_super_adjustments, Unset):
            super_adjustments = UNSET
        else:
            super_adjustments = PayRunSuperAdjustmentResponseDictionaryStringList1.from_dict(_super_adjustments)

        pay_run_id = d.pop("payRunId", UNSET)

        pay_run_super_adjustment_response = cls(
            super_adjustments=super_adjustments,
            pay_run_id=pay_run_id,
        )

        pay_run_super_adjustment_response.additional_properties = d
        return pay_run_super_adjustment_response

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
