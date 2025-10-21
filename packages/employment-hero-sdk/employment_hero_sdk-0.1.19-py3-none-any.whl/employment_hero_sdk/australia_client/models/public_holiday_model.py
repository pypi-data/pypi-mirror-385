import datetime
from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="PublicHolidayModel")


@_attrs_define
class PublicHolidayModel:
    """
    Attributes:
        id (Union[Unset, int]):
        date (Union[Unset, datetime.datetime]):
        states (Union[Unset, List[str]]):
        location_ids (Union[Unset, List[int]]):
        description (Union[Unset, str]):
        note (Union[Unset, str]):
        is_system (Union[Unset, bool]):
        not_a_public_holiday (Union[Unset, bool]):
        mondayised_alternative_to_id (Union[Unset, int]):
    """

    id: Union[Unset, int] = UNSET
    date: Union[Unset, datetime.datetime] = UNSET
    states: Union[Unset, List[str]] = UNSET
    location_ids: Union[Unset, List[int]] = UNSET
    description: Union[Unset, str] = UNSET
    note: Union[Unset, str] = UNSET
    is_system: Union[Unset, bool] = UNSET
    not_a_public_holiday: Union[Unset, bool] = UNSET
    mondayised_alternative_to_id: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        date: Union[Unset, str] = UNSET
        if not isinstance(self.date, Unset):
            date = self.date.isoformat()

        states: Union[Unset, List[str]] = UNSET
        if not isinstance(self.states, Unset):
            states = self.states

        location_ids: Union[Unset, List[int]] = UNSET
        if not isinstance(self.location_ids, Unset):
            location_ids = self.location_ids

        description = self.description

        note = self.note

        is_system = self.is_system

        not_a_public_holiday = self.not_a_public_holiday

        mondayised_alternative_to_id = self.mondayised_alternative_to_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if date is not UNSET:
            field_dict["date"] = date
        if states is not UNSET:
            field_dict["states"] = states
        if location_ids is not UNSET:
            field_dict["locationIds"] = location_ids
        if description is not UNSET:
            field_dict["description"] = description
        if note is not UNSET:
            field_dict["note"] = note
        if is_system is not UNSET:
            field_dict["isSystem"] = is_system
        if not_a_public_holiday is not UNSET:
            field_dict["notAPublicHoliday"] = not_a_public_holiday
        if mondayised_alternative_to_id is not UNSET:
            field_dict["mondayisedAlternativeToId"] = mondayised_alternative_to_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        _date = d.pop("date", UNSET)
        date: Union[Unset, datetime.datetime]
        if isinstance(_date, Unset):
            date = UNSET
        else:
            date = isoparse(_date)

        states = cast(List[str], d.pop("states", UNSET))

        location_ids = cast(List[int], d.pop("locationIds", UNSET))

        description = d.pop("description", UNSET)

        note = d.pop("note", UNSET)

        is_system = d.pop("isSystem", UNSET)

        not_a_public_holiday = d.pop("notAPublicHoliday", UNSET)

        mondayised_alternative_to_id = d.pop("mondayisedAlternativeToId", UNSET)

        public_holiday_model = cls(
            id=id,
            date=date,
            states=states,
            location_ids=location_ids,
            description=description,
            note=note,
            is_system=is_system,
            not_a_public_holiday=not_a_public_holiday,
            mondayised_alternative_to_id=mondayised_alternative_to_id,
        )

        public_holiday_model.additional_properties = d
        return public_holiday_model

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
