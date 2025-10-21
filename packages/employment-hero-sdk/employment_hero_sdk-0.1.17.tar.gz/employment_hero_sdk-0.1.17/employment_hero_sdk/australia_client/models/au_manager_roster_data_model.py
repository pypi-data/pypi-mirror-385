from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.au_manager_roster_shift_model import AuManagerRosterShiftModel
    from ..models.i_leave_based_roster_shift import ILeaveBasedRosterShift
    from ..models.manager_biddable_roster_shift_model import ManagerBiddableRosterShiftModel
    from ..models.manager_unavailability_model import ManagerUnavailabilityModel


T = TypeVar("T", bound="AuManagerRosterDataModel")


@_attrs_define
class AuManagerRosterDataModel:
    """
    Attributes:
        rostered_shifts (Union[Unset, List['AuManagerRosterShiftModel']]):
        unassigned_shifts (Union[Unset, List['AuManagerRosterShiftModel']]):
        biddable_shifts (Union[Unset, List['ManagerBiddableRosterShiftModel']]):
        unavailability (Union[Unset, List['ManagerUnavailabilityModel']]):
        leave_requests (Union[Unset, List['ILeaveBasedRosterShift']]):
    """

    rostered_shifts: Union[Unset, List["AuManagerRosterShiftModel"]] = UNSET
    unassigned_shifts: Union[Unset, List["AuManagerRosterShiftModel"]] = UNSET
    biddable_shifts: Union[Unset, List["ManagerBiddableRosterShiftModel"]] = UNSET
    unavailability: Union[Unset, List["ManagerUnavailabilityModel"]] = UNSET
    leave_requests: Union[Unset, List["ILeaveBasedRosterShift"]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        rostered_shifts: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.rostered_shifts, Unset):
            rostered_shifts = []
            for rostered_shifts_item_data in self.rostered_shifts:
                rostered_shifts_item = rostered_shifts_item_data.to_dict()
                rostered_shifts.append(rostered_shifts_item)

        unassigned_shifts: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.unassigned_shifts, Unset):
            unassigned_shifts = []
            for unassigned_shifts_item_data in self.unassigned_shifts:
                unassigned_shifts_item = unassigned_shifts_item_data.to_dict()
                unassigned_shifts.append(unassigned_shifts_item)

        biddable_shifts: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.biddable_shifts, Unset):
            biddable_shifts = []
            for biddable_shifts_item_data in self.biddable_shifts:
                biddable_shifts_item = biddable_shifts_item_data.to_dict()
                biddable_shifts.append(biddable_shifts_item)

        unavailability: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.unavailability, Unset):
            unavailability = []
            for unavailability_item_data in self.unavailability:
                unavailability_item = unavailability_item_data.to_dict()
                unavailability.append(unavailability_item)

        leave_requests: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.leave_requests, Unset):
            leave_requests = []
            for leave_requests_item_data in self.leave_requests:
                leave_requests_item = leave_requests_item_data.to_dict()
                leave_requests.append(leave_requests_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if rostered_shifts is not UNSET:
            field_dict["rosteredShifts"] = rostered_shifts
        if unassigned_shifts is not UNSET:
            field_dict["unassignedShifts"] = unassigned_shifts
        if biddable_shifts is not UNSET:
            field_dict["biddableShifts"] = biddable_shifts
        if unavailability is not UNSET:
            field_dict["unavailability"] = unavailability
        if leave_requests is not UNSET:
            field_dict["leaveRequests"] = leave_requests

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.au_manager_roster_shift_model import AuManagerRosterShiftModel
        from ..models.i_leave_based_roster_shift import ILeaveBasedRosterShift
        from ..models.manager_biddable_roster_shift_model import ManagerBiddableRosterShiftModel
        from ..models.manager_unavailability_model import ManagerUnavailabilityModel

        d = src_dict.copy()
        rostered_shifts = []
        _rostered_shifts = d.pop("rosteredShifts", UNSET)
        for rostered_shifts_item_data in _rostered_shifts or []:
            rostered_shifts_item = AuManagerRosterShiftModel.from_dict(rostered_shifts_item_data)

            rostered_shifts.append(rostered_shifts_item)

        unassigned_shifts = []
        _unassigned_shifts = d.pop("unassignedShifts", UNSET)
        for unassigned_shifts_item_data in _unassigned_shifts or []:
            unassigned_shifts_item = AuManagerRosterShiftModel.from_dict(unassigned_shifts_item_data)

            unassigned_shifts.append(unassigned_shifts_item)

        biddable_shifts = []
        _biddable_shifts = d.pop("biddableShifts", UNSET)
        for biddable_shifts_item_data in _biddable_shifts or []:
            biddable_shifts_item = ManagerBiddableRosterShiftModel.from_dict(biddable_shifts_item_data)

            biddable_shifts.append(biddable_shifts_item)

        unavailability = []
        _unavailability = d.pop("unavailability", UNSET)
        for unavailability_item_data in _unavailability or []:
            unavailability_item = ManagerUnavailabilityModel.from_dict(unavailability_item_data)

            unavailability.append(unavailability_item)

        leave_requests = []
        _leave_requests = d.pop("leaveRequests", UNSET)
        for leave_requests_item_data in _leave_requests or []:
            leave_requests_item = ILeaveBasedRosterShift.from_dict(leave_requests_item_data)

            leave_requests.append(leave_requests_item)

        au_manager_roster_data_model = cls(
            rostered_shifts=rostered_shifts,
            unassigned_shifts=unassigned_shifts,
            biddable_shifts=biddable_shifts,
            unavailability=unavailability,
            leave_requests=leave_requests,
        )

        au_manager_roster_data_model.additional_properties = d
        return au_manager_roster_data_model

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
