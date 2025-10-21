import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.nominal_classification import NominalClassification
    from ..models.nominal_leave_category import NominalLeaveCategory
    from ..models.nominal_location import NominalLocation
    from ..models.nominal_work_type import NominalWorkType


T = TypeVar("T", bound="ShiftPartModel")


@_attrs_define
class ShiftPartModel:
    """
    Attributes:
        is_break (Union[Unset, bool]):
        is_paid_break (Union[Unset, bool]):
        start_time (Union[Unset, datetime.datetime]):
        end_time (Union[Unset, datetime.datetime]):
        effective_duration (Union[Unset, str]):
        actual_duration (Union[Unset, str]):
        pay_category (Union[Unset, str]):
        pay_category_id (Union[Unset, int]):
        cost (Union[Unset, float]):
        rate_multiplier (Union[Unset, float]):
        base_rate (Union[Unset, float]):
        calculated_rate (Union[Unset, float]):
        display_duration (Union[Unset, str]):
        work_type (Union[Unset, NominalWorkType]):
        classification (Union[Unset, NominalClassification]):
        leave_category (Union[Unset, NominalLeaveCategory]):
        location (Union[Unset, NominalLocation]):
        is_allowance_or_unit_based (Union[Unset, bool]):
    """

    is_break: Union[Unset, bool] = UNSET
    is_paid_break: Union[Unset, bool] = UNSET
    start_time: Union[Unset, datetime.datetime] = UNSET
    end_time: Union[Unset, datetime.datetime] = UNSET
    effective_duration: Union[Unset, str] = UNSET
    actual_duration: Union[Unset, str] = UNSET
    pay_category: Union[Unset, str] = UNSET
    pay_category_id: Union[Unset, int] = UNSET
    cost: Union[Unset, float] = UNSET
    rate_multiplier: Union[Unset, float] = UNSET
    base_rate: Union[Unset, float] = UNSET
    calculated_rate: Union[Unset, float] = UNSET
    display_duration: Union[Unset, str] = UNSET
    work_type: Union[Unset, "NominalWorkType"] = UNSET
    classification: Union[Unset, "NominalClassification"] = UNSET
    leave_category: Union[Unset, "NominalLeaveCategory"] = UNSET
    location: Union[Unset, "NominalLocation"] = UNSET
    is_allowance_or_unit_based: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        is_break = self.is_break

        is_paid_break = self.is_paid_break

        start_time: Union[Unset, str] = UNSET
        if not isinstance(self.start_time, Unset):
            start_time = self.start_time.isoformat()

        end_time: Union[Unset, str] = UNSET
        if not isinstance(self.end_time, Unset):
            end_time = self.end_time.isoformat()

        effective_duration = self.effective_duration

        actual_duration = self.actual_duration

        pay_category = self.pay_category

        pay_category_id = self.pay_category_id

        cost = self.cost

        rate_multiplier = self.rate_multiplier

        base_rate = self.base_rate

        calculated_rate = self.calculated_rate

        display_duration = self.display_duration

        work_type: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.work_type, Unset):
            work_type = self.work_type.to_dict()

        classification: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.classification, Unset):
            classification = self.classification.to_dict()

        leave_category: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.leave_category, Unset):
            leave_category = self.leave_category.to_dict()

        location: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.location, Unset):
            location = self.location.to_dict()

        is_allowance_or_unit_based = self.is_allowance_or_unit_based

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if is_break is not UNSET:
            field_dict["isBreak"] = is_break
        if is_paid_break is not UNSET:
            field_dict["isPaidBreak"] = is_paid_break
        if start_time is not UNSET:
            field_dict["startTime"] = start_time
        if end_time is not UNSET:
            field_dict["endTime"] = end_time
        if effective_duration is not UNSET:
            field_dict["effectiveDuration"] = effective_duration
        if actual_duration is not UNSET:
            field_dict["actualDuration"] = actual_duration
        if pay_category is not UNSET:
            field_dict["payCategory"] = pay_category
        if pay_category_id is not UNSET:
            field_dict["payCategoryId"] = pay_category_id
        if cost is not UNSET:
            field_dict["cost"] = cost
        if rate_multiplier is not UNSET:
            field_dict["rateMultiplier"] = rate_multiplier
        if base_rate is not UNSET:
            field_dict["baseRate"] = base_rate
        if calculated_rate is not UNSET:
            field_dict["calculatedRate"] = calculated_rate
        if display_duration is not UNSET:
            field_dict["displayDuration"] = display_duration
        if work_type is not UNSET:
            field_dict["workType"] = work_type
        if classification is not UNSET:
            field_dict["classification"] = classification
        if leave_category is not UNSET:
            field_dict["leaveCategory"] = leave_category
        if location is not UNSET:
            field_dict["location"] = location
        if is_allowance_or_unit_based is not UNSET:
            field_dict["isAllowanceOrUnitBased"] = is_allowance_or_unit_based

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.nominal_classification import NominalClassification
        from ..models.nominal_leave_category import NominalLeaveCategory
        from ..models.nominal_location import NominalLocation
        from ..models.nominal_work_type import NominalWorkType

        d = src_dict.copy()
        is_break = d.pop("isBreak", UNSET)

        is_paid_break = d.pop("isPaidBreak", UNSET)

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

        effective_duration = d.pop("effectiveDuration", UNSET)

        actual_duration = d.pop("actualDuration", UNSET)

        pay_category = d.pop("payCategory", UNSET)

        pay_category_id = d.pop("payCategoryId", UNSET)

        cost = d.pop("cost", UNSET)

        rate_multiplier = d.pop("rateMultiplier", UNSET)

        base_rate = d.pop("baseRate", UNSET)

        calculated_rate = d.pop("calculatedRate", UNSET)

        display_duration = d.pop("displayDuration", UNSET)

        _work_type = d.pop("workType", UNSET)
        work_type: Union[Unset, NominalWorkType]
        if isinstance(_work_type, Unset):
            work_type = UNSET
        else:
            work_type = NominalWorkType.from_dict(_work_type)

        _classification = d.pop("classification", UNSET)
        classification: Union[Unset, NominalClassification]
        if isinstance(_classification, Unset):
            classification = UNSET
        else:
            classification = NominalClassification.from_dict(_classification)

        _leave_category = d.pop("leaveCategory", UNSET)
        leave_category: Union[Unset, NominalLeaveCategory]
        if isinstance(_leave_category, Unset):
            leave_category = UNSET
        else:
            leave_category = NominalLeaveCategory.from_dict(_leave_category)

        _location = d.pop("location", UNSET)
        location: Union[Unset, NominalLocation]
        if isinstance(_location, Unset):
            location = UNSET
        else:
            location = NominalLocation.from_dict(_location)

        is_allowance_or_unit_based = d.pop("isAllowanceOrUnitBased", UNSET)

        shift_part_model = cls(
            is_break=is_break,
            is_paid_break=is_paid_break,
            start_time=start_time,
            end_time=end_time,
            effective_duration=effective_duration,
            actual_duration=actual_duration,
            pay_category=pay_category,
            pay_category_id=pay_category_id,
            cost=cost,
            rate_multiplier=rate_multiplier,
            base_rate=base_rate,
            calculated_rate=calculated_rate,
            display_duration=display_duration,
            work_type=work_type,
            classification=classification,
            leave_category=leave_category,
            location=location,
            is_allowance_or_unit_based=is_allowance_or_unit_based,
        )

        shift_part_model.additional_properties = d
        return shift_part_model

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
