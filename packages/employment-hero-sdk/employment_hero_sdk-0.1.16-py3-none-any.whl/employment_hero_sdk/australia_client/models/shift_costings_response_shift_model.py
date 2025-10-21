import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.rule_evaluation_result import RuleEvaluationResult
    from ..models.shift_costing_breakdown_model import ShiftCostingBreakdownModel


T = TypeVar("T", bound="ShiftCostingsResponseShiftModel")


@_attrs_define
class ShiftCostingsResponseShiftModel:
    """
    Attributes:
        external_id (Union[Unset, str]):
        start_time (Union[Unset, datetime.datetime]):
        end_time (Union[Unset, datetime.datetime]):
        cost (Union[Unset, float]):
        evaluation_results (Union[Unset, List['RuleEvaluationResult']]):
        consolidated_shifts (Union[Unset, List[str]]):
        cost_breakdown (Union[Unset, List['ShiftCostingBreakdownModel']]):
    """

    external_id: Union[Unset, str] = UNSET
    start_time: Union[Unset, datetime.datetime] = UNSET
    end_time: Union[Unset, datetime.datetime] = UNSET
    cost: Union[Unset, float] = UNSET
    evaluation_results: Union[Unset, List["RuleEvaluationResult"]] = UNSET
    consolidated_shifts: Union[Unset, List[str]] = UNSET
    cost_breakdown: Union[Unset, List["ShiftCostingBreakdownModel"]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        external_id = self.external_id

        start_time: Union[Unset, str] = UNSET
        if not isinstance(self.start_time, Unset):
            start_time = self.start_time.isoformat()

        end_time: Union[Unset, str] = UNSET
        if not isinstance(self.end_time, Unset):
            end_time = self.end_time.isoformat()

        cost = self.cost

        evaluation_results: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.evaluation_results, Unset):
            evaluation_results = []
            for evaluation_results_item_data in self.evaluation_results:
                evaluation_results_item = evaluation_results_item_data.to_dict()
                evaluation_results.append(evaluation_results_item)

        consolidated_shifts: Union[Unset, List[str]] = UNSET
        if not isinstance(self.consolidated_shifts, Unset):
            consolidated_shifts = self.consolidated_shifts

        cost_breakdown: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.cost_breakdown, Unset):
            cost_breakdown = []
            for cost_breakdown_item_data in self.cost_breakdown:
                cost_breakdown_item = cost_breakdown_item_data.to_dict()
                cost_breakdown.append(cost_breakdown_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if start_time is not UNSET:
            field_dict["startTime"] = start_time
        if end_time is not UNSET:
            field_dict["endTime"] = end_time
        if cost is not UNSET:
            field_dict["cost"] = cost
        if evaluation_results is not UNSET:
            field_dict["evaluationResults"] = evaluation_results
        if consolidated_shifts is not UNSET:
            field_dict["consolidatedShifts"] = consolidated_shifts
        if cost_breakdown is not UNSET:
            field_dict["costBreakdown"] = cost_breakdown

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.rule_evaluation_result import RuleEvaluationResult
        from ..models.shift_costing_breakdown_model import ShiftCostingBreakdownModel

        d = src_dict.copy()
        external_id = d.pop("externalId", UNSET)

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

        cost = d.pop("cost", UNSET)

        evaluation_results = []
        _evaluation_results = d.pop("evaluationResults", UNSET)
        for evaluation_results_item_data in _evaluation_results or []:
            evaluation_results_item = RuleEvaluationResult.from_dict(evaluation_results_item_data)

            evaluation_results.append(evaluation_results_item)

        consolidated_shifts = cast(List[str], d.pop("consolidatedShifts", UNSET))

        cost_breakdown = []
        _cost_breakdown = d.pop("costBreakdown", UNSET)
        for cost_breakdown_item_data in _cost_breakdown or []:
            cost_breakdown_item = ShiftCostingBreakdownModel.from_dict(cost_breakdown_item_data)

            cost_breakdown.append(cost_breakdown_item)

        shift_costings_response_shift_model = cls(
            external_id=external_id,
            start_time=start_time,
            end_time=end_time,
            cost=cost,
            evaluation_results=evaluation_results,
            consolidated_shifts=consolidated_shifts,
            cost_breakdown=cost_breakdown,
        )

        shift_costings_response_shift_model.additional_properties = d
        return shift_costings_response_shift_model

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
