from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.basic_employment_agreement_model_au_employment_type_enum import (
    BasicEmploymentAgreementModelAuEmploymentTypeEnum,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="BasicEmploymentAgreementModel")


@_attrs_define
class BasicEmploymentAgreementModel:
    """
    Attributes:
        id (Union[Unset, int]):
        classification (Union[Unset, str]):
        employment_type (Union[Unset, BasicEmploymentAgreementModelAuEmploymentTypeEnum]):
        name (Union[Unset, str]):
        award_name (Union[Unset, str]):
        rank (Union[Unset, int]):
        external_id (Union[Unset, str]):
        award_id (Union[Unset, int]):
        disable_auto_progression (Union[Unset, bool]):
    """

    id: Union[Unset, int] = UNSET
    classification: Union[Unset, str] = UNSET
    employment_type: Union[Unset, BasicEmploymentAgreementModelAuEmploymentTypeEnum] = UNSET
    name: Union[Unset, str] = UNSET
    award_name: Union[Unset, str] = UNSET
    rank: Union[Unset, int] = UNSET
    external_id: Union[Unset, str] = UNSET
    award_id: Union[Unset, int] = UNSET
    disable_auto_progression: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        classification = self.classification

        employment_type: Union[Unset, str] = UNSET
        if not isinstance(self.employment_type, Unset):
            employment_type = self.employment_type.value

        name = self.name

        award_name = self.award_name

        rank = self.rank

        external_id = self.external_id

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
        if name is not UNSET:
            field_dict["name"] = name
        if award_name is not UNSET:
            field_dict["awardName"] = award_name
        if rank is not UNSET:
            field_dict["rank"] = rank
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if award_id is not UNSET:
            field_dict["awardId"] = award_id
        if disable_auto_progression is not UNSET:
            field_dict["disableAutoProgression"] = disable_auto_progression

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        classification = d.pop("classification", UNSET)

        _employment_type = d.pop("employmentType", UNSET)
        employment_type: Union[Unset, BasicEmploymentAgreementModelAuEmploymentTypeEnum]
        if isinstance(_employment_type, Unset):
            employment_type = UNSET
        else:
            employment_type = BasicEmploymentAgreementModelAuEmploymentTypeEnum(_employment_type)

        name = d.pop("name", UNSET)

        award_name = d.pop("awardName", UNSET)

        rank = d.pop("rank", UNSET)

        external_id = d.pop("externalId", UNSET)

        award_id = d.pop("awardId", UNSET)

        disable_auto_progression = d.pop("disableAutoProgression", UNSET)

        basic_employment_agreement_model = cls(
            id=id,
            classification=classification,
            employment_type=employment_type,
            name=name,
            award_name=award_name,
            rank=rank,
            external_id=external_id,
            award_id=award_id,
            disable_auto_progression=disable_auto_progression,
        )

        basic_employment_agreement_model.additional_properties = d
        return basic_employment_agreement_model

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
