import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.unavailability_save_model_nullable_day_of_week import UnavailabilitySaveModelNullableDayOfWeek
from ..types import UNSET, Unset

T = TypeVar("T", bound="UnavailabilitySaveModel")


@_attrs_define
class UnavailabilitySaveModel:
    """
    Attributes:
        id (Union[Unset, int]):
        employee_id (Union[Unset, int]):
        from_date (Union[Unset, datetime.datetime]):
        to_date (Union[Unset, datetime.datetime]):
        end_date (Union[Unset, datetime.datetime]):
        reason (Union[Unset, str]):
        recurring (Union[Unset, bool]):
        recurring_day (Union[Unset, UnavailabilitySaveModelNullableDayOfWeek]):
    """

    id: Union[Unset, int] = UNSET
    employee_id: Union[Unset, int] = UNSET
    from_date: Union[Unset, datetime.datetime] = UNSET
    to_date: Union[Unset, datetime.datetime] = UNSET
    end_date: Union[Unset, datetime.datetime] = UNSET
    reason: Union[Unset, str] = UNSET
    recurring: Union[Unset, bool] = UNSET
    recurring_day: Union[Unset, UnavailabilitySaveModelNullableDayOfWeek] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        employee_id = self.employee_id

        from_date: Union[Unset, str] = UNSET
        if not isinstance(self.from_date, Unset):
            from_date = self.from_date.isoformat()

        to_date: Union[Unset, str] = UNSET
        if not isinstance(self.to_date, Unset):
            to_date = self.to_date.isoformat()

        end_date: Union[Unset, str] = UNSET
        if not isinstance(self.end_date, Unset):
            end_date = self.end_date.isoformat()

        reason = self.reason

        recurring = self.recurring

        recurring_day: Union[Unset, str] = UNSET
        if not isinstance(self.recurring_day, Unset):
            recurring_day = self.recurring_day.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if from_date is not UNSET:
            field_dict["fromDate"] = from_date
        if to_date is not UNSET:
            field_dict["toDate"] = to_date
        if end_date is not UNSET:
            field_dict["endDate"] = end_date
        if reason is not UNSET:
            field_dict["reason"] = reason
        if recurring is not UNSET:
            field_dict["recurring"] = recurring
        if recurring_day is not UNSET:
            field_dict["recurringDay"] = recurring_day

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        employee_id = d.pop("employeeId", UNSET)

        _from_date = d.pop("fromDate", UNSET)
        from_date: Union[Unset, datetime.datetime]
        if isinstance(_from_date, Unset):
            from_date = UNSET
        else:
            from_date = isoparse(_from_date)

        _to_date = d.pop("toDate", UNSET)
        to_date: Union[Unset, datetime.datetime]
        if isinstance(_to_date, Unset):
            to_date = UNSET
        else:
            to_date = isoparse(_to_date)

        _end_date = d.pop("endDate", UNSET)
        end_date: Union[Unset, datetime.datetime]
        if isinstance(_end_date, Unset):
            end_date = UNSET
        else:
            end_date = isoparse(_end_date)

        reason = d.pop("reason", UNSET)

        recurring = d.pop("recurring", UNSET)

        _recurring_day = d.pop("recurringDay", UNSET)
        recurring_day: Union[Unset, UnavailabilitySaveModelNullableDayOfWeek]
        if isinstance(_recurring_day, Unset):
            recurring_day = UNSET
        else:
            recurring_day = UnavailabilitySaveModelNullableDayOfWeek(_recurring_day)

        unavailability_save_model = cls(
            id=id,
            employee_id=employee_id,
            from_date=from_date,
            to_date=to_date,
            end_date=end_date,
            reason=reason,
            recurring=recurring,
            recurring_day=recurring_day,
        )

        unavailability_save_model.additional_properties = d
        return unavailability_save_model

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
