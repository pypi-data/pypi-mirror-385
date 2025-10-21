import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.au_individual_timesheet_line_model_external_service import AuIndividualTimesheetLineModelExternalService
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.attachment import Attachment
    from ..models.timesheet_break_modelv_3 import TimesheetBreakModelv3
    from ..models.timesheet_shift_condition_modelv_3 import TimesheetShiftConditionModelv3


T = TypeVar("T", bound="AuIndividualTimesheetLineModel")


@_attrs_define
class AuIndividualTimesheetLineModel:
    """
    Attributes:
        classification_id (Union[Unset, int]):
        classification (Union[Unset, str]):
        location_is_deleted (Union[Unset, bool]):
        id (Union[Unset, int]):
        employee_id (Union[Unset, int]):
        start_time (Union[Unset, datetime.datetime]):
        end_time (Union[Unset, datetime.datetime]):
        units (Union[Unset, float]):
        work_type_id (Union[Unset, int]):
        location_id (Union[Unset, int]):
        comments (Union[Unset, str]):
        breaks (Union[Unset, List['TimesheetBreakModelv3']]):
        status (Union[Unset, str]):
        rate (Union[Unset, float]):
        leave_category_id (Union[Unset, int]):
        pay_category_id (Union[Unset, int]):
        external_id (Union[Unset, str]):
        source (Union[Unset, AuIndividualTimesheetLineModelExternalService]):
        attachment_id (Union[Unset, int]):
        shift_condition_ids (Union[Unset, List[int]]):
        work_type (Union[Unset, str]):
        fully_qualified_location_name (Union[Unset, str]):
        shift_conditions (Union[Unset, List['TimesheetShiftConditionModelv3']]):
        hidden_comments (Union[Unset, str]):
        attachment (Union[Unset, Attachment]):
        dimension_value_ids (Union[Unset, List[int]]):
    """

    classification_id: Union[Unset, int] = UNSET
    classification: Union[Unset, str] = UNSET
    location_is_deleted: Union[Unset, bool] = UNSET
    id: Union[Unset, int] = UNSET
    employee_id: Union[Unset, int] = UNSET
    start_time: Union[Unset, datetime.datetime] = UNSET
    end_time: Union[Unset, datetime.datetime] = UNSET
    units: Union[Unset, float] = UNSET
    work_type_id: Union[Unset, int] = UNSET
    location_id: Union[Unset, int] = UNSET
    comments: Union[Unset, str] = UNSET
    breaks: Union[Unset, List["TimesheetBreakModelv3"]] = UNSET
    status: Union[Unset, str] = UNSET
    rate: Union[Unset, float] = UNSET
    leave_category_id: Union[Unset, int] = UNSET
    pay_category_id: Union[Unset, int] = UNSET
    external_id: Union[Unset, str] = UNSET
    source: Union[Unset, AuIndividualTimesheetLineModelExternalService] = UNSET
    attachment_id: Union[Unset, int] = UNSET
    shift_condition_ids: Union[Unset, List[int]] = UNSET
    work_type: Union[Unset, str] = UNSET
    fully_qualified_location_name: Union[Unset, str] = UNSET
    shift_conditions: Union[Unset, List["TimesheetShiftConditionModelv3"]] = UNSET
    hidden_comments: Union[Unset, str] = UNSET
    attachment: Union[Unset, "Attachment"] = UNSET
    dimension_value_ids: Union[Unset, List[int]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        classification_id = self.classification_id

        classification = self.classification

        location_is_deleted = self.location_is_deleted

        id = self.id

        employee_id = self.employee_id

        start_time: Union[Unset, str] = UNSET
        if not isinstance(self.start_time, Unset):
            start_time = self.start_time.isoformat()

        end_time: Union[Unset, str] = UNSET
        if not isinstance(self.end_time, Unset):
            end_time = self.end_time.isoformat()

        units = self.units

        work_type_id = self.work_type_id

        location_id = self.location_id

        comments = self.comments

        breaks: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.breaks, Unset):
            breaks = []
            for breaks_item_data in self.breaks:
                breaks_item = breaks_item_data.to_dict()
                breaks.append(breaks_item)

        status = self.status

        rate = self.rate

        leave_category_id = self.leave_category_id

        pay_category_id = self.pay_category_id

        external_id = self.external_id

        source: Union[Unset, str] = UNSET
        if not isinstance(self.source, Unset):
            source = self.source.value

        attachment_id = self.attachment_id

        shift_condition_ids: Union[Unset, List[int]] = UNSET
        if not isinstance(self.shift_condition_ids, Unset):
            shift_condition_ids = self.shift_condition_ids

        work_type = self.work_type

        fully_qualified_location_name = self.fully_qualified_location_name

        shift_conditions: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.shift_conditions, Unset):
            shift_conditions = []
            for shift_conditions_item_data in self.shift_conditions:
                shift_conditions_item = shift_conditions_item_data.to_dict()
                shift_conditions.append(shift_conditions_item)

        hidden_comments = self.hidden_comments

        attachment: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.attachment, Unset):
            attachment = self.attachment.to_dict()

        dimension_value_ids: Union[Unset, List[int]] = UNSET
        if not isinstance(self.dimension_value_ids, Unset):
            dimension_value_ids = self.dimension_value_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if classification_id is not UNSET:
            field_dict["classificationId"] = classification_id
        if classification is not UNSET:
            field_dict["classification"] = classification
        if location_is_deleted is not UNSET:
            field_dict["locationIsDeleted"] = location_is_deleted
        if id is not UNSET:
            field_dict["id"] = id
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if start_time is not UNSET:
            field_dict["startTime"] = start_time
        if end_time is not UNSET:
            field_dict["endTime"] = end_time
        if units is not UNSET:
            field_dict["units"] = units
        if work_type_id is not UNSET:
            field_dict["workTypeId"] = work_type_id
        if location_id is not UNSET:
            field_dict["locationId"] = location_id
        if comments is not UNSET:
            field_dict["comments"] = comments
        if breaks is not UNSET:
            field_dict["breaks"] = breaks
        if status is not UNSET:
            field_dict["status"] = status
        if rate is not UNSET:
            field_dict["rate"] = rate
        if leave_category_id is not UNSET:
            field_dict["leaveCategoryId"] = leave_category_id
        if pay_category_id is not UNSET:
            field_dict["payCategoryId"] = pay_category_id
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if source is not UNSET:
            field_dict["source"] = source
        if attachment_id is not UNSET:
            field_dict["attachmentId"] = attachment_id
        if shift_condition_ids is not UNSET:
            field_dict["shiftConditionIds"] = shift_condition_ids
        if work_type is not UNSET:
            field_dict["workType"] = work_type
        if fully_qualified_location_name is not UNSET:
            field_dict["fullyQualifiedLocationName"] = fully_qualified_location_name
        if shift_conditions is not UNSET:
            field_dict["shiftConditions"] = shift_conditions
        if hidden_comments is not UNSET:
            field_dict["hiddenComments"] = hidden_comments
        if attachment is not UNSET:
            field_dict["attachment"] = attachment
        if dimension_value_ids is not UNSET:
            field_dict["dimensionValueIds"] = dimension_value_ids

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.attachment import Attachment
        from ..models.timesheet_break_modelv_3 import TimesheetBreakModelv3
        from ..models.timesheet_shift_condition_modelv_3 import TimesheetShiftConditionModelv3

        d = src_dict.copy()
        classification_id = d.pop("classificationId", UNSET)

        classification = d.pop("classification", UNSET)

        location_is_deleted = d.pop("locationIsDeleted", UNSET)

        id = d.pop("id", UNSET)

        employee_id = d.pop("employeeId", UNSET)

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

        units = d.pop("units", UNSET)

        work_type_id = d.pop("workTypeId", UNSET)

        location_id = d.pop("locationId", UNSET)

        comments = d.pop("comments", UNSET)

        breaks = []
        _breaks = d.pop("breaks", UNSET)
        for breaks_item_data in _breaks or []:
            breaks_item = TimesheetBreakModelv3.from_dict(breaks_item_data)

            breaks.append(breaks_item)

        status = d.pop("status", UNSET)

        rate = d.pop("rate", UNSET)

        leave_category_id = d.pop("leaveCategoryId", UNSET)

        pay_category_id = d.pop("payCategoryId", UNSET)

        external_id = d.pop("externalId", UNSET)

        _source = d.pop("source", UNSET)
        source: Union[Unset, AuIndividualTimesheetLineModelExternalService]
        if isinstance(_source, Unset):
            source = UNSET
        else:
            source = AuIndividualTimesheetLineModelExternalService(_source)

        attachment_id = d.pop("attachmentId", UNSET)

        shift_condition_ids = cast(List[int], d.pop("shiftConditionIds", UNSET))

        work_type = d.pop("workType", UNSET)

        fully_qualified_location_name = d.pop("fullyQualifiedLocationName", UNSET)

        shift_conditions = []
        _shift_conditions = d.pop("shiftConditions", UNSET)
        for shift_conditions_item_data in _shift_conditions or []:
            shift_conditions_item = TimesheetShiftConditionModelv3.from_dict(shift_conditions_item_data)

            shift_conditions.append(shift_conditions_item)

        hidden_comments = d.pop("hiddenComments", UNSET)

        _attachment = d.pop("attachment", UNSET)
        attachment: Union[Unset, Attachment]
        if isinstance(_attachment, Unset):
            attachment = UNSET
        else:
            attachment = Attachment.from_dict(_attachment)

        dimension_value_ids = cast(List[int], d.pop("dimensionValueIds", UNSET))

        au_individual_timesheet_line_model = cls(
            classification_id=classification_id,
            classification=classification,
            location_is_deleted=location_is_deleted,
            id=id,
            employee_id=employee_id,
            start_time=start_time,
            end_time=end_time,
            units=units,
            work_type_id=work_type_id,
            location_id=location_id,
            comments=comments,
            breaks=breaks,
            status=status,
            rate=rate,
            leave_category_id=leave_category_id,
            pay_category_id=pay_category_id,
            external_id=external_id,
            source=source,
            attachment_id=attachment_id,
            shift_condition_ids=shift_condition_ids,
            work_type=work_type,
            fully_qualified_location_name=fully_qualified_location_name,
            shift_conditions=shift_conditions,
            hidden_comments=hidden_comments,
            attachment=attachment,
            dimension_value_ids=dimension_value_ids,
        )

        au_individual_timesheet_line_model.additional_properties = d
        return au_individual_timesheet_line_model

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
