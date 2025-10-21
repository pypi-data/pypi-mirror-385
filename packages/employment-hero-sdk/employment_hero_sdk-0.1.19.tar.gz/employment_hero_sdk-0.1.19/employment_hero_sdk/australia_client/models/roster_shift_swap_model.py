import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="RosterShiftSwapModel")


@_attrs_define
class RosterShiftSwapModel:
    """
    Attributes:
        id (Union[Unset, int]):
        from_employee (Union[Unset, str]):
        to_employee (Union[Unset, str]):
        from_employee_id (Union[Unset, int]):
        to_employee_id (Union[Unset, int]):
        date_created (Union[Unset, datetime.datetime]):
        note (Union[Unset, str]):
        rejected_reason (Union[Unset, str]):
        status (Union[Unset, int]):
        status_description (Union[Unset, str]):
    """

    id: Union[Unset, int] = UNSET
    from_employee: Union[Unset, str] = UNSET
    to_employee: Union[Unset, str] = UNSET
    from_employee_id: Union[Unset, int] = UNSET
    to_employee_id: Union[Unset, int] = UNSET
    date_created: Union[Unset, datetime.datetime] = UNSET
    note: Union[Unset, str] = UNSET
    rejected_reason: Union[Unset, str] = UNSET
    status: Union[Unset, int] = UNSET
    status_description: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        from_employee = self.from_employee

        to_employee = self.to_employee

        from_employee_id = self.from_employee_id

        to_employee_id = self.to_employee_id

        date_created: Union[Unset, str] = UNSET
        if not isinstance(self.date_created, Unset):
            date_created = self.date_created.isoformat()

        note = self.note

        rejected_reason = self.rejected_reason

        status = self.status

        status_description = self.status_description

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if from_employee is not UNSET:
            field_dict["fromEmployee"] = from_employee
        if to_employee is not UNSET:
            field_dict["toEmployee"] = to_employee
        if from_employee_id is not UNSET:
            field_dict["fromEmployeeId"] = from_employee_id
        if to_employee_id is not UNSET:
            field_dict["toEmployeeId"] = to_employee_id
        if date_created is not UNSET:
            field_dict["dateCreated"] = date_created
        if note is not UNSET:
            field_dict["note"] = note
        if rejected_reason is not UNSET:
            field_dict["rejectedReason"] = rejected_reason
        if status is not UNSET:
            field_dict["status"] = status
        if status_description is not UNSET:
            field_dict["statusDescription"] = status_description

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        from_employee = d.pop("fromEmployee", UNSET)

        to_employee = d.pop("toEmployee", UNSET)

        from_employee_id = d.pop("fromEmployeeId", UNSET)

        to_employee_id = d.pop("toEmployeeId", UNSET)

        _date_created = d.pop("dateCreated", UNSET)
        date_created: Union[Unset, datetime.datetime]
        if isinstance(_date_created, Unset):
            date_created = UNSET
        else:
            date_created = isoparse(_date_created)

        note = d.pop("note", UNSET)

        rejected_reason = d.pop("rejectedReason", UNSET)

        status = d.pop("status", UNSET)

        status_description = d.pop("statusDescription", UNSET)

        roster_shift_swap_model = cls(
            id=id,
            from_employee=from_employee,
            to_employee=to_employee,
            from_employee_id=from_employee_id,
            to_employee_id=to_employee_id,
            date_created=date_created,
            note=note,
            rejected_reason=rejected_reason,
            status=status,
            status_description=status_description,
        )

        roster_shift_swap_model.additional_properties = d
        return roster_shift_swap_model

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
