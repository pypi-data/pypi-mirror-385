from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AuAddressModel")


@_attrs_define
class AuAddressModel:
    """
    Attributes:
        street_address (Union[Unset, str]):
        address_line_2 (Union[Unset, str]):
        postcode (Union[Unset, str]):
        country (Union[Unset, str]):
        country_id (Union[Unset, str]):
        suburb_id (Union[Unset, int]):
        suburb (Union[Unset, str]):
        state (Union[Unset, str]):
        is_manual_address (Union[Unset, bool]):
        is_out_of_region (Union[Unset, bool]):
    """

    street_address: Union[Unset, str] = UNSET
    address_line_2: Union[Unset, str] = UNSET
    postcode: Union[Unset, str] = UNSET
    country: Union[Unset, str] = UNSET
    country_id: Union[Unset, str] = UNSET
    suburb_id: Union[Unset, int] = UNSET
    suburb: Union[Unset, str] = UNSET
    state: Union[Unset, str] = UNSET
    is_manual_address: Union[Unset, bool] = UNSET
    is_out_of_region: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        street_address = self.street_address

        address_line_2 = self.address_line_2

        postcode = self.postcode

        country = self.country

        country_id = self.country_id

        suburb_id = self.suburb_id

        suburb = self.suburb

        state = self.state

        is_manual_address = self.is_manual_address

        is_out_of_region = self.is_out_of_region

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if street_address is not UNSET:
            field_dict["streetAddress"] = street_address
        if address_line_2 is not UNSET:
            field_dict["addressLine2"] = address_line_2
        if postcode is not UNSET:
            field_dict["postcode"] = postcode
        if country is not UNSET:
            field_dict["country"] = country
        if country_id is not UNSET:
            field_dict["countryId"] = country_id
        if suburb_id is not UNSET:
            field_dict["suburbId"] = suburb_id
        if suburb is not UNSET:
            field_dict["suburb"] = suburb
        if state is not UNSET:
            field_dict["state"] = state
        if is_manual_address is not UNSET:
            field_dict["isManualAddress"] = is_manual_address
        if is_out_of_region is not UNSET:
            field_dict["isOutOfRegion"] = is_out_of_region

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        street_address = d.pop("streetAddress", UNSET)

        address_line_2 = d.pop("addressLine2", UNSET)

        postcode = d.pop("postcode", UNSET)

        country = d.pop("country", UNSET)

        country_id = d.pop("countryId", UNSET)

        suburb_id = d.pop("suburbId", UNSET)

        suburb = d.pop("suburb", UNSET)

        state = d.pop("state", UNSET)

        is_manual_address = d.pop("isManualAddress", UNSET)

        is_out_of_region = d.pop("isOutOfRegion", UNSET)

        au_address_model = cls(
            street_address=street_address,
            address_line_2=address_line_2,
            postcode=postcode,
            country=country,
            country_id=country_id,
            suburb_id=suburb_id,
            suburb=suburb,
            state=state,
            is_manual_address=is_manual_address,
            is_out_of_region=is_out_of_region,
        )

        au_address_model.additional_properties = d
        return au_address_model

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
