import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetShiftsModel")


@_attrs_define
class GetShiftsModel:
    """
    Attributes:
        kiosk_id (Union[Unset, int]):
        location_id (Union[Unset, int]):
        employee_id (Union[Unset, int]):
        from_date_utc (Union[Unset, datetime.datetime]):
        to_date_utc (Union[Unset, datetime.datetime]):
    """

    kiosk_id: Union[Unset, int] = UNSET
    location_id: Union[Unset, int] = UNSET
    employee_id: Union[Unset, int] = UNSET
    from_date_utc: Union[Unset, datetime.datetime] = UNSET
    to_date_utc: Union[Unset, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        kiosk_id = self.kiosk_id

        location_id = self.location_id

        employee_id = self.employee_id

        from_date_utc: Union[Unset, str] = UNSET
        if not isinstance(self.from_date_utc, Unset):
            from_date_utc = self.from_date_utc.isoformat()

        to_date_utc: Union[Unset, str] = UNSET
        if not isinstance(self.to_date_utc, Unset):
            to_date_utc = self.to_date_utc.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if kiosk_id is not UNSET:
            field_dict["kioskId"] = kiosk_id
        if location_id is not UNSET:
            field_dict["locationId"] = location_id
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if from_date_utc is not UNSET:
            field_dict["fromDateUtc"] = from_date_utc
        if to_date_utc is not UNSET:
            field_dict["toDateUtc"] = to_date_utc

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        kiosk_id = d.pop("kioskId", UNSET)

        location_id = d.pop("locationId", UNSET)

        employee_id = d.pop("employeeId", UNSET)

        _from_date_utc = d.pop("fromDateUtc", UNSET)
        from_date_utc: Union[Unset, datetime.datetime]
        if isinstance(_from_date_utc, Unset):
            from_date_utc = UNSET
        else:
            from_date_utc = isoparse(_from_date_utc)

        _to_date_utc = d.pop("toDateUtc", UNSET)
        to_date_utc: Union[Unset, datetime.datetime]
        if isinstance(_to_date_utc, Unset):
            to_date_utc = UNSET
        else:
            to_date_utc = isoparse(_to_date_utc)

        get_shifts_model = cls(
            kiosk_id=kiosk_id,
            location_id=location_id,
            employee_id=employee_id,
            from_date_utc=from_date_utc,
            to_date_utc=to_date_utc,
        )

        get_shifts_model.additional_properties = d
        return get_shifts_model

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
