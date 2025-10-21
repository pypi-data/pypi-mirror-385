from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AuUserAccountPartnerMetadata")


@_attrs_define
class AuUserAccountPartnerMetadata:
    """
    Attributes:
        id (Union[Unset, int]):
        email (Union[Unset, str]):
        partner_ids (Union[Unset, List[int]]):
    """

    id: Union[Unset, int] = UNSET
    email: Union[Unset, str] = UNSET
    partner_ids: Union[Unset, List[int]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        email = self.email

        partner_ids: Union[Unset, List[int]] = UNSET
        if not isinstance(self.partner_ids, Unset):
            partner_ids = self.partner_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if email is not UNSET:
            field_dict["email"] = email
        if partner_ids is not UNSET:
            field_dict["partnerIds"] = partner_ids

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        email = d.pop("email", UNSET)

        partner_ids = cast(List[int], d.pop("partnerIds", UNSET))

        au_user_account_partner_metadata = cls(
            id=id,
            email=email,
            partner_ids=partner_ids,
        )

        au_user_account_partner_metadata.additional_properties = d
        return au_user_account_partner_metadata

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
