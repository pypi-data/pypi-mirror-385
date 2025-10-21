from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SingleSignOnRequestAdditionalDataModel")


@_attrs_define
class SingleSignOnRequestAdditionalDataModel:
    """
    Attributes:
        organisation_id (Union[Unset, str]):
        member_id (Union[Unset, str]):
    """

    organisation_id: Union[Unset, str] = UNSET
    member_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        organisation_id = self.organisation_id

        member_id = self.member_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if organisation_id is not UNSET:
            field_dict["organisationId"] = organisation_id
        if member_id is not UNSET:
            field_dict["memberId"] = member_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        organisation_id = d.pop("organisationId", UNSET)

        member_id = d.pop("memberId", UNSET)

        single_sign_on_request_additional_data_model = cls(
            organisation_id=organisation_id,
            member_id=member_id,
        )

        single_sign_on_request_additional_data_model.additional_properties = d
        return single_sign_on_request_additional_data_model

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
