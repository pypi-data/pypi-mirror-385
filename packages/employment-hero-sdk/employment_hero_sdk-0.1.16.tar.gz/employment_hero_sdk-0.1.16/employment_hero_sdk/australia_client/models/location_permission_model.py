from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="LocationPermissionModel")


@_attrs_define
class LocationPermissionModel:
    """
    Attributes:
        id (Union[Unset, List[int]]):
        can_approve_leave_requests (Union[Unset, bool]):
        can_view_leave_requests (Union[Unset, bool]):
        can_approve_timesheets (Union[Unset, bool]):
        can_create_timesheets (Union[Unset, bool]):
        can_approve_expenses (Union[Unset, bool]):
        can_view_expenses (Union[Unset, bool]):
        can_view_shift_costs (Union[Unset, bool]):
        can_view_rosters (Union[Unset, bool]):
        can_manage_rosters (Union[Unset, bool]):
    """

    id: Union[Unset, List[int]] = UNSET
    can_approve_leave_requests: Union[Unset, bool] = UNSET
    can_view_leave_requests: Union[Unset, bool] = UNSET
    can_approve_timesheets: Union[Unset, bool] = UNSET
    can_create_timesheets: Union[Unset, bool] = UNSET
    can_approve_expenses: Union[Unset, bool] = UNSET
    can_view_expenses: Union[Unset, bool] = UNSET
    can_view_shift_costs: Union[Unset, bool] = UNSET
    can_view_rosters: Union[Unset, bool] = UNSET
    can_manage_rosters: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id: Union[Unset, List[int]] = UNSET
        if not isinstance(self.id, Unset):
            id = self.id

        can_approve_leave_requests = self.can_approve_leave_requests

        can_view_leave_requests = self.can_view_leave_requests

        can_approve_timesheets = self.can_approve_timesheets

        can_create_timesheets = self.can_create_timesheets

        can_approve_expenses = self.can_approve_expenses

        can_view_expenses = self.can_view_expenses

        can_view_shift_costs = self.can_view_shift_costs

        can_view_rosters = self.can_view_rosters

        can_manage_rosters = self.can_manage_rosters

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if can_approve_leave_requests is not UNSET:
            field_dict["canApproveLeaveRequests"] = can_approve_leave_requests
        if can_view_leave_requests is not UNSET:
            field_dict["canViewLeaveRequests"] = can_view_leave_requests
        if can_approve_timesheets is not UNSET:
            field_dict["canApproveTimesheets"] = can_approve_timesheets
        if can_create_timesheets is not UNSET:
            field_dict["canCreateTimesheets"] = can_create_timesheets
        if can_approve_expenses is not UNSET:
            field_dict["canApproveExpenses"] = can_approve_expenses
        if can_view_expenses is not UNSET:
            field_dict["canViewExpenses"] = can_view_expenses
        if can_view_shift_costs is not UNSET:
            field_dict["canViewShiftCosts"] = can_view_shift_costs
        if can_view_rosters is not UNSET:
            field_dict["canViewRosters"] = can_view_rosters
        if can_manage_rosters is not UNSET:
            field_dict["canManageRosters"] = can_manage_rosters

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = cast(List[int], d.pop("id", UNSET))

        can_approve_leave_requests = d.pop("canApproveLeaveRequests", UNSET)

        can_view_leave_requests = d.pop("canViewLeaveRequests", UNSET)

        can_approve_timesheets = d.pop("canApproveTimesheets", UNSET)

        can_create_timesheets = d.pop("canCreateTimesheets", UNSET)

        can_approve_expenses = d.pop("canApproveExpenses", UNSET)

        can_view_expenses = d.pop("canViewExpenses", UNSET)

        can_view_shift_costs = d.pop("canViewShiftCosts", UNSET)

        can_view_rosters = d.pop("canViewRosters", UNSET)

        can_manage_rosters = d.pop("canManageRosters", UNSET)

        location_permission_model = cls(
            id=id,
            can_approve_leave_requests=can_approve_leave_requests,
            can_view_leave_requests=can_view_leave_requests,
            can_approve_timesheets=can_approve_timesheets,
            can_create_timesheets=can_create_timesheets,
            can_approve_expenses=can_approve_expenses,
            can_view_expenses=can_view_expenses,
            can_view_shift_costs=can_view_shift_costs,
            can_view_rosters=can_view_rosters,
            can_manage_rosters=can_manage_rosters,
        )

        location_permission_model.additional_properties = d
        return location_permission_model

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
