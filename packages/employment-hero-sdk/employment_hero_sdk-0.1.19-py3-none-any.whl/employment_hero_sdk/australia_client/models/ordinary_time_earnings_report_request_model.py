from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="OrdinaryTimeEarningsReportRequestModel")


@_attrs_define
class OrdinaryTimeEarningsReportRequestModel:
    """
    Attributes:
        pay_schedule_id (Union[Unset, int]):
        employing_entity_id (Union[Unset, int]):
        financial_year_ending (Union[Unset, int]):
    """

    pay_schedule_id: Union[Unset, int] = UNSET
    employing_entity_id: Union[Unset, int] = UNSET
    financial_year_ending: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        pay_schedule_id = self.pay_schedule_id

        employing_entity_id = self.employing_entity_id

        financial_year_ending = self.financial_year_ending

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if pay_schedule_id is not UNSET:
            field_dict["payScheduleId"] = pay_schedule_id
        if employing_entity_id is not UNSET:
            field_dict["employingEntityId"] = employing_entity_id
        if financial_year_ending is not UNSET:
            field_dict["financialYearEnding"] = financial_year_ending

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        pay_schedule_id = d.pop("payScheduleId", UNSET)

        employing_entity_id = d.pop("employingEntityId", UNSET)

        financial_year_ending = d.pop("financialYearEnding", UNSET)

        ordinary_time_earnings_report_request_model = cls(
            pay_schedule_id=pay_schedule_id,
            employing_entity_id=employing_entity_id,
            financial_year_ending=financial_year_ending,
        )

        ordinary_time_earnings_report_request_model.additional_properties = d
        return ordinary_time_earnings_report_request_model

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
