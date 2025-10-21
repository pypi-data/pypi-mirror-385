import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="EssCurrentTimesheetsModel")


@_attrs_define
class EssCurrentTimesheetsModel:
    """
    Attributes:
        period_starting (Union[Unset, datetime.datetime]):
        period_ending (Union[Unset, datetime.datetime]):
        submitted_count (Union[Unset, int]):
        approved_count (Union[Unset, int]):
        rejected_count (Union[Unset, int]):
        processed_count (Union[Unset, int]):
        duration_in_minutes (Union[Unset, float]):
    """

    period_starting: Union[Unset, datetime.datetime] = UNSET
    period_ending: Union[Unset, datetime.datetime] = UNSET
    submitted_count: Union[Unset, int] = UNSET
    approved_count: Union[Unset, int] = UNSET
    rejected_count: Union[Unset, int] = UNSET
    processed_count: Union[Unset, int] = UNSET
    duration_in_minutes: Union[Unset, float] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        period_starting: Union[Unset, str] = UNSET
        if not isinstance(self.period_starting, Unset):
            period_starting = self.period_starting.isoformat()

        period_ending: Union[Unset, str] = UNSET
        if not isinstance(self.period_ending, Unset):
            period_ending = self.period_ending.isoformat()

        submitted_count = self.submitted_count

        approved_count = self.approved_count

        rejected_count = self.rejected_count

        processed_count = self.processed_count

        duration_in_minutes = self.duration_in_minutes

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if period_starting is not UNSET:
            field_dict["periodStarting"] = period_starting
        if period_ending is not UNSET:
            field_dict["periodEnding"] = period_ending
        if submitted_count is not UNSET:
            field_dict["submittedCount"] = submitted_count
        if approved_count is not UNSET:
            field_dict["approvedCount"] = approved_count
        if rejected_count is not UNSET:
            field_dict["rejectedCount"] = rejected_count
        if processed_count is not UNSET:
            field_dict["processedCount"] = processed_count
        if duration_in_minutes is not UNSET:
            field_dict["durationInMinutes"] = duration_in_minutes

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _period_starting = d.pop("periodStarting", UNSET)
        period_starting: Union[Unset, datetime.datetime]
        if isinstance(_period_starting, Unset):
            period_starting = UNSET
        else:
            period_starting = isoparse(_period_starting)

        _period_ending = d.pop("periodEnding", UNSET)
        period_ending: Union[Unset, datetime.datetime]
        if isinstance(_period_ending, Unset):
            period_ending = UNSET
        else:
            period_ending = isoparse(_period_ending)

        submitted_count = d.pop("submittedCount", UNSET)

        approved_count = d.pop("approvedCount", UNSET)

        rejected_count = d.pop("rejectedCount", UNSET)

        processed_count = d.pop("processedCount", UNSET)

        duration_in_minutes = d.pop("durationInMinutes", UNSET)

        ess_current_timesheets_model = cls(
            period_starting=period_starting,
            period_ending=period_ending,
            submitted_count=submitted_count,
            approved_count=approved_count,
            rejected_count=rejected_count,
            processed_count=processed_count,
            duration_in_minutes=duration_in_minutes,
        )

        ess_current_timesheets_model.additional_properties = d
        return ess_current_timesheets_model

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
