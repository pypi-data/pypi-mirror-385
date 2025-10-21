from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.rule_evaluation_result_rule_match_result import RuleEvaluationResultRuleMatchResult
from ..types import UNSET, Unset

T = TypeVar("T", bound="RuleEvaluationResult")


@_attrs_define
class RuleEvaluationResult:
    """
    Attributes:
        rule_name (Union[Unset, str]):
        match_result (Union[Unset, RuleEvaluationResultRuleMatchResult]):
    """

    rule_name: Union[Unset, str] = UNSET
    match_result: Union[Unset, RuleEvaluationResultRuleMatchResult] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        rule_name = self.rule_name

        match_result: Union[Unset, str] = UNSET
        if not isinstance(self.match_result, Unset):
            match_result = self.match_result.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if rule_name is not UNSET:
            field_dict["ruleName"] = rule_name
        if match_result is not UNSET:
            field_dict["matchResult"] = match_result

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        rule_name = d.pop("ruleName", UNSET)

        _match_result = d.pop("matchResult", UNSET)
        match_result: Union[Unset, RuleEvaluationResultRuleMatchResult]
        if isinstance(_match_result, Unset):
            match_result = UNSET
        else:
            match_result = RuleEvaluationResultRuleMatchResult(_match_result)

        rule_evaluation_result = cls(
            rule_name=rule_name,
            match_result=match_result,
        )

        rule_evaluation_result.additional_properties = d
        return rule_evaluation_result

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
