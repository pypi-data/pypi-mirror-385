import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="PayRateScheduleModel")


@_attrs_define
class PayRateScheduleModel:
    """
    Attributes:
        id (Union[Unset, int]):
        employee_id (Union[Unset, int]):
        rate (Union[Unset, float]):
        rate_unit (Union[Unset, str]):
        commencement_date (Union[Unset, datetime.datetime]):
    """

    id: Union[Unset, int] = UNSET
    employee_id: Union[Unset, int] = UNSET
    rate: Union[Unset, float] = UNSET
    rate_unit: Union[Unset, str] = UNSET
    commencement_date: Union[Unset, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        employee_id = self.employee_id

        rate = self.rate

        rate_unit = self.rate_unit

        commencement_date: Union[Unset, str] = UNSET
        if not isinstance(self.commencement_date, Unset):
            commencement_date = self.commencement_date.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if rate is not UNSET:
            field_dict["rate"] = rate
        if rate_unit is not UNSET:
            field_dict["rateUnit"] = rate_unit
        if commencement_date is not UNSET:
            field_dict["commencementDate"] = commencement_date

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        employee_id = d.pop("employeeId", UNSET)

        rate = d.pop("rate", UNSET)

        rate_unit = d.pop("rateUnit", UNSET)

        _commencement_date = d.pop("commencementDate", UNSET)
        commencement_date: Union[Unset, datetime.datetime]
        if isinstance(_commencement_date, Unset):
            commencement_date = UNSET
        else:
            commencement_date = isoparse(_commencement_date)

        pay_rate_schedule_model = cls(
            id=id,
            employee_id=employee_id,
            rate=rate,
            rate_unit=rate_unit,
            commencement_date=commencement_date,
        )

        pay_rate_schedule_model.additional_properties = d
        return pay_rate_schedule_model

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
