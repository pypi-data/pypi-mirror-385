from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.leave_history_report_detail_model_leave_unit_type_enum import (
    LeaveHistoryReportDetailModelLeaveUnitTypeEnum,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="LeaveHistoryReportDetailModel")


@_attrs_define
class LeaveHistoryReportDetailModel:
    """
    Attributes:
        pay_period (Union[Unset, str]):
        notes (Union[Unset, str]):
        leave_accrued (Union[Unset, float]):
        leave_taken (Union[Unset, float]):
        unit_type (Union[Unset, LeaveHistoryReportDetailModelLeaveUnitTypeEnum]):
    """

    pay_period: Union[Unset, str] = UNSET
    notes: Union[Unset, str] = UNSET
    leave_accrued: Union[Unset, float] = UNSET
    leave_taken: Union[Unset, float] = UNSET
    unit_type: Union[Unset, LeaveHistoryReportDetailModelLeaveUnitTypeEnum] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        pay_period = self.pay_period

        notes = self.notes

        leave_accrued = self.leave_accrued

        leave_taken = self.leave_taken

        unit_type: Union[Unset, str] = UNSET
        if not isinstance(self.unit_type, Unset):
            unit_type = self.unit_type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if pay_period is not UNSET:
            field_dict["payPeriod"] = pay_period
        if notes is not UNSET:
            field_dict["notes"] = notes
        if leave_accrued is not UNSET:
            field_dict["leaveAccrued"] = leave_accrued
        if leave_taken is not UNSET:
            field_dict["leaveTaken"] = leave_taken
        if unit_type is not UNSET:
            field_dict["unitType"] = unit_type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        pay_period = d.pop("payPeriod", UNSET)

        notes = d.pop("notes", UNSET)

        leave_accrued = d.pop("leaveAccrued", UNSET)

        leave_taken = d.pop("leaveTaken", UNSET)

        _unit_type = d.pop("unitType", UNSET)
        unit_type: Union[Unset, LeaveHistoryReportDetailModelLeaveUnitTypeEnum]
        if isinstance(_unit_type, Unset):
            unit_type = UNSET
        else:
            unit_type = LeaveHistoryReportDetailModelLeaveUnitTypeEnum(_unit_type)

        leave_history_report_detail_model = cls(
            pay_period=pay_period,
            notes=notes,
            leave_accrued=leave_accrued,
            leave_taken=leave_taken,
            unit_type=unit_type,
        )

        leave_history_report_detail_model.additional_properties = d
        return leave_history_report_detail_model

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
