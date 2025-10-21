import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="SwapShiftModel")


@_attrs_define
class SwapShiftModel:
    """
    Attributes:
        roster_shift_id (Union[Unset, int]):
        from_employee_id (Union[Unset, int]):
        to_employee_id (Union[Unset, int]):
        note (Union[Unset, str]):
        date_created (Union[Unset, datetime.datetime]):
        created_by_user_id (Union[Unset, int]):
        token (Union[Unset, str]):
    """

    roster_shift_id: Union[Unset, int] = UNSET
    from_employee_id: Union[Unset, int] = UNSET
    to_employee_id: Union[Unset, int] = UNSET
    note: Union[Unset, str] = UNSET
    date_created: Union[Unset, datetime.datetime] = UNSET
    created_by_user_id: Union[Unset, int] = UNSET
    token: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        roster_shift_id = self.roster_shift_id

        from_employee_id = self.from_employee_id

        to_employee_id = self.to_employee_id

        note = self.note

        date_created: Union[Unset, str] = UNSET
        if not isinstance(self.date_created, Unset):
            date_created = self.date_created.isoformat()

        created_by_user_id = self.created_by_user_id

        token = self.token

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if roster_shift_id is not UNSET:
            field_dict["rosterShiftId"] = roster_shift_id
        if from_employee_id is not UNSET:
            field_dict["fromEmployeeId"] = from_employee_id
        if to_employee_id is not UNSET:
            field_dict["toEmployeeId"] = to_employee_id
        if note is not UNSET:
            field_dict["note"] = note
        if date_created is not UNSET:
            field_dict["dateCreated"] = date_created
        if created_by_user_id is not UNSET:
            field_dict["createdByUserId"] = created_by_user_id
        if token is not UNSET:
            field_dict["token"] = token

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        roster_shift_id = d.pop("rosterShiftId", UNSET)

        from_employee_id = d.pop("fromEmployeeId", UNSET)

        to_employee_id = d.pop("toEmployeeId", UNSET)

        note = d.pop("note", UNSET)

        _date_created = d.pop("dateCreated", UNSET)
        date_created: Union[Unset, datetime.datetime]
        if isinstance(_date_created, Unset):
            date_created = UNSET
        else:
            date_created = isoparse(_date_created)

        created_by_user_id = d.pop("createdByUserId", UNSET)

        token = d.pop("token", UNSET)

        swap_shift_model = cls(
            roster_shift_id=roster_shift_id,
            from_employee_id=from_employee_id,
            to_employee_id=to_employee_id,
            note=note,
            date_created=date_created,
            created_by_user_id=created_by_user_id,
            token=token,
        )

        swap_shift_model.additional_properties = d
        return swap_shift_model

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
