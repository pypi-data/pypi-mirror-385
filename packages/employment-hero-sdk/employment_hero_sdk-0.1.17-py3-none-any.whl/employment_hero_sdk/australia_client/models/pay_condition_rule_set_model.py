import datetime
from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.pay_condition_rule_set_model_nullable_shift_consolidation_option import (
    PayConditionRuleSetModelNullableShiftConsolidationOption,
)
from ..models.pay_condition_rule_set_model_rule_set_period_type import PayConditionRuleSetModelRuleSetPeriodType
from ..types import UNSET, Unset

T = TypeVar("T", bound="PayConditionRuleSetModel")


@_attrs_define
class PayConditionRuleSetModel:
    """
    Attributes:
        id (Union[Unset, int]):
        name (Union[Unset, str]):
        description (Union[Unset, str]):
        period_type (Union[Unset, PayConditionRuleSetModelRuleSetPeriodType]):
        day_of_week_ending (Union[Unset, int]):
        day_of_month_ending (Union[Unset, int]):
        period_ending (Union[Unset, datetime.datetime]):
        shift_consolidation_option (Union[Unset, PayConditionRuleSetModelNullableShiftConsolidationOption]):
        shift_consolidation_threshold (Union[Unset, str]):
        rules_json (Union[Unset, str]):
        disabled_rules (Union[Unset, List[str]]):
    """

    id: Union[Unset, int] = UNSET
    name: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    period_type: Union[Unset, PayConditionRuleSetModelRuleSetPeriodType] = UNSET
    day_of_week_ending: Union[Unset, int] = UNSET
    day_of_month_ending: Union[Unset, int] = UNSET
    period_ending: Union[Unset, datetime.datetime] = UNSET
    shift_consolidation_option: Union[Unset, PayConditionRuleSetModelNullableShiftConsolidationOption] = UNSET
    shift_consolidation_threshold: Union[Unset, str] = UNSET
    rules_json: Union[Unset, str] = UNSET
    disabled_rules: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        name = self.name

        description = self.description

        period_type: Union[Unset, str] = UNSET
        if not isinstance(self.period_type, Unset):
            period_type = self.period_type.value

        day_of_week_ending = self.day_of_week_ending

        day_of_month_ending = self.day_of_month_ending

        period_ending: Union[Unset, str] = UNSET
        if not isinstance(self.period_ending, Unset):
            period_ending = self.period_ending.isoformat()

        shift_consolidation_option: Union[Unset, str] = UNSET
        if not isinstance(self.shift_consolidation_option, Unset):
            shift_consolidation_option = self.shift_consolidation_option.value

        shift_consolidation_threshold = self.shift_consolidation_threshold

        rules_json = self.rules_json

        disabled_rules: Union[Unset, List[str]] = UNSET
        if not isinstance(self.disabled_rules, Unset):
            disabled_rules = self.disabled_rules

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if period_type is not UNSET:
            field_dict["periodType"] = period_type
        if day_of_week_ending is not UNSET:
            field_dict["dayOfWeekEnding"] = day_of_week_ending
        if day_of_month_ending is not UNSET:
            field_dict["dayOfMonthEnding"] = day_of_month_ending
        if period_ending is not UNSET:
            field_dict["periodEnding"] = period_ending
        if shift_consolidation_option is not UNSET:
            field_dict["shiftConsolidationOption"] = shift_consolidation_option
        if shift_consolidation_threshold is not UNSET:
            field_dict["shiftConsolidationThreshold"] = shift_consolidation_threshold
        if rules_json is not UNSET:
            field_dict["rulesJson"] = rules_json
        if disabled_rules is not UNSET:
            field_dict["disabledRules"] = disabled_rules

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        _period_type = d.pop("periodType", UNSET)
        period_type: Union[Unset, PayConditionRuleSetModelRuleSetPeriodType]
        if isinstance(_period_type, Unset):
            period_type = UNSET
        else:
            period_type = PayConditionRuleSetModelRuleSetPeriodType(_period_type)

        day_of_week_ending = d.pop("dayOfWeekEnding", UNSET)

        day_of_month_ending = d.pop("dayOfMonthEnding", UNSET)

        _period_ending = d.pop("periodEnding", UNSET)
        period_ending: Union[Unset, datetime.datetime]
        if isinstance(_period_ending, Unset):
            period_ending = UNSET
        else:
            period_ending = isoparse(_period_ending)

        _shift_consolidation_option = d.pop("shiftConsolidationOption", UNSET)
        shift_consolidation_option: Union[Unset, PayConditionRuleSetModelNullableShiftConsolidationOption]
        if isinstance(_shift_consolidation_option, Unset):
            shift_consolidation_option = UNSET
        else:
            shift_consolidation_option = PayConditionRuleSetModelNullableShiftConsolidationOption(
                _shift_consolidation_option
            )

        shift_consolidation_threshold = d.pop("shiftConsolidationThreshold", UNSET)

        rules_json = d.pop("rulesJson", UNSET)

        disabled_rules = cast(List[str], d.pop("disabledRules", UNSET))

        pay_condition_rule_set_model = cls(
            id=id,
            name=name,
            description=description,
            period_type=period_type,
            day_of_week_ending=day_of_week_ending,
            day_of_month_ending=day_of_month_ending,
            period_ending=period_ending,
            shift_consolidation_option=shift_consolidation_option,
            shift_consolidation_threshold=shift_consolidation_threshold,
            rules_json=rules_json,
            disabled_rules=disabled_rules,
        )

        pay_condition_rule_set_model.additional_properties = d
        return pay_condition_rule_set_model

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
