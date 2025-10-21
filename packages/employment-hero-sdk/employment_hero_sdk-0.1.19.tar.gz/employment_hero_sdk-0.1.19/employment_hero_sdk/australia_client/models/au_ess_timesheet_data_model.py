from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.au_ess_roster_shift_model import AuEssRosterShiftModel
    from ..models.ess_leave_request_model import EssLeaveRequestModel
    from ..models.ess_timesheet_model import EssTimesheetModel
    from ..models.public_holiday_model import PublicHolidayModel


T = TypeVar("T", bound="AuEssTimesheetDataModel")


@_attrs_define
class AuEssTimesheetDataModel:
    """
    Attributes:
        timesheets (Union[Unset, List['EssTimesheetModel']]):
        leave_requests (Union[Unset, List['EssLeaveRequestModel']]):
        roster_shifts (Union[Unset, List['AuEssRosterShiftModel']]):
        public_holidays (Union[Unset, List['PublicHolidayModel']]):
    """

    timesheets: Union[Unset, List["EssTimesheetModel"]] = UNSET
    leave_requests: Union[Unset, List["EssLeaveRequestModel"]] = UNSET
    roster_shifts: Union[Unset, List["AuEssRosterShiftModel"]] = UNSET
    public_holidays: Union[Unset, List["PublicHolidayModel"]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        timesheets: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.timesheets, Unset):
            timesheets = []
            for timesheets_item_data in self.timesheets:
                timesheets_item = timesheets_item_data.to_dict()
                timesheets.append(timesheets_item)

        leave_requests: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.leave_requests, Unset):
            leave_requests = []
            for leave_requests_item_data in self.leave_requests:
                leave_requests_item = leave_requests_item_data.to_dict()
                leave_requests.append(leave_requests_item)

        roster_shifts: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.roster_shifts, Unset):
            roster_shifts = []
            for roster_shifts_item_data in self.roster_shifts:
                roster_shifts_item = roster_shifts_item_data.to_dict()
                roster_shifts.append(roster_shifts_item)

        public_holidays: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.public_holidays, Unset):
            public_holidays = []
            for public_holidays_item_data in self.public_holidays:
                public_holidays_item = public_holidays_item_data.to_dict()
                public_holidays.append(public_holidays_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if timesheets is not UNSET:
            field_dict["timesheets"] = timesheets
        if leave_requests is not UNSET:
            field_dict["leaveRequests"] = leave_requests
        if roster_shifts is not UNSET:
            field_dict["rosterShifts"] = roster_shifts
        if public_holidays is not UNSET:
            field_dict["publicHolidays"] = public_holidays

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.au_ess_roster_shift_model import AuEssRosterShiftModel
        from ..models.ess_leave_request_model import EssLeaveRequestModel
        from ..models.ess_timesheet_model import EssTimesheetModel
        from ..models.public_holiday_model import PublicHolidayModel

        d = src_dict.copy()
        timesheets = []
        _timesheets = d.pop("timesheets", UNSET)
        for timesheets_item_data in _timesheets or []:
            timesheets_item = EssTimesheetModel.from_dict(timesheets_item_data)

            timesheets.append(timesheets_item)

        leave_requests = []
        _leave_requests = d.pop("leaveRequests", UNSET)
        for leave_requests_item_data in _leave_requests or []:
            leave_requests_item = EssLeaveRequestModel.from_dict(leave_requests_item_data)

            leave_requests.append(leave_requests_item)

        roster_shifts = []
        _roster_shifts = d.pop("rosterShifts", UNSET)
        for roster_shifts_item_data in _roster_shifts or []:
            roster_shifts_item = AuEssRosterShiftModel.from_dict(roster_shifts_item_data)

            roster_shifts.append(roster_shifts_item)

        public_holidays = []
        _public_holidays = d.pop("publicHolidays", UNSET)
        for public_holidays_item_data in _public_holidays or []:
            public_holidays_item = PublicHolidayModel.from_dict(public_holidays_item_data)

            public_holidays.append(public_holidays_item)

        au_ess_timesheet_data_model = cls(
            timesheets=timesheets,
            leave_requests=leave_requests,
            roster_shifts=roster_shifts,
            public_holidays=public_holidays,
        )

        au_ess_timesheet_data_model.additional_properties = d
        return au_ess_timesheet_data_model

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
