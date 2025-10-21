from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.timesheet_rounding_rules_model_rounding_direction_enum import (
    TimesheetRoundingRulesModelRoundingDirectionEnum,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="TimesheetRoundingRulesModel")


@_attrs_define
class TimesheetRoundingRulesModel:
    """
    Attributes:
        id (Union[Unset, int]):
        shift_start_rounding_direction (Union[Unset, TimesheetRoundingRulesModelRoundingDirectionEnum]):
        shift_start_rounding_interval (Union[Unset, int]):
        shift_end_rounding_direction (Union[Unset, TimesheetRoundingRulesModelRoundingDirectionEnum]):
        shift_end_rounding_interval (Union[Unset, int]):
        break_start_rounding_direction (Union[Unset, TimesheetRoundingRulesModelRoundingDirectionEnum]):
        break_start_rounding_interval (Union[Unset, int]):
        break_end_rounding_direction (Union[Unset, TimesheetRoundingRulesModelRoundingDirectionEnum]):
        break_end_rounding_interval (Union[Unset, int]):
        round_up_to_shift_start_time_rounding_interval (Union[Unset, int]):
        round_down_to_shift_start_time_rounding_interval (Union[Unset, int]):
        round_up_to_shift_end_time_rounding_interval (Union[Unset, int]):
        round_down_to_shift_end_time_rounding_interval (Union[Unset, int]):
    """

    id: Union[Unset, int] = UNSET
    shift_start_rounding_direction: Union[Unset, TimesheetRoundingRulesModelRoundingDirectionEnum] = UNSET
    shift_start_rounding_interval: Union[Unset, int] = UNSET
    shift_end_rounding_direction: Union[Unset, TimesheetRoundingRulesModelRoundingDirectionEnum] = UNSET
    shift_end_rounding_interval: Union[Unset, int] = UNSET
    break_start_rounding_direction: Union[Unset, TimesheetRoundingRulesModelRoundingDirectionEnum] = UNSET
    break_start_rounding_interval: Union[Unset, int] = UNSET
    break_end_rounding_direction: Union[Unset, TimesheetRoundingRulesModelRoundingDirectionEnum] = UNSET
    break_end_rounding_interval: Union[Unset, int] = UNSET
    round_up_to_shift_start_time_rounding_interval: Union[Unset, int] = UNSET
    round_down_to_shift_start_time_rounding_interval: Union[Unset, int] = UNSET
    round_up_to_shift_end_time_rounding_interval: Union[Unset, int] = UNSET
    round_down_to_shift_end_time_rounding_interval: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        shift_start_rounding_direction: Union[Unset, str] = UNSET
        if not isinstance(self.shift_start_rounding_direction, Unset):
            shift_start_rounding_direction = self.shift_start_rounding_direction.value

        shift_start_rounding_interval = self.shift_start_rounding_interval

        shift_end_rounding_direction: Union[Unset, str] = UNSET
        if not isinstance(self.shift_end_rounding_direction, Unset):
            shift_end_rounding_direction = self.shift_end_rounding_direction.value

        shift_end_rounding_interval = self.shift_end_rounding_interval

        break_start_rounding_direction: Union[Unset, str] = UNSET
        if not isinstance(self.break_start_rounding_direction, Unset):
            break_start_rounding_direction = self.break_start_rounding_direction.value

        break_start_rounding_interval = self.break_start_rounding_interval

        break_end_rounding_direction: Union[Unset, str] = UNSET
        if not isinstance(self.break_end_rounding_direction, Unset):
            break_end_rounding_direction = self.break_end_rounding_direction.value

        break_end_rounding_interval = self.break_end_rounding_interval

        round_up_to_shift_start_time_rounding_interval = self.round_up_to_shift_start_time_rounding_interval

        round_down_to_shift_start_time_rounding_interval = self.round_down_to_shift_start_time_rounding_interval

        round_up_to_shift_end_time_rounding_interval = self.round_up_to_shift_end_time_rounding_interval

        round_down_to_shift_end_time_rounding_interval = self.round_down_to_shift_end_time_rounding_interval

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if shift_start_rounding_direction is not UNSET:
            field_dict["shiftStartRoundingDirection"] = shift_start_rounding_direction
        if shift_start_rounding_interval is not UNSET:
            field_dict["shiftStartRoundingInterval"] = shift_start_rounding_interval
        if shift_end_rounding_direction is not UNSET:
            field_dict["shiftEndRoundingDirection"] = shift_end_rounding_direction
        if shift_end_rounding_interval is not UNSET:
            field_dict["shiftEndRoundingInterval"] = shift_end_rounding_interval
        if break_start_rounding_direction is not UNSET:
            field_dict["breakStartRoundingDirection"] = break_start_rounding_direction
        if break_start_rounding_interval is not UNSET:
            field_dict["breakStartRoundingInterval"] = break_start_rounding_interval
        if break_end_rounding_direction is not UNSET:
            field_dict["breakEndRoundingDirection"] = break_end_rounding_direction
        if break_end_rounding_interval is not UNSET:
            field_dict["breakEndRoundingInterval"] = break_end_rounding_interval
        if round_up_to_shift_start_time_rounding_interval is not UNSET:
            field_dict["roundUpToShiftStartTimeRoundingInterval"] = round_up_to_shift_start_time_rounding_interval
        if round_down_to_shift_start_time_rounding_interval is not UNSET:
            field_dict["roundDownToShiftStartTimeRoundingInterval"] = round_down_to_shift_start_time_rounding_interval
        if round_up_to_shift_end_time_rounding_interval is not UNSET:
            field_dict["roundUpToShiftEndTimeRoundingInterval"] = round_up_to_shift_end_time_rounding_interval
        if round_down_to_shift_end_time_rounding_interval is not UNSET:
            field_dict["roundDownToShiftEndTimeRoundingInterval"] = round_down_to_shift_end_time_rounding_interval

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        _shift_start_rounding_direction = d.pop("shiftStartRoundingDirection", UNSET)
        shift_start_rounding_direction: Union[Unset, TimesheetRoundingRulesModelRoundingDirectionEnum]
        if isinstance(_shift_start_rounding_direction, Unset):
            shift_start_rounding_direction = UNSET
        else:
            shift_start_rounding_direction = TimesheetRoundingRulesModelRoundingDirectionEnum(
                _shift_start_rounding_direction
            )

        shift_start_rounding_interval = d.pop("shiftStartRoundingInterval", UNSET)

        _shift_end_rounding_direction = d.pop("shiftEndRoundingDirection", UNSET)
        shift_end_rounding_direction: Union[Unset, TimesheetRoundingRulesModelRoundingDirectionEnum]
        if isinstance(_shift_end_rounding_direction, Unset):
            shift_end_rounding_direction = UNSET
        else:
            shift_end_rounding_direction = TimesheetRoundingRulesModelRoundingDirectionEnum(
                _shift_end_rounding_direction
            )

        shift_end_rounding_interval = d.pop("shiftEndRoundingInterval", UNSET)

        _break_start_rounding_direction = d.pop("breakStartRoundingDirection", UNSET)
        break_start_rounding_direction: Union[Unset, TimesheetRoundingRulesModelRoundingDirectionEnum]
        if isinstance(_break_start_rounding_direction, Unset):
            break_start_rounding_direction = UNSET
        else:
            break_start_rounding_direction = TimesheetRoundingRulesModelRoundingDirectionEnum(
                _break_start_rounding_direction
            )

        break_start_rounding_interval = d.pop("breakStartRoundingInterval", UNSET)

        _break_end_rounding_direction = d.pop("breakEndRoundingDirection", UNSET)
        break_end_rounding_direction: Union[Unset, TimesheetRoundingRulesModelRoundingDirectionEnum]
        if isinstance(_break_end_rounding_direction, Unset):
            break_end_rounding_direction = UNSET
        else:
            break_end_rounding_direction = TimesheetRoundingRulesModelRoundingDirectionEnum(
                _break_end_rounding_direction
            )

        break_end_rounding_interval = d.pop("breakEndRoundingInterval", UNSET)

        round_up_to_shift_start_time_rounding_interval = d.pop("roundUpToShiftStartTimeRoundingInterval", UNSET)

        round_down_to_shift_start_time_rounding_interval = d.pop("roundDownToShiftStartTimeRoundingInterval", UNSET)

        round_up_to_shift_end_time_rounding_interval = d.pop("roundUpToShiftEndTimeRoundingInterval", UNSET)

        round_down_to_shift_end_time_rounding_interval = d.pop("roundDownToShiftEndTimeRoundingInterval", UNSET)

        timesheet_rounding_rules_model = cls(
            id=id,
            shift_start_rounding_direction=shift_start_rounding_direction,
            shift_start_rounding_interval=shift_start_rounding_interval,
            shift_end_rounding_direction=shift_end_rounding_direction,
            shift_end_rounding_interval=shift_end_rounding_interval,
            break_start_rounding_direction=break_start_rounding_direction,
            break_start_rounding_interval=break_start_rounding_interval,
            break_end_rounding_direction=break_end_rounding_direction,
            break_end_rounding_interval=break_end_rounding_interval,
            round_up_to_shift_start_time_rounding_interval=round_up_to_shift_start_time_rounding_interval,
            round_down_to_shift_start_time_rounding_interval=round_down_to_shift_start_time_rounding_interval,
            round_up_to_shift_end_time_rounding_interval=round_up_to_shift_end_time_rounding_interval,
            round_down_to_shift_end_time_rounding_interval=round_down_to_shift_end_time_rounding_interval,
        )

        timesheet_rounding_rules_model.additional_properties = d
        return timesheet_rounding_rules_model

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
