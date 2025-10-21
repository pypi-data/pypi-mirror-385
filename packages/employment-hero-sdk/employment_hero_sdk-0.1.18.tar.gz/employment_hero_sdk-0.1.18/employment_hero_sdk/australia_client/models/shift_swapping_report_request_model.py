import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.shift_swapping_report_request_model_roster_shift_swap_status_enum import (
    ShiftSwappingReportRequestModelRosterShiftSwapStatusEnum,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="ShiftSwappingReportRequestModel")


@_attrs_define
class ShiftSwappingReportRequestModel:
    """
    Attributes:
        from_employee_id (Union[Unset, int]):
        to_employee_id (Union[Unset, int]):
        include_costs (Union[Unset, bool]):
        statuses (Union[Unset, List[ShiftSwappingReportRequestModelRosterShiftSwapStatusEnum]]):
        from_date (Union[Unset, datetime.datetime]):
        to_date (Union[Unset, datetime.datetime]):
        location_id (Union[Unset, int]):
        employing_entity_id (Union[Unset, int]):
    """

    from_employee_id: Union[Unset, int] = UNSET
    to_employee_id: Union[Unset, int] = UNSET
    include_costs: Union[Unset, bool] = UNSET
    statuses: Union[Unset, List[ShiftSwappingReportRequestModelRosterShiftSwapStatusEnum]] = UNSET
    from_date: Union[Unset, datetime.datetime] = UNSET
    to_date: Union[Unset, datetime.datetime] = UNSET
    location_id: Union[Unset, int] = UNSET
    employing_entity_id: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from_employee_id = self.from_employee_id

        to_employee_id = self.to_employee_id

        include_costs = self.include_costs

        statuses: Union[Unset, List[str]] = UNSET
        if not isinstance(self.statuses, Unset):
            statuses = []
            for statuses_item_data in self.statuses:
                statuses_item = statuses_item_data.value
                statuses.append(statuses_item)

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
        if from_employee_id is not UNSET:
            field_dict["fromEmployeeId"] = from_employee_id
        if to_employee_id is not UNSET:
            field_dict["toEmployeeId"] = to_employee_id
        if include_costs is not UNSET:
            field_dict["includeCosts"] = include_costs
        if statuses is not UNSET:
            field_dict["statuses"] = statuses
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
        from_employee_id = d.pop("fromEmployeeId", UNSET)

        to_employee_id = d.pop("toEmployeeId", UNSET)

        include_costs = d.pop("includeCosts", UNSET)

        statuses = []
        _statuses = d.pop("statuses", UNSET)
        for statuses_item_data in _statuses or []:
            statuses_item = ShiftSwappingReportRequestModelRosterShiftSwapStatusEnum(statuses_item_data)

            statuses.append(statuses_item)

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

        shift_swapping_report_request_model = cls(
            from_employee_id=from_employee_id,
            to_employee_id=to_employee_id,
            include_costs=include_costs,
            statuses=statuses,
            from_date=from_date,
            to_date=to_date,
            location_id=location_id,
            employing_entity_id=employing_entity_id,
        )

        shift_swapping_report_request_model.additional_properties = d
        return shift_swapping_report_request_model

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
