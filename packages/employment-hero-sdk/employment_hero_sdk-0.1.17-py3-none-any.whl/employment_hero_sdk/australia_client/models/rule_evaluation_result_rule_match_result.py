from enum import Enum


class RuleEvaluationResultRuleMatchResult(str, Enum):
    DISABLEDFOREMPLOYEE = "DisabledForEmployee"
    DISABLEDFORRULESET = "DisabledForRuleSet"
    EXCLUDEDCUSTOMRULE = "ExcludedCustomRule"
    MATCH = "Match"
    NOMATCH = "NoMatch"

    def __str__(self) -> str:
        return str(self.value)
