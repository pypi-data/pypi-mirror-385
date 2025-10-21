import datetime
from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.roster_shift_filter_model_roster_shift_status import RosterShiftFilterModelRosterShiftStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="RosterShiftFilterModel")


@_attrs_define
class RosterShiftFilterModel:
    """
    Attributes:
        from_date (Union[Unset, datetime.datetime]):
        to_date (Union[Unset, datetime.datetime]):
        shift_status (Union[Unset, RosterShiftFilterModelRosterShiftStatus]):
        shift_statuses (Union[Unset, List[RosterShiftFilterModelRosterShiftStatus]]):
        selected_locations (Union[Unset, List[str]]):
        selected_employees (Union[Unset, List[str]]):
        selected_roles (Union[Unset, List[str]]):
        employee_id (Union[Unset, int]):
        location_id (Union[Unset, int]):
        employee_group_id (Union[Unset, int]):
        unassigned_shifts_only (Union[Unset, bool]):
        select_all_roles (Union[Unset, bool]):
        exclude_shifts_overlapping_from_date (Union[Unset, bool]):
        page_size (Union[Unset, int]):
        current_page (Union[Unset, int]):
        include_warnings (Union[Unset, bool]):
    """

    from_date: Union[Unset, datetime.datetime] = UNSET
    to_date: Union[Unset, datetime.datetime] = UNSET
    shift_status: Union[Unset, RosterShiftFilterModelRosterShiftStatus] = UNSET
    shift_statuses: Union[Unset, List[RosterShiftFilterModelRosterShiftStatus]] = UNSET
    selected_locations: Union[Unset, List[str]] = UNSET
    selected_employees: Union[Unset, List[str]] = UNSET
    selected_roles: Union[Unset, List[str]] = UNSET
    employee_id: Union[Unset, int] = UNSET
    location_id: Union[Unset, int] = UNSET
    employee_group_id: Union[Unset, int] = UNSET
    unassigned_shifts_only: Union[Unset, bool] = UNSET
    select_all_roles: Union[Unset, bool] = UNSET
    exclude_shifts_overlapping_from_date: Union[Unset, bool] = UNSET
    page_size: Union[Unset, int] = UNSET
    current_page: Union[Unset, int] = UNSET
    include_warnings: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from_date: Union[Unset, str] = UNSET
        if not isinstance(self.from_date, Unset):
            from_date = self.from_date.isoformat()

        to_date: Union[Unset, str] = UNSET
        if not isinstance(self.to_date, Unset):
            to_date = self.to_date.isoformat()

        shift_status: Union[Unset, str] = UNSET
        if not isinstance(self.shift_status, Unset):
            shift_status = self.shift_status.value

        shift_statuses: Union[Unset, List[str]] = UNSET
        if not isinstance(self.shift_statuses, Unset):
            shift_statuses = []
            for shift_statuses_item_data in self.shift_statuses:
                shift_statuses_item = shift_statuses_item_data.value
                shift_statuses.append(shift_statuses_item)

        selected_locations: Union[Unset, List[str]] = UNSET
        if not isinstance(self.selected_locations, Unset):
            selected_locations = self.selected_locations

        selected_employees: Union[Unset, List[str]] = UNSET
        if not isinstance(self.selected_employees, Unset):
            selected_employees = self.selected_employees

        selected_roles: Union[Unset, List[str]] = UNSET
        if not isinstance(self.selected_roles, Unset):
            selected_roles = self.selected_roles

        employee_id = self.employee_id

        location_id = self.location_id

        employee_group_id = self.employee_group_id

        unassigned_shifts_only = self.unassigned_shifts_only

        select_all_roles = self.select_all_roles

        exclude_shifts_overlapping_from_date = self.exclude_shifts_overlapping_from_date

        page_size = self.page_size

        current_page = self.current_page

        include_warnings = self.include_warnings

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if from_date is not UNSET:
            field_dict["fromDate"] = from_date
        if to_date is not UNSET:
            field_dict["toDate"] = to_date
        if shift_status is not UNSET:
            field_dict["shiftStatus"] = shift_status
        if shift_statuses is not UNSET:
            field_dict["shiftStatuses"] = shift_statuses
        if selected_locations is not UNSET:
            field_dict["selectedLocations"] = selected_locations
        if selected_employees is not UNSET:
            field_dict["selectedEmployees"] = selected_employees
        if selected_roles is not UNSET:
            field_dict["selectedRoles"] = selected_roles
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if location_id is not UNSET:
            field_dict["locationId"] = location_id
        if employee_group_id is not UNSET:
            field_dict["employeeGroupId"] = employee_group_id
        if unassigned_shifts_only is not UNSET:
            field_dict["unassignedShiftsOnly"] = unassigned_shifts_only
        if select_all_roles is not UNSET:
            field_dict["selectAllRoles"] = select_all_roles
        if exclude_shifts_overlapping_from_date is not UNSET:
            field_dict["excludeShiftsOverlappingFromDate"] = exclude_shifts_overlapping_from_date
        if page_size is not UNSET:
            field_dict["pageSize"] = page_size
        if current_page is not UNSET:
            field_dict["currentPage"] = current_page
        if include_warnings is not UNSET:
            field_dict["includeWarnings"] = include_warnings

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
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

        _shift_status = d.pop("shiftStatus", UNSET)
        shift_status: Union[Unset, RosterShiftFilterModelRosterShiftStatus]
        if isinstance(_shift_status, Unset):
            shift_status = UNSET
        else:
            shift_status = RosterShiftFilterModelRosterShiftStatus(_shift_status)

        shift_statuses = []
        _shift_statuses = d.pop("shiftStatuses", UNSET)
        for shift_statuses_item_data in _shift_statuses or []:
            shift_statuses_item = RosterShiftFilterModelRosterShiftStatus(shift_statuses_item_data)

            shift_statuses.append(shift_statuses_item)

        selected_locations = cast(List[str], d.pop("selectedLocations", UNSET))

        selected_employees = cast(List[str], d.pop("selectedEmployees", UNSET))

        selected_roles = cast(List[str], d.pop("selectedRoles", UNSET))

        employee_id = d.pop("employeeId", UNSET)

        location_id = d.pop("locationId", UNSET)

        employee_group_id = d.pop("employeeGroupId", UNSET)

        unassigned_shifts_only = d.pop("unassignedShiftsOnly", UNSET)

        select_all_roles = d.pop("selectAllRoles", UNSET)

        exclude_shifts_overlapping_from_date = d.pop("excludeShiftsOverlappingFromDate", UNSET)

        page_size = d.pop("pageSize", UNSET)

        current_page = d.pop("currentPage", UNSET)

        include_warnings = d.pop("includeWarnings", UNSET)

        roster_shift_filter_model = cls(
            from_date=from_date,
            to_date=to_date,
            shift_status=shift_status,
            shift_statuses=shift_statuses,
            selected_locations=selected_locations,
            selected_employees=selected_employees,
            selected_roles=selected_roles,
            employee_id=employee_id,
            location_id=location_id,
            employee_group_id=employee_group_id,
            unassigned_shifts_only=unassigned_shifts_only,
            select_all_roles=select_all_roles,
            exclude_shifts_overlapping_from_date=exclude_shifts_overlapping_from_date,
            page_size=page_size,
            current_page=current_page,
            include_warnings=include_warnings,
        )

        roster_shift_filter_model.additional_properties = d
        return roster_shift_filter_model

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
