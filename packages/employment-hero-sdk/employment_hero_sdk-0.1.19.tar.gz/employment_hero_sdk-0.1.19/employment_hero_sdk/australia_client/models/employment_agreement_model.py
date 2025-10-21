from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.employment_agreement_model_employment_type_enum import EmploymentAgreementModelEmploymentTypeEnum
from ..models.employment_agreement_model_external_service import EmploymentAgreementModelExternalService
from ..models.employment_agreement_model_pay_rate_template_type_enum import (
    EmploymentAgreementModelPayRateTemplateTypeEnum,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.employment_agreement_pay_rate_template_model import EmploymentAgreementPayRateTemplateModel
    from ..models.leave_allowance_template_model import LeaveAllowanceTemplateModel
    from ..models.pay_condition_rule_set_model import PayConditionRuleSetModel


T = TypeVar("T", bound="EmploymentAgreementModel")


@_attrs_define
class EmploymentAgreementModel:
    """
    Attributes:
        id (Union[Unset, int]):
        classification (Union[Unset, str]):
        employment_type (Union[Unset, EmploymentAgreementModelEmploymentTypeEnum]):
        pay_rate_template_type (Union[Unset, EmploymentAgreementModelPayRateTemplateTypeEnum]):
        pay_condition_rule_set_id (Union[Unset, int]):
        pay_condition_rule_set (Union[Unset, PayConditionRuleSetModel]):
        leave_allowance_templates (Union[Unset, List['LeaveAllowanceTemplateModel']]):
        leave_allowance_template_ids (Union[Unset, List[int]]):
        age_pay_rate_templates (Union[Unset, List['EmploymentAgreementPayRateTemplateModel']]):
        external_id (Union[Unset, str]):
        source (Union[Unset, EmploymentAgreementModelExternalService]):
        rank (Union[Unset, int]):
        award_id (Union[Unset, int]):
        disable_auto_progression (Union[Unset, bool]):
    """

    id: Union[Unset, int] = UNSET
    classification: Union[Unset, str] = UNSET
    employment_type: Union[Unset, EmploymentAgreementModelEmploymentTypeEnum] = UNSET
    pay_rate_template_type: Union[Unset, EmploymentAgreementModelPayRateTemplateTypeEnum] = UNSET
    pay_condition_rule_set_id: Union[Unset, int] = UNSET
    pay_condition_rule_set: Union[Unset, "PayConditionRuleSetModel"] = UNSET
    leave_allowance_templates: Union[Unset, List["LeaveAllowanceTemplateModel"]] = UNSET
    leave_allowance_template_ids: Union[Unset, List[int]] = UNSET
    age_pay_rate_templates: Union[Unset, List["EmploymentAgreementPayRateTemplateModel"]] = UNSET
    external_id: Union[Unset, str] = UNSET
    source: Union[Unset, EmploymentAgreementModelExternalService] = UNSET
    rank: Union[Unset, int] = UNSET
    award_id: Union[Unset, int] = UNSET
    disable_auto_progression: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        classification = self.classification

        employment_type: Union[Unset, str] = UNSET
        if not isinstance(self.employment_type, Unset):
            employment_type = self.employment_type.value

        pay_rate_template_type: Union[Unset, str] = UNSET
        if not isinstance(self.pay_rate_template_type, Unset):
            pay_rate_template_type = self.pay_rate_template_type.value

        pay_condition_rule_set_id = self.pay_condition_rule_set_id

        pay_condition_rule_set: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.pay_condition_rule_set, Unset):
            pay_condition_rule_set = self.pay_condition_rule_set.to_dict()

        leave_allowance_templates: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.leave_allowance_templates, Unset):
            leave_allowance_templates = []
            for leave_allowance_templates_item_data in self.leave_allowance_templates:
                leave_allowance_templates_item = leave_allowance_templates_item_data.to_dict()
                leave_allowance_templates.append(leave_allowance_templates_item)

        leave_allowance_template_ids: Union[Unset, List[int]] = UNSET
        if not isinstance(self.leave_allowance_template_ids, Unset):
            leave_allowance_template_ids = self.leave_allowance_template_ids

        age_pay_rate_templates: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.age_pay_rate_templates, Unset):
            age_pay_rate_templates = []
            for age_pay_rate_templates_item_data in self.age_pay_rate_templates:
                age_pay_rate_templates_item = age_pay_rate_templates_item_data.to_dict()
                age_pay_rate_templates.append(age_pay_rate_templates_item)

        external_id = self.external_id

        source: Union[Unset, str] = UNSET
        if not isinstance(self.source, Unset):
            source = self.source.value

        rank = self.rank

        award_id = self.award_id

        disable_auto_progression = self.disable_auto_progression

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if classification is not UNSET:
            field_dict["classification"] = classification
        if employment_type is not UNSET:
            field_dict["employmentType"] = employment_type
        if pay_rate_template_type is not UNSET:
            field_dict["payRateTemplateType"] = pay_rate_template_type
        if pay_condition_rule_set_id is not UNSET:
            field_dict["payConditionRuleSetId"] = pay_condition_rule_set_id
        if pay_condition_rule_set is not UNSET:
            field_dict["payConditionRuleSet"] = pay_condition_rule_set
        if leave_allowance_templates is not UNSET:
            field_dict["leaveAllowanceTemplates"] = leave_allowance_templates
        if leave_allowance_template_ids is not UNSET:
            field_dict["leaveAllowanceTemplateIds"] = leave_allowance_template_ids
        if age_pay_rate_templates is not UNSET:
            field_dict["agePayRateTemplates"] = age_pay_rate_templates
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if source is not UNSET:
            field_dict["source"] = source
        if rank is not UNSET:
            field_dict["rank"] = rank
        if award_id is not UNSET:
            field_dict["awardId"] = award_id
        if disable_auto_progression is not UNSET:
            field_dict["disableAutoProgression"] = disable_auto_progression

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.employment_agreement_pay_rate_template_model import EmploymentAgreementPayRateTemplateModel
        from ..models.leave_allowance_template_model import LeaveAllowanceTemplateModel
        from ..models.pay_condition_rule_set_model import PayConditionRuleSetModel

        d = src_dict.copy()
        id = d.pop("id", UNSET)

        classification = d.pop("classification", UNSET)

        _employment_type = d.pop("employmentType", UNSET)
        employment_type: Union[Unset, EmploymentAgreementModelEmploymentTypeEnum]
        if isinstance(_employment_type, Unset):
            employment_type = UNSET
        else:
            employment_type = EmploymentAgreementModelEmploymentTypeEnum(_employment_type)

        _pay_rate_template_type = d.pop("payRateTemplateType", UNSET)
        pay_rate_template_type: Union[Unset, EmploymentAgreementModelPayRateTemplateTypeEnum]
        if isinstance(_pay_rate_template_type, Unset):
            pay_rate_template_type = UNSET
        else:
            pay_rate_template_type = EmploymentAgreementModelPayRateTemplateTypeEnum(_pay_rate_template_type)

        pay_condition_rule_set_id = d.pop("payConditionRuleSetId", UNSET)

        _pay_condition_rule_set = d.pop("payConditionRuleSet", UNSET)
        pay_condition_rule_set: Union[Unset, PayConditionRuleSetModel]
        if isinstance(_pay_condition_rule_set, Unset):
            pay_condition_rule_set = UNSET
        else:
            pay_condition_rule_set = PayConditionRuleSetModel.from_dict(_pay_condition_rule_set)

        leave_allowance_templates = []
        _leave_allowance_templates = d.pop("leaveAllowanceTemplates", UNSET)
        for leave_allowance_templates_item_data in _leave_allowance_templates or []:
            leave_allowance_templates_item = LeaveAllowanceTemplateModel.from_dict(leave_allowance_templates_item_data)

            leave_allowance_templates.append(leave_allowance_templates_item)

        leave_allowance_template_ids = cast(List[int], d.pop("leaveAllowanceTemplateIds", UNSET))

        age_pay_rate_templates = []
        _age_pay_rate_templates = d.pop("agePayRateTemplates", UNSET)
        for age_pay_rate_templates_item_data in _age_pay_rate_templates or []:
            age_pay_rate_templates_item = EmploymentAgreementPayRateTemplateModel.from_dict(
                age_pay_rate_templates_item_data
            )

            age_pay_rate_templates.append(age_pay_rate_templates_item)

        external_id = d.pop("externalId", UNSET)

        _source = d.pop("source", UNSET)
        source: Union[Unset, EmploymentAgreementModelExternalService]
        if isinstance(_source, Unset):
            source = UNSET
        else:
            source = EmploymentAgreementModelExternalService(_source)

        rank = d.pop("rank", UNSET)

        award_id = d.pop("awardId", UNSET)

        disable_auto_progression = d.pop("disableAutoProgression", UNSET)

        employment_agreement_model = cls(
            id=id,
            classification=classification,
            employment_type=employment_type,
            pay_rate_template_type=pay_rate_template_type,
            pay_condition_rule_set_id=pay_condition_rule_set_id,
            pay_condition_rule_set=pay_condition_rule_set,
            leave_allowance_templates=leave_allowance_templates,
            leave_allowance_template_ids=leave_allowance_template_ids,
            age_pay_rate_templates=age_pay_rate_templates,
            external_id=external_id,
            source=source,
            rank=rank,
            award_id=award_id,
            disable_auto_progression=disable_auto_progression,
        )

        employment_agreement_model.additional_properties = d
        return employment_agreement_model

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
