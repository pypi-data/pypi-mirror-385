from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="BulkApplyLeaveRequestModel")


@_attrs_define
class BulkApplyLeaveRequestModel:
    """
    Attributes:
        leave_request_ids (Union[Unset, List[int]]):
        align_to_pay_run_period (Union[Unset, bool]):
    """

    leave_request_ids: Union[Unset, List[int]] = UNSET
    align_to_pay_run_period: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        leave_request_ids: Union[Unset, List[int]] = UNSET
        if not isinstance(self.leave_request_ids, Unset):
            leave_request_ids = self.leave_request_ids

        align_to_pay_run_period = self.align_to_pay_run_period

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if leave_request_ids is not UNSET:
            field_dict["leaveRequestIds"] = leave_request_ids
        if align_to_pay_run_period is not UNSET:
            field_dict["alignToPayRunPeriod"] = align_to_pay_run_period

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        leave_request_ids = cast(List[int], d.pop("leaveRequestIds", UNSET))

        align_to_pay_run_period = d.pop("alignToPayRunPeriod", UNSET)

        bulk_apply_leave_request_model = cls(
            leave_request_ids=leave_request_ids,
            align_to_pay_run_period=align_to_pay_run_period,
        )

        bulk_apply_leave_request_model.additional_properties = d
        return bulk_apply_leave_request_model

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
