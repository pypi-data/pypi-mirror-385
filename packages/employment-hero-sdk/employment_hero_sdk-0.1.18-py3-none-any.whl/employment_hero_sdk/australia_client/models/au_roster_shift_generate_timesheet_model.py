import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.au_roster_shift_generate_timesheet_model_nullable_shift_assignment_status_enum import (
    AuRosterShiftGenerateTimesheetModelNullableShiftAssignmentStatusEnum,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.qualification_model import QualificationModel
    from ..models.roster_shift_break_api_model import RosterShiftBreakApiModel
    from ..models.roster_shift_role import RosterShiftRole
    from ..models.roster_shift_swap_model import RosterShiftSwapModel


T = TypeVar("T", bound="AuRosterShiftGenerateTimesheetModel")


@_attrs_define
class AuRosterShiftGenerateTimesheetModel:
    """
    Attributes:
        classification_id (Union[Unset, int]):
        classification_name (Union[Unset, str]):
        description (Union[Unset, str]):
        is_different (Union[Unset, bool]):
        fully_qualified_location_name (Union[Unset, str]):
        warnings (Union[Unset, List[str]]):
        id (Union[Unset, int]):
        token (Union[Unset, str]):
        qualifications (Union[Unset, List['QualificationModel']]):
        breaks (Union[Unset, List['RosterShiftBreakApiModel']]):
        employee_id (Union[Unset, int]):
        employee_name (Union[Unset, str]):
        location_id (Union[Unset, int]):
        location_name (Union[Unset, str]):
        work_type_id (Union[Unset, int]):
        work_type_name (Union[Unset, str]):
        role (Union[Unset, RosterShiftRole]):
        start_time (Union[Unset, datetime.datetime]):
        end_time (Union[Unset, datetime.datetime]):
        notes (Union[Unset, str]):
        published (Union[Unset, bool]):
        accepted (Union[Unset, bool]):
        pending_swap (Union[Unset, RosterShiftSwapModel]):
        date_published (Union[Unset, datetime.datetime]):
        biddable (Union[Unset, bool]):
        shift_swap_cutoff_time (Union[Unset, datetime.datetime]):
        shift_assignment_status (Union[Unset, AuRosterShiftGenerateTimesheetModelNullableShiftAssignmentStatusEnum]):
    """

    classification_id: Union[Unset, int] = UNSET
    classification_name: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    is_different: Union[Unset, bool] = UNSET
    fully_qualified_location_name: Union[Unset, str] = UNSET
    warnings: Union[Unset, List[str]] = UNSET
    id: Union[Unset, int] = UNSET
    token: Union[Unset, str] = UNSET
    qualifications: Union[Unset, List["QualificationModel"]] = UNSET
    breaks: Union[Unset, List["RosterShiftBreakApiModel"]] = UNSET
    employee_id: Union[Unset, int] = UNSET
    employee_name: Union[Unset, str] = UNSET
    location_id: Union[Unset, int] = UNSET
    location_name: Union[Unset, str] = UNSET
    work_type_id: Union[Unset, int] = UNSET
    work_type_name: Union[Unset, str] = UNSET
    role: Union[Unset, "RosterShiftRole"] = UNSET
    start_time: Union[Unset, datetime.datetime] = UNSET
    end_time: Union[Unset, datetime.datetime] = UNSET
    notes: Union[Unset, str] = UNSET
    published: Union[Unset, bool] = UNSET
    accepted: Union[Unset, bool] = UNSET
    pending_swap: Union[Unset, "RosterShiftSwapModel"] = UNSET
    date_published: Union[Unset, datetime.datetime] = UNSET
    biddable: Union[Unset, bool] = UNSET
    shift_swap_cutoff_time: Union[Unset, datetime.datetime] = UNSET
    shift_assignment_status: Union[Unset, AuRosterShiftGenerateTimesheetModelNullableShiftAssignmentStatusEnum] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        classification_id = self.classification_id

        classification_name = self.classification_name

        description = self.description

        is_different = self.is_different

        fully_qualified_location_name = self.fully_qualified_location_name

        warnings: Union[Unset, List[str]] = UNSET
        if not isinstance(self.warnings, Unset):
            warnings = self.warnings

        id = self.id

        token = self.token

        qualifications: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.qualifications, Unset):
            qualifications = []
            for qualifications_item_data in self.qualifications:
                qualifications_item = qualifications_item_data.to_dict()
                qualifications.append(qualifications_item)

        breaks: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.breaks, Unset):
            breaks = []
            for breaks_item_data in self.breaks:
                breaks_item = breaks_item_data.to_dict()
                breaks.append(breaks_item)

        employee_id = self.employee_id

        employee_name = self.employee_name

        location_id = self.location_id

        location_name = self.location_name

        work_type_id = self.work_type_id

        work_type_name = self.work_type_name

        role: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.role, Unset):
            role = self.role.to_dict()

        start_time: Union[Unset, str] = UNSET
        if not isinstance(self.start_time, Unset):
            start_time = self.start_time.isoformat()

        end_time: Union[Unset, str] = UNSET
        if not isinstance(self.end_time, Unset):
            end_time = self.end_time.isoformat()

        notes = self.notes

        published = self.published

        accepted = self.accepted

        pending_swap: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.pending_swap, Unset):
            pending_swap = self.pending_swap.to_dict()

        date_published: Union[Unset, str] = UNSET
        if not isinstance(self.date_published, Unset):
            date_published = self.date_published.isoformat()

        biddable = self.biddable

        shift_swap_cutoff_time: Union[Unset, str] = UNSET
        if not isinstance(self.shift_swap_cutoff_time, Unset):
            shift_swap_cutoff_time = self.shift_swap_cutoff_time.isoformat()

        shift_assignment_status: Union[Unset, str] = UNSET
        if not isinstance(self.shift_assignment_status, Unset):
            shift_assignment_status = self.shift_assignment_status.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if classification_id is not UNSET:
            field_dict["classificationId"] = classification_id
        if classification_name is not UNSET:
            field_dict["classificationName"] = classification_name
        if description is not UNSET:
            field_dict["description"] = description
        if is_different is not UNSET:
            field_dict["isDifferent"] = is_different
        if fully_qualified_location_name is not UNSET:
            field_dict["fullyQualifiedLocationName"] = fully_qualified_location_name
        if warnings is not UNSET:
            field_dict["warnings"] = warnings
        if id is not UNSET:
            field_dict["id"] = id
        if token is not UNSET:
            field_dict["token"] = token
        if qualifications is not UNSET:
            field_dict["qualifications"] = qualifications
        if breaks is not UNSET:
            field_dict["breaks"] = breaks
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if employee_name is not UNSET:
            field_dict["employeeName"] = employee_name
        if location_id is not UNSET:
            field_dict["locationId"] = location_id
        if location_name is not UNSET:
            field_dict["locationName"] = location_name
        if work_type_id is not UNSET:
            field_dict["workTypeId"] = work_type_id
        if work_type_name is not UNSET:
            field_dict["workTypeName"] = work_type_name
        if role is not UNSET:
            field_dict["role"] = role
        if start_time is not UNSET:
            field_dict["startTime"] = start_time
        if end_time is not UNSET:
            field_dict["endTime"] = end_time
        if notes is not UNSET:
            field_dict["notes"] = notes
        if published is not UNSET:
            field_dict["published"] = published
        if accepted is not UNSET:
            field_dict["accepted"] = accepted
        if pending_swap is not UNSET:
            field_dict["pendingSwap"] = pending_swap
        if date_published is not UNSET:
            field_dict["datePublished"] = date_published
        if biddable is not UNSET:
            field_dict["biddable"] = biddable
        if shift_swap_cutoff_time is not UNSET:
            field_dict["shiftSwapCutoffTime"] = shift_swap_cutoff_time
        if shift_assignment_status is not UNSET:
            field_dict["shiftAssignmentStatus"] = shift_assignment_status

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.qualification_model import QualificationModel
        from ..models.roster_shift_break_api_model import RosterShiftBreakApiModel
        from ..models.roster_shift_role import RosterShiftRole
        from ..models.roster_shift_swap_model import RosterShiftSwapModel

        d = src_dict.copy()
        classification_id = d.pop("classificationId", UNSET)

        classification_name = d.pop("classificationName", UNSET)

        description = d.pop("description", UNSET)

        is_different = d.pop("isDifferent", UNSET)

        fully_qualified_location_name = d.pop("fullyQualifiedLocationName", UNSET)

        warnings = cast(List[str], d.pop("warnings", UNSET))

        id = d.pop("id", UNSET)

        token = d.pop("token", UNSET)

        qualifications = []
        _qualifications = d.pop("qualifications", UNSET)
        for qualifications_item_data in _qualifications or []:
            qualifications_item = QualificationModel.from_dict(qualifications_item_data)

            qualifications.append(qualifications_item)

        breaks = []
        _breaks = d.pop("breaks", UNSET)
        for breaks_item_data in _breaks or []:
            breaks_item = RosterShiftBreakApiModel.from_dict(breaks_item_data)

            breaks.append(breaks_item)

        employee_id = d.pop("employeeId", UNSET)

        employee_name = d.pop("employeeName", UNSET)

        location_id = d.pop("locationId", UNSET)

        location_name = d.pop("locationName", UNSET)

        work_type_id = d.pop("workTypeId", UNSET)

        work_type_name = d.pop("workTypeName", UNSET)

        _role = d.pop("role", UNSET)
        role: Union[Unset, RosterShiftRole]
        if isinstance(_role, Unset):
            role = UNSET
        else:
            role = RosterShiftRole.from_dict(_role)

        _start_time = d.pop("startTime", UNSET)
        start_time: Union[Unset, datetime.datetime]
        if isinstance(_start_time, Unset):
            start_time = UNSET
        else:
            start_time = isoparse(_start_time)

        _end_time = d.pop("endTime", UNSET)
        end_time: Union[Unset, datetime.datetime]
        if isinstance(_end_time, Unset):
            end_time = UNSET
        else:
            end_time = isoparse(_end_time)

        notes = d.pop("notes", UNSET)

        published = d.pop("published", UNSET)

        accepted = d.pop("accepted", UNSET)

        _pending_swap = d.pop("pendingSwap", UNSET)
        pending_swap: Union[Unset, RosterShiftSwapModel]
        if isinstance(_pending_swap, Unset):
            pending_swap = UNSET
        else:
            pending_swap = RosterShiftSwapModel.from_dict(_pending_swap)

        _date_published = d.pop("datePublished", UNSET)
        date_published: Union[Unset, datetime.datetime]
        if isinstance(_date_published, Unset):
            date_published = UNSET
        else:
            date_published = isoparse(_date_published)

        biddable = d.pop("biddable", UNSET)

        _shift_swap_cutoff_time = d.pop("shiftSwapCutoffTime", UNSET)
        shift_swap_cutoff_time: Union[Unset, datetime.datetime]
        if isinstance(_shift_swap_cutoff_time, Unset):
            shift_swap_cutoff_time = UNSET
        else:
            shift_swap_cutoff_time = isoparse(_shift_swap_cutoff_time)

        _shift_assignment_status = d.pop("shiftAssignmentStatus", UNSET)
        shift_assignment_status: Union[Unset, AuRosterShiftGenerateTimesheetModelNullableShiftAssignmentStatusEnum]
        if isinstance(_shift_assignment_status, Unset):
            shift_assignment_status = UNSET
        else:
            shift_assignment_status = AuRosterShiftGenerateTimesheetModelNullableShiftAssignmentStatusEnum(
                _shift_assignment_status
            )

        au_roster_shift_generate_timesheet_model = cls(
            classification_id=classification_id,
            classification_name=classification_name,
            description=description,
            is_different=is_different,
            fully_qualified_location_name=fully_qualified_location_name,
            warnings=warnings,
            id=id,
            token=token,
            qualifications=qualifications,
            breaks=breaks,
            employee_id=employee_id,
            employee_name=employee_name,
            location_id=location_id,
            location_name=location_name,
            work_type_id=work_type_id,
            work_type_name=work_type_name,
            role=role,
            start_time=start_time,
            end_time=end_time,
            notes=notes,
            published=published,
            accepted=accepted,
            pending_swap=pending_swap,
            date_published=date_published,
            biddable=biddable,
            shift_swap_cutoff_time=shift_swap_cutoff_time,
            shift_assignment_status=shift_assignment_status,
        )

        au_roster_shift_generate_timesheet_model.additional_properties = d
        return au_roster_shift_generate_timesheet_model

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
