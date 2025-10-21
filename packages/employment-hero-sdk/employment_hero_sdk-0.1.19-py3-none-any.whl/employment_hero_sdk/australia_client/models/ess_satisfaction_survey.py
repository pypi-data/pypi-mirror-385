import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.ess_satisfaction_survey_employee_satisfaction_value import EssSatisfactionSurveyEmployeeSatisfactionValue
from ..types import UNSET, Unset

T = TypeVar("T", bound="EssSatisfactionSurvey")


@_attrs_define
class EssSatisfactionSurvey:
    """
    Attributes:
        value (Union[Unset, EssSatisfactionSurveyEmployeeSatisfactionValue]):
        week_start_date (Union[Unset, datetime.datetime]):
    """

    value: Union[Unset, EssSatisfactionSurveyEmployeeSatisfactionValue] = UNSET
    week_start_date: Union[Unset, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        value: Union[Unset, str] = UNSET
        if not isinstance(self.value, Unset):
            value = self.value.value

        week_start_date: Union[Unset, str] = UNSET
        if not isinstance(self.week_start_date, Unset):
            week_start_date = self.week_start_date.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if value is not UNSET:
            field_dict["value"] = value
        if week_start_date is not UNSET:
            field_dict["weekStartDate"] = week_start_date

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _value = d.pop("value", UNSET)
        value: Union[Unset, EssSatisfactionSurveyEmployeeSatisfactionValue]
        if isinstance(_value, Unset):
            value = UNSET
        else:
            value = EssSatisfactionSurveyEmployeeSatisfactionValue(_value)

        _week_start_date = d.pop("weekStartDate", UNSET)
        week_start_date: Union[Unset, datetime.datetime]
        if isinstance(_week_start_date, Unset):
            week_start_date = UNSET
        else:
            week_start_date = isoparse(_week_start_date)

        ess_satisfaction_survey = cls(
            value=value,
            week_start_date=week_start_date,
        )

        ess_satisfaction_survey.additional_properties = d
        return ess_satisfaction_survey

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
