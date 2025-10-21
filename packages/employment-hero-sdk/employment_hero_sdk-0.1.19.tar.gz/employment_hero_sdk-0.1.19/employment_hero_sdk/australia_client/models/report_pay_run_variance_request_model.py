import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.report_pay_run_variance_request_model_pay_run_comparison_type import (
    ReportPayRunVarianceRequestModelPayRunComparisonType,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="ReportPayRunVarianceRequestModel")


@_attrs_define
class ReportPayRunVarianceRequestModel:
    """
    Attributes:
        pay_run_id_1 (Union[Unset, int]):
        pay_run_id_2 (Union[Unset, int]):
        pay_period_from_1 (Union[Unset, datetime.datetime]):
        pay_period_to_1 (Union[Unset, datetime.datetime]):
        pay_period_from_2 (Union[Unset, datetime.datetime]):
        pay_period_to_2 (Union[Unset, datetime.datetime]):
        comparison_type (Union[Unset, ReportPayRunVarianceRequestModelPayRunComparisonType]):
        highlight_variance_percentage (Union[Unset, float]):
        only_show_variances (Union[Unset, bool]):
    """

    pay_run_id_1: Union[Unset, int] = UNSET
    pay_run_id_2: Union[Unset, int] = UNSET
    pay_period_from_1: Union[Unset, datetime.datetime] = UNSET
    pay_period_to_1: Union[Unset, datetime.datetime] = UNSET
    pay_period_from_2: Union[Unset, datetime.datetime] = UNSET
    pay_period_to_2: Union[Unset, datetime.datetime] = UNSET
    comparison_type: Union[Unset, ReportPayRunVarianceRequestModelPayRunComparisonType] = UNSET
    highlight_variance_percentage: Union[Unset, float] = UNSET
    only_show_variances: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        pay_run_id_1 = self.pay_run_id_1

        pay_run_id_2 = self.pay_run_id_2

        pay_period_from_1: Union[Unset, str] = UNSET
        if not isinstance(self.pay_period_from_1, Unset):
            pay_period_from_1 = self.pay_period_from_1.isoformat()

        pay_period_to_1: Union[Unset, str] = UNSET
        if not isinstance(self.pay_period_to_1, Unset):
            pay_period_to_1 = self.pay_period_to_1.isoformat()

        pay_period_from_2: Union[Unset, str] = UNSET
        if not isinstance(self.pay_period_from_2, Unset):
            pay_period_from_2 = self.pay_period_from_2.isoformat()

        pay_period_to_2: Union[Unset, str] = UNSET
        if not isinstance(self.pay_period_to_2, Unset):
            pay_period_to_2 = self.pay_period_to_2.isoformat()

        comparison_type: Union[Unset, str] = UNSET
        if not isinstance(self.comparison_type, Unset):
            comparison_type = self.comparison_type.value

        highlight_variance_percentage = self.highlight_variance_percentage

        only_show_variances = self.only_show_variances

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if pay_run_id_1 is not UNSET:
            field_dict["payRunId1"] = pay_run_id_1
        if pay_run_id_2 is not UNSET:
            field_dict["payRunId2"] = pay_run_id_2
        if pay_period_from_1 is not UNSET:
            field_dict["payPeriodFrom1"] = pay_period_from_1
        if pay_period_to_1 is not UNSET:
            field_dict["payPeriodTo1"] = pay_period_to_1
        if pay_period_from_2 is not UNSET:
            field_dict["payPeriodFrom2"] = pay_period_from_2
        if pay_period_to_2 is not UNSET:
            field_dict["payPeriodTo2"] = pay_period_to_2
        if comparison_type is not UNSET:
            field_dict["comparisonType"] = comparison_type
        if highlight_variance_percentage is not UNSET:
            field_dict["highlightVariancePercentage"] = highlight_variance_percentage
        if only_show_variances is not UNSET:
            field_dict["onlyShowVariances"] = only_show_variances

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        pay_run_id_1 = d.pop("payRunId1", UNSET)

        pay_run_id_2 = d.pop("payRunId2", UNSET)

        _pay_period_from_1 = d.pop("payPeriodFrom1", UNSET)
        pay_period_from_1: Union[Unset, datetime.datetime]
        if isinstance(_pay_period_from_1, Unset):
            pay_period_from_1 = UNSET
        else:
            pay_period_from_1 = isoparse(_pay_period_from_1)

        _pay_period_to_1 = d.pop("payPeriodTo1", UNSET)
        pay_period_to_1: Union[Unset, datetime.datetime]
        if isinstance(_pay_period_to_1, Unset):
            pay_period_to_1 = UNSET
        else:
            pay_period_to_1 = isoparse(_pay_period_to_1)

        _pay_period_from_2 = d.pop("payPeriodFrom2", UNSET)
        pay_period_from_2: Union[Unset, datetime.datetime]
        if isinstance(_pay_period_from_2, Unset):
            pay_period_from_2 = UNSET
        else:
            pay_period_from_2 = isoparse(_pay_period_from_2)

        _pay_period_to_2 = d.pop("payPeriodTo2", UNSET)
        pay_period_to_2: Union[Unset, datetime.datetime]
        if isinstance(_pay_period_to_2, Unset):
            pay_period_to_2 = UNSET
        else:
            pay_period_to_2 = isoparse(_pay_period_to_2)

        _comparison_type = d.pop("comparisonType", UNSET)
        comparison_type: Union[Unset, ReportPayRunVarianceRequestModelPayRunComparisonType]
        if isinstance(_comparison_type, Unset):
            comparison_type = UNSET
        else:
            comparison_type = ReportPayRunVarianceRequestModelPayRunComparisonType(_comparison_type)

        highlight_variance_percentage = d.pop("highlightVariancePercentage", UNSET)

        only_show_variances = d.pop("onlyShowVariances", UNSET)

        report_pay_run_variance_request_model = cls(
            pay_run_id_1=pay_run_id_1,
            pay_run_id_2=pay_run_id_2,
            pay_period_from_1=pay_period_from_1,
            pay_period_to_1=pay_period_to_1,
            pay_period_from_2=pay_period_from_2,
            pay_period_to_2=pay_period_to_2,
            comparison_type=comparison_type,
            highlight_variance_percentage=highlight_variance_percentage,
            only_show_variances=only_show_variances,
        )

        report_pay_run_variance_request_model.additional_properties = d
        return report_pay_run_variance_request_model

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
