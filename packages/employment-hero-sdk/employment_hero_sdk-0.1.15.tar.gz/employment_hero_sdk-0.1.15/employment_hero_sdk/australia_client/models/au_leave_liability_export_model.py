import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.au_leave_liability_export_model_leave_unit_type_enum import AuLeaveLiabilityExportModelLeaveUnitTypeEnum
from ..types import UNSET, Unset

T = TypeVar("T", bound="AuLeaveLiabilityExportModel")


@_attrs_define
class AuLeaveLiabilityExportModel:
    """
    Attributes:
        leave_loading_dollar_value (Union[Unset, float]):
        employee_id (Union[Unset, int]):
        first_name (Union[Unset, str]):
        surname (Union[Unset, str]):
        external_id (Union[Unset, str]):
        start_date (Union[Unset, datetime.datetime]):
        last_paid_date (Union[Unset, datetime.datetime]):
        last_pay_period_ending (Union[Unset, datetime.datetime]):
        calculated_weeks (Union[Unset, float]):
        location (Union[Unset, str]):
        leave_category_name (Union[Unset, str]):
        approved_leave_amount (Union[Unset, float]):
        accrued_amount (Union[Unset, float]):
        leave_value (Union[Unset, float]):
        approved_leave_amount_in_hours (Union[Unset, float]):
        unit_type (Union[Unset, AuLeaveLiabilityExportModelLeaveUnitTypeEnum]):
        accrued_amount_in_hours (Union[Unset, float]):
    """

    leave_loading_dollar_value: Union[Unset, float] = UNSET
    employee_id: Union[Unset, int] = UNSET
    first_name: Union[Unset, str] = UNSET
    surname: Union[Unset, str] = UNSET
    external_id: Union[Unset, str] = UNSET
    start_date: Union[Unset, datetime.datetime] = UNSET
    last_paid_date: Union[Unset, datetime.datetime] = UNSET
    last_pay_period_ending: Union[Unset, datetime.datetime] = UNSET
    calculated_weeks: Union[Unset, float] = UNSET
    location: Union[Unset, str] = UNSET
    leave_category_name: Union[Unset, str] = UNSET
    approved_leave_amount: Union[Unset, float] = UNSET
    accrued_amount: Union[Unset, float] = UNSET
    leave_value: Union[Unset, float] = UNSET
    approved_leave_amount_in_hours: Union[Unset, float] = UNSET
    unit_type: Union[Unset, AuLeaveLiabilityExportModelLeaveUnitTypeEnum] = UNSET
    accrued_amount_in_hours: Union[Unset, float] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        leave_loading_dollar_value = self.leave_loading_dollar_value

        employee_id = self.employee_id

        first_name = self.first_name

        surname = self.surname

        external_id = self.external_id

        start_date: Union[Unset, str] = UNSET
        if not isinstance(self.start_date, Unset):
            start_date = self.start_date.isoformat()

        last_paid_date: Union[Unset, str] = UNSET
        if not isinstance(self.last_paid_date, Unset):
            last_paid_date = self.last_paid_date.isoformat()

        last_pay_period_ending: Union[Unset, str] = UNSET
        if not isinstance(self.last_pay_period_ending, Unset):
            last_pay_period_ending = self.last_pay_period_ending.isoformat()

        calculated_weeks = self.calculated_weeks

        location = self.location

        leave_category_name = self.leave_category_name

        approved_leave_amount = self.approved_leave_amount

        accrued_amount = self.accrued_amount

        leave_value = self.leave_value

        approved_leave_amount_in_hours = self.approved_leave_amount_in_hours

        unit_type: Union[Unset, str] = UNSET
        if not isinstance(self.unit_type, Unset):
            unit_type = self.unit_type.value

        accrued_amount_in_hours = self.accrued_amount_in_hours

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if leave_loading_dollar_value is not UNSET:
            field_dict["leaveLoadingDollarValue"] = leave_loading_dollar_value
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if first_name is not UNSET:
            field_dict["firstName"] = first_name
        if surname is not UNSET:
            field_dict["surname"] = surname
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if start_date is not UNSET:
            field_dict["startDate"] = start_date
        if last_paid_date is not UNSET:
            field_dict["lastPaidDate"] = last_paid_date
        if last_pay_period_ending is not UNSET:
            field_dict["lastPayPeriodEnding"] = last_pay_period_ending
        if calculated_weeks is not UNSET:
            field_dict["calculatedWeeks"] = calculated_weeks
        if location is not UNSET:
            field_dict["location"] = location
        if leave_category_name is not UNSET:
            field_dict["leaveCategoryName"] = leave_category_name
        if approved_leave_amount is not UNSET:
            field_dict["approvedLeaveAmount"] = approved_leave_amount
        if accrued_amount is not UNSET:
            field_dict["accruedAmount"] = accrued_amount
        if leave_value is not UNSET:
            field_dict["leaveValue"] = leave_value
        if approved_leave_amount_in_hours is not UNSET:
            field_dict["approvedLeaveAmountInHours"] = approved_leave_amount_in_hours
        if unit_type is not UNSET:
            field_dict["unitType"] = unit_type
        if accrued_amount_in_hours is not UNSET:
            field_dict["accruedAmountInHours"] = accrued_amount_in_hours

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        leave_loading_dollar_value = d.pop("leaveLoadingDollarValue", UNSET)

        employee_id = d.pop("employeeId", UNSET)

        first_name = d.pop("firstName", UNSET)

        surname = d.pop("surname", UNSET)

        external_id = d.pop("externalId", UNSET)

        _start_date = d.pop("startDate", UNSET)
        start_date: Union[Unset, datetime.datetime]
        if isinstance(_start_date, Unset):
            start_date = UNSET
        else:
            start_date = isoparse(_start_date)

        _last_paid_date = d.pop("lastPaidDate", UNSET)
        last_paid_date: Union[Unset, datetime.datetime]
        if isinstance(_last_paid_date, Unset):
            last_paid_date = UNSET
        else:
            last_paid_date = isoparse(_last_paid_date)

        _last_pay_period_ending = d.pop("lastPayPeriodEnding", UNSET)
        last_pay_period_ending: Union[Unset, datetime.datetime]
        if isinstance(_last_pay_period_ending, Unset):
            last_pay_period_ending = UNSET
        else:
            last_pay_period_ending = isoparse(_last_pay_period_ending)

        calculated_weeks = d.pop("calculatedWeeks", UNSET)

        location = d.pop("location", UNSET)

        leave_category_name = d.pop("leaveCategoryName", UNSET)

        approved_leave_amount = d.pop("approvedLeaveAmount", UNSET)

        accrued_amount = d.pop("accruedAmount", UNSET)

        leave_value = d.pop("leaveValue", UNSET)

        approved_leave_amount_in_hours = d.pop("approvedLeaveAmountInHours", UNSET)

        _unit_type = d.pop("unitType", UNSET)
        unit_type: Union[Unset, AuLeaveLiabilityExportModelLeaveUnitTypeEnum]
        if isinstance(_unit_type, Unset):
            unit_type = UNSET
        else:
            unit_type = AuLeaveLiabilityExportModelLeaveUnitTypeEnum(_unit_type)

        accrued_amount_in_hours = d.pop("accruedAmountInHours", UNSET)

        au_leave_liability_export_model = cls(
            leave_loading_dollar_value=leave_loading_dollar_value,
            employee_id=employee_id,
            first_name=first_name,
            surname=surname,
            external_id=external_id,
            start_date=start_date,
            last_paid_date=last_paid_date,
            last_pay_period_ending=last_pay_period_ending,
            calculated_weeks=calculated_weeks,
            location=location,
            leave_category_name=leave_category_name,
            approved_leave_amount=approved_leave_amount,
            accrued_amount=accrued_amount,
            leave_value=leave_value,
            approved_leave_amount_in_hours=approved_leave_amount_in_hours,
            unit_type=unit_type,
            accrued_amount_in_hours=accrued_amount_in_hours,
        )

        au_leave_liability_export_model.additional_properties = d
        return au_leave_liability_export_model

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
