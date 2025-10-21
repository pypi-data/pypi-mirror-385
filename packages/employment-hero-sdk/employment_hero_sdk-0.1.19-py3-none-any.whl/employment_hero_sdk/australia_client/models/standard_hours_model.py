from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.standard_hours_model_nullable_advanced_work_week_configuration_option import (
    StandardHoursModelNullableAdvancedWorkWeekConfigurationOption,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.standard_hours_day_model import StandardHoursDayModel


T = TypeVar("T", bound="StandardHoursModel")


@_attrs_define
class StandardHoursModel:
    """
    Attributes:
        employee_id (Union[Unset, int]):
        standard_hours_per_week (Union[Unset, float]):
        standard_hours_per_day (Union[Unset, float]):
        use_advanced_work_week (Union[Unset, bool]):
        standard_work_days (Union[Unset, List['StandardHoursDayModel']]):
        full_time_equivalent_hours (Union[Unset, float]):
        advanced_work_week_configuration (Union[Unset, StandardHoursModelNullableAdvancedWorkWeekConfigurationOption]):
    """

    employee_id: Union[Unset, int] = UNSET
    standard_hours_per_week: Union[Unset, float] = UNSET
    standard_hours_per_day: Union[Unset, float] = UNSET
    use_advanced_work_week: Union[Unset, bool] = UNSET
    standard_work_days: Union[Unset, List["StandardHoursDayModel"]] = UNSET
    full_time_equivalent_hours: Union[Unset, float] = UNSET
    advanced_work_week_configuration: Union[Unset, StandardHoursModelNullableAdvancedWorkWeekConfigurationOption] = (
        UNSET
    )
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        employee_id = self.employee_id

        standard_hours_per_week = self.standard_hours_per_week

        standard_hours_per_day = self.standard_hours_per_day

        use_advanced_work_week = self.use_advanced_work_week

        standard_work_days: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.standard_work_days, Unset):
            standard_work_days = []
            for standard_work_days_item_data in self.standard_work_days:
                standard_work_days_item = standard_work_days_item_data.to_dict()
                standard_work_days.append(standard_work_days_item)

        full_time_equivalent_hours = self.full_time_equivalent_hours

        advanced_work_week_configuration: Union[Unset, str] = UNSET
        if not isinstance(self.advanced_work_week_configuration, Unset):
            advanced_work_week_configuration = self.advanced_work_week_configuration.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if standard_hours_per_week is not UNSET:
            field_dict["standardHoursPerWeek"] = standard_hours_per_week
        if standard_hours_per_day is not UNSET:
            field_dict["standardHoursPerDay"] = standard_hours_per_day
        if use_advanced_work_week is not UNSET:
            field_dict["useAdvancedWorkWeek"] = use_advanced_work_week
        if standard_work_days is not UNSET:
            field_dict["standardWorkDays"] = standard_work_days
        if full_time_equivalent_hours is not UNSET:
            field_dict["fullTimeEquivalentHours"] = full_time_equivalent_hours
        if advanced_work_week_configuration is not UNSET:
            field_dict["advancedWorkWeekConfiguration"] = advanced_work_week_configuration

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.standard_hours_day_model import StandardHoursDayModel

        d = src_dict.copy()
        employee_id = d.pop("employeeId", UNSET)

        standard_hours_per_week = d.pop("standardHoursPerWeek", UNSET)

        standard_hours_per_day = d.pop("standardHoursPerDay", UNSET)

        use_advanced_work_week = d.pop("useAdvancedWorkWeek", UNSET)

        standard_work_days = []
        _standard_work_days = d.pop("standardWorkDays", UNSET)
        for standard_work_days_item_data in _standard_work_days or []:
            standard_work_days_item = StandardHoursDayModel.from_dict(standard_work_days_item_data)

            standard_work_days.append(standard_work_days_item)

        full_time_equivalent_hours = d.pop("fullTimeEquivalentHours", UNSET)

        _advanced_work_week_configuration = d.pop("advancedWorkWeekConfiguration", UNSET)
        advanced_work_week_configuration: Union[Unset, StandardHoursModelNullableAdvancedWorkWeekConfigurationOption]
        if isinstance(_advanced_work_week_configuration, Unset):
            advanced_work_week_configuration = UNSET
        else:
            advanced_work_week_configuration = StandardHoursModelNullableAdvancedWorkWeekConfigurationOption(
                _advanced_work_week_configuration
            )

        standard_hours_model = cls(
            employee_id=employee_id,
            standard_hours_per_week=standard_hours_per_week,
            standard_hours_per_day=standard_hours_per_day,
            use_advanced_work_week=use_advanced_work_week,
            standard_work_days=standard_work_days,
            full_time_equivalent_hours=full_time_equivalent_hours,
            advanced_work_week_configuration=advanced_work_week_configuration,
        )

        standard_hours_model.additional_properties = d
        return standard_hours_model

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
