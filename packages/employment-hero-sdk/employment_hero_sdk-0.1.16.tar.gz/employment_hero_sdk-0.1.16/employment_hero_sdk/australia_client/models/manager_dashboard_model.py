from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.manager_item_count_model import ManagerItemCountModel


T = TypeVar("T", bound="ManagerDashboardModel")


@_attrs_define
class ManagerDashboardModel:
    """
    Attributes:
        pending_leave_requests (Union[Unset, ManagerItemCountModel]):
        submitted_timesheets (Union[Unset, ManagerItemCountModel]):
        pending_expense_requests (Union[Unset, ManagerItemCountModel]):
    """

    pending_leave_requests: Union[Unset, "ManagerItemCountModel"] = UNSET
    submitted_timesheets: Union[Unset, "ManagerItemCountModel"] = UNSET
    pending_expense_requests: Union[Unset, "ManagerItemCountModel"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        pending_leave_requests: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.pending_leave_requests, Unset):
            pending_leave_requests = self.pending_leave_requests.to_dict()

        submitted_timesheets: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.submitted_timesheets, Unset):
            submitted_timesheets = self.submitted_timesheets.to_dict()

        pending_expense_requests: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.pending_expense_requests, Unset):
            pending_expense_requests = self.pending_expense_requests.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if pending_leave_requests is not UNSET:
            field_dict["pendingLeaveRequests"] = pending_leave_requests
        if submitted_timesheets is not UNSET:
            field_dict["submittedTimesheets"] = submitted_timesheets
        if pending_expense_requests is not UNSET:
            field_dict["pendingExpenseRequests"] = pending_expense_requests

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.manager_item_count_model import ManagerItemCountModel

        d = src_dict.copy()
        _pending_leave_requests = d.pop("pendingLeaveRequests", UNSET)
        pending_leave_requests: Union[Unset, ManagerItemCountModel]
        if isinstance(_pending_leave_requests, Unset):
            pending_leave_requests = UNSET
        else:
            pending_leave_requests = ManagerItemCountModel.from_dict(_pending_leave_requests)

        _submitted_timesheets = d.pop("submittedTimesheets", UNSET)
        submitted_timesheets: Union[Unset, ManagerItemCountModel]
        if isinstance(_submitted_timesheets, Unset):
            submitted_timesheets = UNSET
        else:
            submitted_timesheets = ManagerItemCountModel.from_dict(_submitted_timesheets)

        _pending_expense_requests = d.pop("pendingExpenseRequests", UNSET)
        pending_expense_requests: Union[Unset, ManagerItemCountModel]
        if isinstance(_pending_expense_requests, Unset):
            pending_expense_requests = UNSET
        else:
            pending_expense_requests = ManagerItemCountModel.from_dict(_pending_expense_requests)

        manager_dashboard_model = cls(
            pending_leave_requests=pending_leave_requests,
            submitted_timesheets=submitted_timesheets,
            pending_expense_requests=pending_expense_requests,
        )

        manager_dashboard_model.additional_properties = d
        return manager_dashboard_model

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
