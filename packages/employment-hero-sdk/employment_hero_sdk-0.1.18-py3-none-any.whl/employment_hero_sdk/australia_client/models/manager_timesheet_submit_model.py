import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.manager_timesheet_submit_model_nullable_external_service import (
    ManagerTimesheetSubmitModelNullableExternalService,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.attachment import Attachment
    from ..models.timesheet_break_submit_model import TimesheetBreakSubmitModel


T = TypeVar("T", bound="ManagerTimesheetSubmitModel")


@_attrs_define
class ManagerTimesheetSubmitModel:
    """
    Attributes:
        id (Union[Unset, int]):
        employee_id (Union[Unset, int]):
        location_id (Union[Unset, int]):
        work_type_id (Union[Unset, int]):
        pay_category_id (Union[Unset, int]):
        leave_category_id (Union[Unset, int]):
        leave_request_id (Union[Unset, int]):
        classification_id (Union[Unset, int]):
        shift_condition_ids (Union[Unset, List[int]]):
        start (Union[Unset, datetime.datetime]):
        end (Union[Unset, datetime.datetime]):
        submitted_start (Union[Unset, datetime.datetime]):
        submitted_end (Union[Unset, datetime.datetime]):
        units (Union[Unset, float]):
        rate (Union[Unset, float]):
        comments (Union[Unset, str]):
        hidden_comments (Union[Unset, str]):
        breaks (Union[Unset, List['TimesheetBreakSubmitModel']]):
        attachment (Union[Unset, Attachment]):
        source (Union[Unset, ManagerTimesheetSubmitModelNullableExternalService]):
        location_is_deleted (Union[Unset, bool]):
        dimension_value_ids (Union[Unset, List[int]]):
    """

    id: Union[Unset, int] = UNSET
    employee_id: Union[Unset, int] = UNSET
    location_id: Union[Unset, int] = UNSET
    work_type_id: Union[Unset, int] = UNSET
    pay_category_id: Union[Unset, int] = UNSET
    leave_category_id: Union[Unset, int] = UNSET
    leave_request_id: Union[Unset, int] = UNSET
    classification_id: Union[Unset, int] = UNSET
    shift_condition_ids: Union[Unset, List[int]] = UNSET
    start: Union[Unset, datetime.datetime] = UNSET
    end: Union[Unset, datetime.datetime] = UNSET
    submitted_start: Union[Unset, datetime.datetime] = UNSET
    submitted_end: Union[Unset, datetime.datetime] = UNSET
    units: Union[Unset, float] = UNSET
    rate: Union[Unset, float] = UNSET
    comments: Union[Unset, str] = UNSET
    hidden_comments: Union[Unset, str] = UNSET
    breaks: Union[Unset, List["TimesheetBreakSubmitModel"]] = UNSET
    attachment: Union[Unset, "Attachment"] = UNSET
    source: Union[Unset, ManagerTimesheetSubmitModelNullableExternalService] = UNSET
    location_is_deleted: Union[Unset, bool] = UNSET
    dimension_value_ids: Union[Unset, List[int]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        employee_id = self.employee_id

        location_id = self.location_id

        work_type_id = self.work_type_id

        pay_category_id = self.pay_category_id

        leave_category_id = self.leave_category_id

        leave_request_id = self.leave_request_id

        classification_id = self.classification_id

        shift_condition_ids: Union[Unset, List[int]] = UNSET
        if not isinstance(self.shift_condition_ids, Unset):
            shift_condition_ids = self.shift_condition_ids

        start: Union[Unset, str] = UNSET
        if not isinstance(self.start, Unset):
            start = self.start.isoformat()

        end: Union[Unset, str] = UNSET
        if not isinstance(self.end, Unset):
            end = self.end.isoformat()

        submitted_start: Union[Unset, str] = UNSET
        if not isinstance(self.submitted_start, Unset):
            submitted_start = self.submitted_start.isoformat()

        submitted_end: Union[Unset, str] = UNSET
        if not isinstance(self.submitted_end, Unset):
            submitted_end = self.submitted_end.isoformat()

        units = self.units

        rate = self.rate

        comments = self.comments

        hidden_comments = self.hidden_comments

        breaks: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.breaks, Unset):
            breaks = []
            for breaks_item_data in self.breaks:
                breaks_item = breaks_item_data.to_dict()
                breaks.append(breaks_item)

        attachment: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.attachment, Unset):
            attachment = self.attachment.to_dict()

        source: Union[Unset, str] = UNSET
        if not isinstance(self.source, Unset):
            source = self.source.value

        location_is_deleted = self.location_is_deleted

        dimension_value_ids: Union[Unset, List[int]] = UNSET
        if not isinstance(self.dimension_value_ids, Unset):
            dimension_value_ids = self.dimension_value_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if location_id is not UNSET:
            field_dict["locationId"] = location_id
        if work_type_id is not UNSET:
            field_dict["workTypeId"] = work_type_id
        if pay_category_id is not UNSET:
            field_dict["payCategoryId"] = pay_category_id
        if leave_category_id is not UNSET:
            field_dict["leaveCategoryId"] = leave_category_id
        if leave_request_id is not UNSET:
            field_dict["leaveRequestId"] = leave_request_id
        if classification_id is not UNSET:
            field_dict["classificationId"] = classification_id
        if shift_condition_ids is not UNSET:
            field_dict["shiftConditionIds"] = shift_condition_ids
        if start is not UNSET:
            field_dict["start"] = start
        if end is not UNSET:
            field_dict["end"] = end
        if submitted_start is not UNSET:
            field_dict["submittedStart"] = submitted_start
        if submitted_end is not UNSET:
            field_dict["submittedEnd"] = submitted_end
        if units is not UNSET:
            field_dict["units"] = units
        if rate is not UNSET:
            field_dict["rate"] = rate
        if comments is not UNSET:
            field_dict["comments"] = comments
        if hidden_comments is not UNSET:
            field_dict["hiddenComments"] = hidden_comments
        if breaks is not UNSET:
            field_dict["breaks"] = breaks
        if attachment is not UNSET:
            field_dict["attachment"] = attachment
        if source is not UNSET:
            field_dict["source"] = source
        if location_is_deleted is not UNSET:
            field_dict["locationIsDeleted"] = location_is_deleted
        if dimension_value_ids is not UNSET:
            field_dict["dimensionValueIds"] = dimension_value_ids

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.attachment import Attachment
        from ..models.timesheet_break_submit_model import TimesheetBreakSubmitModel

        d = src_dict.copy()
        id = d.pop("id", UNSET)

        employee_id = d.pop("employeeId", UNSET)

        location_id = d.pop("locationId", UNSET)

        work_type_id = d.pop("workTypeId", UNSET)

        pay_category_id = d.pop("payCategoryId", UNSET)

        leave_category_id = d.pop("leaveCategoryId", UNSET)

        leave_request_id = d.pop("leaveRequestId", UNSET)

        classification_id = d.pop("classificationId", UNSET)

        shift_condition_ids = cast(List[int], d.pop("shiftConditionIds", UNSET))

        _start = d.pop("start", UNSET)
        start: Union[Unset, datetime.datetime]
        if isinstance(_start, Unset):
            start = UNSET
        else:
            start = isoparse(_start)

        _end = d.pop("end", UNSET)
        end: Union[Unset, datetime.datetime]
        if isinstance(_end, Unset):
            end = UNSET
        else:
            end = isoparse(_end)

        _submitted_start = d.pop("submittedStart", UNSET)
        submitted_start: Union[Unset, datetime.datetime]
        if isinstance(_submitted_start, Unset):
            submitted_start = UNSET
        else:
            submitted_start = isoparse(_submitted_start)

        _submitted_end = d.pop("submittedEnd", UNSET)
        submitted_end: Union[Unset, datetime.datetime]
        if isinstance(_submitted_end, Unset):
            submitted_end = UNSET
        else:
            submitted_end = isoparse(_submitted_end)

        units = d.pop("units", UNSET)

        rate = d.pop("rate", UNSET)

        comments = d.pop("comments", UNSET)

        hidden_comments = d.pop("hiddenComments", UNSET)

        breaks = []
        _breaks = d.pop("breaks", UNSET)
        for breaks_item_data in _breaks or []:
            breaks_item = TimesheetBreakSubmitModel.from_dict(breaks_item_data)

            breaks.append(breaks_item)

        _attachment = d.pop("attachment", UNSET)
        attachment: Union[Unset, Attachment]
        if isinstance(_attachment, Unset):
            attachment = UNSET
        else:
            attachment = Attachment.from_dict(_attachment)

        _source = d.pop("source", UNSET)
        source: Union[Unset, ManagerTimesheetSubmitModelNullableExternalService]
        if isinstance(_source, Unset):
            source = UNSET
        else:
            source = ManagerTimesheetSubmitModelNullableExternalService(_source)

        location_is_deleted = d.pop("locationIsDeleted", UNSET)

        dimension_value_ids = cast(List[int], d.pop("dimensionValueIds", UNSET))

        manager_timesheet_submit_model = cls(
            id=id,
            employee_id=employee_id,
            location_id=location_id,
            work_type_id=work_type_id,
            pay_category_id=pay_category_id,
            leave_category_id=leave_category_id,
            leave_request_id=leave_request_id,
            classification_id=classification_id,
            shift_condition_ids=shift_condition_ids,
            start=start,
            end=end,
            submitted_start=submitted_start,
            submitted_end=submitted_end,
            units=units,
            rate=rate,
            comments=comments,
            hidden_comments=hidden_comments,
            breaks=breaks,
            attachment=attachment,
            source=source,
            location_is_deleted=location_is_deleted,
            dimension_value_ids=dimension_value_ids,
        )

        manager_timesheet_submit_model.additional_properties = d
        return manager_timesheet_submit_model

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
