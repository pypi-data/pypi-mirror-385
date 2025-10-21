from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.au_leave_balances_export_model_leave_unit_type_enum import AuLeaveBalancesExportModelLeaveUnitTypeEnum
from ..types import UNSET, Unset

T = TypeVar("T", bound="AuLeaveBalancesExportModel")


@_attrs_define
class AuLeaveBalancesExportModel:
    """
    Attributes:
        accrued_amount_in_days (Union[Unset, float]):
        leave_value (Union[Unset, float]):
        loading_value (Union[Unset, float]):
        leave_plus_loading (Union[Unset, float]):
        employee_id (Union[Unset, int]):
        external_id (Union[Unset, str]):
        first_name (Union[Unset, str]):
        surname (Union[Unset, str]):
        location (Union[Unset, str]):
        leave_category_name (Union[Unset, str]):
        accrued_amount (Union[Unset, float]):
        accrued_amount_in_hours (Union[Unset, float]):
        unit_type (Union[Unset, AuLeaveBalancesExportModelLeaveUnitTypeEnum]):
    """

    accrued_amount_in_days: Union[Unset, float] = UNSET
    leave_value: Union[Unset, float] = UNSET
    loading_value: Union[Unset, float] = UNSET
    leave_plus_loading: Union[Unset, float] = UNSET
    employee_id: Union[Unset, int] = UNSET
    external_id: Union[Unset, str] = UNSET
    first_name: Union[Unset, str] = UNSET
    surname: Union[Unset, str] = UNSET
    location: Union[Unset, str] = UNSET
    leave_category_name: Union[Unset, str] = UNSET
    accrued_amount: Union[Unset, float] = UNSET
    accrued_amount_in_hours: Union[Unset, float] = UNSET
    unit_type: Union[Unset, AuLeaveBalancesExportModelLeaveUnitTypeEnum] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        accrued_amount_in_days = self.accrued_amount_in_days

        leave_value = self.leave_value

        loading_value = self.loading_value

        leave_plus_loading = self.leave_plus_loading

        employee_id = self.employee_id

        external_id = self.external_id

        first_name = self.first_name

        surname = self.surname

        location = self.location

        leave_category_name = self.leave_category_name

        accrued_amount = self.accrued_amount

        accrued_amount_in_hours = self.accrued_amount_in_hours

        unit_type: Union[Unset, str] = UNSET
        if not isinstance(self.unit_type, Unset):
            unit_type = self.unit_type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if accrued_amount_in_days is not UNSET:
            field_dict["accruedAmountInDays"] = accrued_amount_in_days
        if leave_value is not UNSET:
            field_dict["leaveValue"] = leave_value
        if loading_value is not UNSET:
            field_dict["loadingValue"] = loading_value
        if leave_plus_loading is not UNSET:
            field_dict["leavePlusLoading"] = leave_plus_loading
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if first_name is not UNSET:
            field_dict["firstName"] = first_name
        if surname is not UNSET:
            field_dict["surname"] = surname
        if location is not UNSET:
            field_dict["location"] = location
        if leave_category_name is not UNSET:
            field_dict["leaveCategoryName"] = leave_category_name
        if accrued_amount is not UNSET:
            field_dict["accruedAmount"] = accrued_amount
        if accrued_amount_in_hours is not UNSET:
            field_dict["accruedAmountInHours"] = accrued_amount_in_hours
        if unit_type is not UNSET:
            field_dict["unitType"] = unit_type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        accrued_amount_in_days = d.pop("accruedAmountInDays", UNSET)

        leave_value = d.pop("leaveValue", UNSET)

        loading_value = d.pop("loadingValue", UNSET)

        leave_plus_loading = d.pop("leavePlusLoading", UNSET)

        employee_id = d.pop("employeeId", UNSET)

        external_id = d.pop("externalId", UNSET)

        first_name = d.pop("firstName", UNSET)

        surname = d.pop("surname", UNSET)

        location = d.pop("location", UNSET)

        leave_category_name = d.pop("leaveCategoryName", UNSET)

        accrued_amount = d.pop("accruedAmount", UNSET)

        accrued_amount_in_hours = d.pop("accruedAmountInHours", UNSET)

        _unit_type = d.pop("unitType", UNSET)
        unit_type: Union[Unset, AuLeaveBalancesExportModelLeaveUnitTypeEnum]
        if isinstance(_unit_type, Unset):
            unit_type = UNSET
        else:
            unit_type = AuLeaveBalancesExportModelLeaveUnitTypeEnum(_unit_type)

        au_leave_balances_export_model = cls(
            accrued_amount_in_days=accrued_amount_in_days,
            leave_value=leave_value,
            loading_value=loading_value,
            leave_plus_loading=leave_plus_loading,
            employee_id=employee_id,
            external_id=external_id,
            first_name=first_name,
            surname=surname,
            location=location,
            leave_category_name=leave_category_name,
            accrued_amount=accrued_amount,
            accrued_amount_in_hours=accrued_amount_in_hours,
            unit_type=unit_type,
        )

        au_leave_balances_export_model.additional_properties = d
        return au_leave_balances_export_model

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
