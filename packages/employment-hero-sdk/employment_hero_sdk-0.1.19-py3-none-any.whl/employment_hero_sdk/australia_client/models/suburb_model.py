from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SuburbModel")


@_attrs_define
class SuburbModel:
    """
    Attributes:
        id (Union[Unset, int]):
        name (Union[Unset, str]):
        state (Union[Unset, str]):
        postcode (Union[Unset, str]):
        country (Union[Unset, str]):
        country_id (Union[Unset, str]):
    """

    id: Union[Unset, int] = UNSET
    name: Union[Unset, str] = UNSET
    state: Union[Unset, str] = UNSET
    postcode: Union[Unset, str] = UNSET
    country: Union[Unset, str] = UNSET
    country_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        name = self.name

        state = self.state

        postcode = self.postcode

        country = self.country

        country_id = self.country_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if state is not UNSET:
            field_dict["state"] = state
        if postcode is not UNSET:
            field_dict["postcode"] = postcode
        if country is not UNSET:
            field_dict["country"] = country
        if country_id is not UNSET:
            field_dict["countryId"] = country_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        state = d.pop("state", UNSET)

        postcode = d.pop("postcode", UNSET)

        country = d.pop("country", UNSET)

        country_id = d.pop("countryId", UNSET)

        suburb_model = cls(
            id=id,
            name=name,
            state=state,
            postcode=postcode,
            country=country,
            country_id=country_id,
        )

        suburb_model.additional_properties = d
        return suburb_model

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
