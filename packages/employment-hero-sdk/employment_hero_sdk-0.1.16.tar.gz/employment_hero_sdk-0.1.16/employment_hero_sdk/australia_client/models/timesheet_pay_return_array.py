import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="TimesheetPayReturnArray")


@_attrs_define
class TimesheetPayReturnArray:
    """
    Attributes:
        id (Union[Unset, int]):
        timesheet (Union[Unset, int]):
        pay_rule (Union[Unset, int]):
        overridden (Union[Unset, bool]):
        value (Union[Unset, float]):
        cost (Union[Unset, float]):
        override_comment (Union[Unset, str]):
        pay_cycle_id (Union[Unset, int]):
        created (Union[Unset, datetime.datetime]):
        modified (Union[Unset, datetime.datetime]):
    """

    id: Union[Unset, int] = UNSET
    timesheet: Union[Unset, int] = UNSET
    pay_rule: Union[Unset, int] = UNSET
    overridden: Union[Unset, bool] = UNSET
    value: Union[Unset, float] = UNSET
    cost: Union[Unset, float] = UNSET
    override_comment: Union[Unset, str] = UNSET
    pay_cycle_id: Union[Unset, int] = UNSET
    created: Union[Unset, datetime.datetime] = UNSET
    modified: Union[Unset, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        timesheet = self.timesheet

        pay_rule = self.pay_rule

        overridden = self.overridden

        value = self.value

        cost = self.cost

        override_comment = self.override_comment

        pay_cycle_id = self.pay_cycle_id

        created: Union[Unset, str] = UNSET
        if not isinstance(self.created, Unset):
            created = self.created.isoformat()

        modified: Union[Unset, str] = UNSET
        if not isinstance(self.modified, Unset):
            modified = self.modified.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if timesheet is not UNSET:
            field_dict["timesheet"] = timesheet
        if pay_rule is not UNSET:
            field_dict["payRule"] = pay_rule
        if overridden is not UNSET:
            field_dict["overridden"] = overridden
        if value is not UNSET:
            field_dict["value"] = value
        if cost is not UNSET:
            field_dict["cost"] = cost
        if override_comment is not UNSET:
            field_dict["overrideComment"] = override_comment
        if pay_cycle_id is not UNSET:
            field_dict["payCycleId"] = pay_cycle_id
        if created is not UNSET:
            field_dict["created"] = created
        if modified is not UNSET:
            field_dict["modified"] = modified

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        timesheet = d.pop("timesheet", UNSET)

        pay_rule = d.pop("payRule", UNSET)

        overridden = d.pop("overridden", UNSET)

        value = d.pop("value", UNSET)

        cost = d.pop("cost", UNSET)

        override_comment = d.pop("overrideComment", UNSET)

        pay_cycle_id = d.pop("payCycleId", UNSET)

        _created = d.pop("created", UNSET)
        created: Union[Unset, datetime.datetime]
        if isinstance(_created, Unset):
            created = UNSET
        else:
            created = isoparse(_created)

        _modified = d.pop("modified", UNSET)
        modified: Union[Unset, datetime.datetime]
        if isinstance(_modified, Unset):
            modified = UNSET
        else:
            modified = isoparse(_modified)

        timesheet_pay_return_array = cls(
            id=id,
            timesheet=timesheet,
            pay_rule=pay_rule,
            overridden=overridden,
            value=value,
            cost=cost,
            override_comment=override_comment,
            pay_cycle_id=pay_cycle_id,
            created=created,
            modified=modified,
        )

        timesheet_pay_return_array.additional_properties = d
        return timesheet_pay_return_array

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
