import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.super_accrual_export_model_nullable_super_interchange_status import (
    SuperAccrualExportModelNullableSuperInterchangeStatus,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="SuperAccrualExportModel")


@_attrs_define
class SuperAccrualExportModel:
    """
    Attributes:
        location_id (Union[Unset, int]):
        location_name (Union[Unset, str]):
        employee_id (Union[Unset, int]):
        first_name (Union[Unset, str]):
        surname (Union[Unset, str]):
        external_id (Union[Unset, str]):
        accrual_date (Union[Unset, datetime.datetime]):
        accrual_type (Union[Unset, str]):
        accrual_amount (Union[Unset, float]):
        batch_id (Union[Unset, int]):
        status (Union[Unset, SuperAccrualExportModelNullableSuperInterchangeStatus]):
    """

    location_id: Union[Unset, int] = UNSET
    location_name: Union[Unset, str] = UNSET
    employee_id: Union[Unset, int] = UNSET
    first_name: Union[Unset, str] = UNSET
    surname: Union[Unset, str] = UNSET
    external_id: Union[Unset, str] = UNSET
    accrual_date: Union[Unset, datetime.datetime] = UNSET
    accrual_type: Union[Unset, str] = UNSET
    accrual_amount: Union[Unset, float] = UNSET
    batch_id: Union[Unset, int] = UNSET
    status: Union[Unset, SuperAccrualExportModelNullableSuperInterchangeStatus] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        location_id = self.location_id

        location_name = self.location_name

        employee_id = self.employee_id

        first_name = self.first_name

        surname = self.surname

        external_id = self.external_id

        accrual_date: Union[Unset, str] = UNSET
        if not isinstance(self.accrual_date, Unset):
            accrual_date = self.accrual_date.isoformat()

        accrual_type = self.accrual_type

        accrual_amount = self.accrual_amount

        batch_id = self.batch_id

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if location_id is not UNSET:
            field_dict["locationId"] = location_id
        if location_name is not UNSET:
            field_dict["locationName"] = location_name
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if first_name is not UNSET:
            field_dict["firstName"] = first_name
        if surname is not UNSET:
            field_dict["surname"] = surname
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if accrual_date is not UNSET:
            field_dict["accrualDate"] = accrual_date
        if accrual_type is not UNSET:
            field_dict["accrualType"] = accrual_type
        if accrual_amount is not UNSET:
            field_dict["accrualAmount"] = accrual_amount
        if batch_id is not UNSET:
            field_dict["batchId"] = batch_id
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        location_id = d.pop("locationId", UNSET)

        location_name = d.pop("locationName", UNSET)

        employee_id = d.pop("employeeId", UNSET)

        first_name = d.pop("firstName", UNSET)

        surname = d.pop("surname", UNSET)

        external_id = d.pop("externalId", UNSET)

        _accrual_date = d.pop("accrualDate", UNSET)
        accrual_date: Union[Unset, datetime.datetime]
        if isinstance(_accrual_date, Unset):
            accrual_date = UNSET
        else:
            accrual_date = isoparse(_accrual_date)

        accrual_type = d.pop("accrualType", UNSET)

        accrual_amount = d.pop("accrualAmount", UNSET)

        batch_id = d.pop("batchId", UNSET)

        _status = d.pop("status", UNSET)
        status: Union[Unset, SuperAccrualExportModelNullableSuperInterchangeStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = SuperAccrualExportModelNullableSuperInterchangeStatus(_status)

        super_accrual_export_model = cls(
            location_id=location_id,
            location_name=location_name,
            employee_id=employee_id,
            first_name=first_name,
            surname=surname,
            external_id=external_id,
            accrual_date=accrual_date,
            accrual_type=accrual_type,
            accrual_amount=accrual_amount,
            batch_id=batch_id,
            status=status,
        )

        super_accrual_export_model.additional_properties = d
        return super_accrual_export_model

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
