import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.basic_kiosk_employee_model import BasicKioskEmployeeModel
    from ..models.reporting_dimension_value_base_api_model import ReportingDimensionValueBaseApiModel
    from ..models.shift_condition_model import ShiftConditionModel
    from ..models.time_and_attendance_break_model import TimeAndAttendanceBreakModel


T = TypeVar("T", bound="AuTimeAndAttendanceShiftModel")


@_attrs_define
class AuTimeAndAttendanceShiftModel:
    """
    Attributes:
        classification_id (Union[Unset, int]):
        classification_name (Union[Unset, str]):
        id (Union[Unset, int]):
        start_time_local (Union[Unset, datetime.datetime]):
        start_time_utc (Union[Unset, datetime.datetime]):
        end_time_utc (Union[Unset, datetime.datetime]):
        end_time_local (Union[Unset, datetime.datetime]):
        location_id (Union[Unset, int]):
        location_fully_qualified_name (Union[Unset, str]):
        work_type_id (Union[Unset, int]):
        work_type_name (Union[Unset, str]):
        kiosk_id (Union[Unset, int]):
        kiosk_name (Union[Unset, str]):
        timesheet_line_id (Union[Unset, int]):
        employee (Union[Unset, BasicKioskEmployeeModel]):
        breaks (Union[Unset, List['TimeAndAttendanceBreakModel']]):
        shift_conditions (Union[Unset, List['ShiftConditionModel']]):
        dimension_values (Union[Unset, List['ReportingDimensionValueBaseApiModel']]):
    """

    classification_id: Union[Unset, int] = UNSET
    classification_name: Union[Unset, str] = UNSET
    id: Union[Unset, int] = UNSET
    start_time_local: Union[Unset, datetime.datetime] = UNSET
    start_time_utc: Union[Unset, datetime.datetime] = UNSET
    end_time_utc: Union[Unset, datetime.datetime] = UNSET
    end_time_local: Union[Unset, datetime.datetime] = UNSET
    location_id: Union[Unset, int] = UNSET
    location_fully_qualified_name: Union[Unset, str] = UNSET
    work_type_id: Union[Unset, int] = UNSET
    work_type_name: Union[Unset, str] = UNSET
    kiosk_id: Union[Unset, int] = UNSET
    kiosk_name: Union[Unset, str] = UNSET
    timesheet_line_id: Union[Unset, int] = UNSET
    employee: Union[Unset, "BasicKioskEmployeeModel"] = UNSET
    breaks: Union[Unset, List["TimeAndAttendanceBreakModel"]] = UNSET
    shift_conditions: Union[Unset, List["ShiftConditionModel"]] = UNSET
    dimension_values: Union[Unset, List["ReportingDimensionValueBaseApiModel"]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        classification_id = self.classification_id

        classification_name = self.classification_name

        id = self.id

        start_time_local: Union[Unset, str] = UNSET
        if not isinstance(self.start_time_local, Unset):
            start_time_local = self.start_time_local.isoformat()

        start_time_utc: Union[Unset, str] = UNSET
        if not isinstance(self.start_time_utc, Unset):
            start_time_utc = self.start_time_utc.isoformat()

        end_time_utc: Union[Unset, str] = UNSET
        if not isinstance(self.end_time_utc, Unset):
            end_time_utc = self.end_time_utc.isoformat()

        end_time_local: Union[Unset, str] = UNSET
        if not isinstance(self.end_time_local, Unset):
            end_time_local = self.end_time_local.isoformat()

        location_id = self.location_id

        location_fully_qualified_name = self.location_fully_qualified_name

        work_type_id = self.work_type_id

        work_type_name = self.work_type_name

        kiosk_id = self.kiosk_id

        kiosk_name = self.kiosk_name

        timesheet_line_id = self.timesheet_line_id

        employee: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.employee, Unset):
            employee = self.employee.to_dict()

        breaks: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.breaks, Unset):
            breaks = []
            for breaks_item_data in self.breaks:
                breaks_item = breaks_item_data.to_dict()
                breaks.append(breaks_item)

        shift_conditions: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.shift_conditions, Unset):
            shift_conditions = []
            for shift_conditions_item_data in self.shift_conditions:
                shift_conditions_item = shift_conditions_item_data.to_dict()
                shift_conditions.append(shift_conditions_item)

        dimension_values: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.dimension_values, Unset):
            dimension_values = []
            for dimension_values_item_data in self.dimension_values:
                dimension_values_item = dimension_values_item_data.to_dict()
                dimension_values.append(dimension_values_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if classification_id is not UNSET:
            field_dict["classificationId"] = classification_id
        if classification_name is not UNSET:
            field_dict["classificationName"] = classification_name
        if id is not UNSET:
            field_dict["id"] = id
        if start_time_local is not UNSET:
            field_dict["startTimeLocal"] = start_time_local
        if start_time_utc is not UNSET:
            field_dict["startTimeUtc"] = start_time_utc
        if end_time_utc is not UNSET:
            field_dict["endTimeUtc"] = end_time_utc
        if end_time_local is not UNSET:
            field_dict["endTimeLocal"] = end_time_local
        if location_id is not UNSET:
            field_dict["locationId"] = location_id
        if location_fully_qualified_name is not UNSET:
            field_dict["locationFullyQualifiedName"] = location_fully_qualified_name
        if work_type_id is not UNSET:
            field_dict["workTypeId"] = work_type_id
        if work_type_name is not UNSET:
            field_dict["workTypeName"] = work_type_name
        if kiosk_id is not UNSET:
            field_dict["kioskId"] = kiosk_id
        if kiosk_name is not UNSET:
            field_dict["kioskName"] = kiosk_name
        if timesheet_line_id is not UNSET:
            field_dict["timesheetLineId"] = timesheet_line_id
        if employee is not UNSET:
            field_dict["employee"] = employee
        if breaks is not UNSET:
            field_dict["breaks"] = breaks
        if shift_conditions is not UNSET:
            field_dict["shiftConditions"] = shift_conditions
        if dimension_values is not UNSET:
            field_dict["dimensionValues"] = dimension_values

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.basic_kiosk_employee_model import BasicKioskEmployeeModel
        from ..models.reporting_dimension_value_base_api_model import ReportingDimensionValueBaseApiModel
        from ..models.shift_condition_model import ShiftConditionModel
        from ..models.time_and_attendance_break_model import TimeAndAttendanceBreakModel

        d = src_dict.copy()
        classification_id = d.pop("classificationId", UNSET)

        classification_name = d.pop("classificationName", UNSET)

        id = d.pop("id", UNSET)

        _start_time_local = d.pop("startTimeLocal", UNSET)
        start_time_local: Union[Unset, datetime.datetime]
        if isinstance(_start_time_local, Unset):
            start_time_local = UNSET
        else:
            start_time_local = isoparse(_start_time_local)

        _start_time_utc = d.pop("startTimeUtc", UNSET)
        start_time_utc: Union[Unset, datetime.datetime]
        if isinstance(_start_time_utc, Unset):
            start_time_utc = UNSET
        else:
            start_time_utc = isoparse(_start_time_utc)

        _end_time_utc = d.pop("endTimeUtc", UNSET)
        end_time_utc: Union[Unset, datetime.datetime]
        if isinstance(_end_time_utc, Unset):
            end_time_utc = UNSET
        else:
            end_time_utc = isoparse(_end_time_utc)

        _end_time_local = d.pop("endTimeLocal", UNSET)
        end_time_local: Union[Unset, datetime.datetime]
        if isinstance(_end_time_local, Unset):
            end_time_local = UNSET
        else:
            end_time_local = isoparse(_end_time_local)

        location_id = d.pop("locationId", UNSET)

        location_fully_qualified_name = d.pop("locationFullyQualifiedName", UNSET)

        work_type_id = d.pop("workTypeId", UNSET)

        work_type_name = d.pop("workTypeName", UNSET)

        kiosk_id = d.pop("kioskId", UNSET)

        kiosk_name = d.pop("kioskName", UNSET)

        timesheet_line_id = d.pop("timesheetLineId", UNSET)

        _employee = d.pop("employee", UNSET)
        employee: Union[Unset, BasicKioskEmployeeModel]
        if isinstance(_employee, Unset):
            employee = UNSET
        else:
            employee = BasicKioskEmployeeModel.from_dict(_employee)

        breaks = []
        _breaks = d.pop("breaks", UNSET)
        for breaks_item_data in _breaks or []:
            breaks_item = TimeAndAttendanceBreakModel.from_dict(breaks_item_data)

            breaks.append(breaks_item)

        shift_conditions = []
        _shift_conditions = d.pop("shiftConditions", UNSET)
        for shift_conditions_item_data in _shift_conditions or []:
            shift_conditions_item = ShiftConditionModel.from_dict(shift_conditions_item_data)

            shift_conditions.append(shift_conditions_item)

        dimension_values = []
        _dimension_values = d.pop("dimensionValues", UNSET)
        for dimension_values_item_data in _dimension_values or []:
            dimension_values_item = ReportingDimensionValueBaseApiModel.from_dict(dimension_values_item_data)

            dimension_values.append(dimension_values_item)

        au_time_and_attendance_shift_model = cls(
            classification_id=classification_id,
            classification_name=classification_name,
            id=id,
            start_time_local=start_time_local,
            start_time_utc=start_time_utc,
            end_time_utc=end_time_utc,
            end_time_local=end_time_local,
            location_id=location_id,
            location_fully_qualified_name=location_fully_qualified_name,
            work_type_id=work_type_id,
            work_type_name=work_type_name,
            kiosk_id=kiosk_id,
            kiosk_name=kiosk_name,
            timesheet_line_id=timesheet_line_id,
            employee=employee,
            breaks=breaks,
            shift_conditions=shift_conditions,
            dimension_values=dimension_values,
        )

        au_time_and_attendance_shift_model.additional_properties = d
        return au_time_and_attendance_shift_model

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
