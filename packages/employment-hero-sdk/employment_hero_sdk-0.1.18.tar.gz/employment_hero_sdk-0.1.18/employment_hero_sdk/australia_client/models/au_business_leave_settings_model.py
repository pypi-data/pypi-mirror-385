import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.au_business_leave_settings_model_leave_accrual_start_date_type import (
    AuBusinessLeaveSettingsModelLeaveAccrualStartDateType,
)
from ..models.au_business_leave_settings_model_leave_entitlement_calculation_method_enum import (
    AuBusinessLeaveSettingsModelLeaveEntitlementCalculationMethodEnum,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="AuBusinessLeaveSettingsModel")


@_attrs_define
class AuBusinessLeaveSettingsModel:
    """
    Attributes:
        leave_calculation_method (Union[Unset, AuBusinessLeaveSettingsModelLeaveEntitlementCalculationMethodEnum]):
        require_notes_for_leave_requests (Union[Unset, bool]):
        leave_year_should_start_on (Union[Unset, datetime.datetime]):
        leave_accrual_start_date_type (Union[Unset, AuBusinessLeaveSettingsModelLeaveAccrualStartDateType]):
    """

    leave_calculation_method: Union[Unset, AuBusinessLeaveSettingsModelLeaveEntitlementCalculationMethodEnum] = UNSET
    require_notes_for_leave_requests: Union[Unset, bool] = UNSET
    leave_year_should_start_on: Union[Unset, datetime.datetime] = UNSET
    leave_accrual_start_date_type: Union[Unset, AuBusinessLeaveSettingsModelLeaveAccrualStartDateType] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        leave_calculation_method: Union[Unset, str] = UNSET
        if not isinstance(self.leave_calculation_method, Unset):
            leave_calculation_method = self.leave_calculation_method.value

        require_notes_for_leave_requests = self.require_notes_for_leave_requests

        leave_year_should_start_on: Union[Unset, str] = UNSET
        if not isinstance(self.leave_year_should_start_on, Unset):
            leave_year_should_start_on = self.leave_year_should_start_on.isoformat()

        leave_accrual_start_date_type: Union[Unset, str] = UNSET
        if not isinstance(self.leave_accrual_start_date_type, Unset):
            leave_accrual_start_date_type = self.leave_accrual_start_date_type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if leave_calculation_method is not UNSET:
            field_dict["leaveCalculationMethod"] = leave_calculation_method
        if require_notes_for_leave_requests is not UNSET:
            field_dict["requireNotesForLeaveRequests"] = require_notes_for_leave_requests
        if leave_year_should_start_on is not UNSET:
            field_dict["leaveYearShouldStartOn"] = leave_year_should_start_on
        if leave_accrual_start_date_type is not UNSET:
            field_dict["leaveAccrualStartDateType"] = leave_accrual_start_date_type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _leave_calculation_method = d.pop("leaveCalculationMethod", UNSET)
        leave_calculation_method: Union[Unset, AuBusinessLeaveSettingsModelLeaveEntitlementCalculationMethodEnum]
        if isinstance(_leave_calculation_method, Unset):
            leave_calculation_method = UNSET
        else:
            leave_calculation_method = AuBusinessLeaveSettingsModelLeaveEntitlementCalculationMethodEnum(
                _leave_calculation_method
            )

        require_notes_for_leave_requests = d.pop("requireNotesForLeaveRequests", UNSET)

        _leave_year_should_start_on = d.pop("leaveYearShouldStartOn", UNSET)
        leave_year_should_start_on: Union[Unset, datetime.datetime]
        if isinstance(_leave_year_should_start_on, Unset):
            leave_year_should_start_on = UNSET
        else:
            leave_year_should_start_on = isoparse(_leave_year_should_start_on)

        _leave_accrual_start_date_type = d.pop("leaveAccrualStartDateType", UNSET)
        leave_accrual_start_date_type: Union[Unset, AuBusinessLeaveSettingsModelLeaveAccrualStartDateType]
        if isinstance(_leave_accrual_start_date_type, Unset):
            leave_accrual_start_date_type = UNSET
        else:
            leave_accrual_start_date_type = AuBusinessLeaveSettingsModelLeaveAccrualStartDateType(
                _leave_accrual_start_date_type
            )

        au_business_leave_settings_model = cls(
            leave_calculation_method=leave_calculation_method,
            require_notes_for_leave_requests=require_notes_for_leave_requests,
            leave_year_should_start_on=leave_year_should_start_on,
            leave_accrual_start_date_type=leave_accrual_start_date_type,
        )

        au_business_leave_settings_model.additional_properties = d
        return au_business_leave_settings_model

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
