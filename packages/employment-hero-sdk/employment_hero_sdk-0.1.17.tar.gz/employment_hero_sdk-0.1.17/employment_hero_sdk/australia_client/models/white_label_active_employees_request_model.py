import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="WhiteLabelActiveEmployeesRequestModel")


@_attrs_define
class WhiteLabelActiveEmployeesRequestModel:
    """
    Attributes:
        email_addresses (Union[Unset, str]):
        include_inactive_businesses (Union[Unset, bool]):
        from_date (Union[Unset, datetime.datetime]):
        to_date (Union[Unset, datetime.datetime]):
        location_id (Union[Unset, int]):
        employing_entity_id (Union[Unset, int]):
    """

    email_addresses: Union[Unset, str] = UNSET
    include_inactive_businesses: Union[Unset, bool] = UNSET
    from_date: Union[Unset, datetime.datetime] = UNSET
    to_date: Union[Unset, datetime.datetime] = UNSET
    location_id: Union[Unset, int] = UNSET
    employing_entity_id: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        email_addresses = self.email_addresses

        include_inactive_businesses = self.include_inactive_businesses

        from_date: Union[Unset, str] = UNSET
        if not isinstance(self.from_date, Unset):
            from_date = self.from_date.isoformat()

        to_date: Union[Unset, str] = UNSET
        if not isinstance(self.to_date, Unset):
            to_date = self.to_date.isoformat()

        location_id = self.location_id

        employing_entity_id = self.employing_entity_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if email_addresses is not UNSET:
            field_dict["emailAddresses"] = email_addresses
        if include_inactive_businesses is not UNSET:
            field_dict["includeInactiveBusinesses"] = include_inactive_businesses
        if from_date is not UNSET:
            field_dict["fromDate"] = from_date
        if to_date is not UNSET:
            field_dict["toDate"] = to_date
        if location_id is not UNSET:
            field_dict["locationId"] = location_id
        if employing_entity_id is not UNSET:
            field_dict["employingEntityId"] = employing_entity_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        email_addresses = d.pop("emailAddresses", UNSET)

        include_inactive_businesses = d.pop("includeInactiveBusinesses", UNSET)

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

        location_id = d.pop("locationId", UNSET)

        employing_entity_id = d.pop("employingEntityId", UNSET)

        white_label_active_employees_request_model = cls(
            email_addresses=email_addresses,
            include_inactive_businesses=include_inactive_businesses,
            from_date=from_date,
            to_date=to_date,
            location_id=location_id,
            employing_entity_id=employing_entity_id,
        )

        white_label_active_employees_request_model.additional_properties = d
        return white_label_active_employees_request_model

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
