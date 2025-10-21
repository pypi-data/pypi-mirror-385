from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.au_employing_entity_model_nullable_fbt_exempt_organisation_type_enum import (
    AuEmployingEntityModelNullableFbtExemptOrganisationTypeEnum,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="AuEmployingEntityModel")


@_attrs_define
class AuEmployingEntityModel:
    """
    Attributes:
        abn (Union[Unset, str]):
        suburb (Union[Unset, str]):
        state (Union[Unset, str]):
        branch_code (Union[Unset, str]):
        is_exempt_from_fringe_benefits_tax (Union[Unset, bool]):
        has_separate_entertainment_fringe_benefits_cap (Union[Unset, bool]):
        fbt_exempt_organisation_type (Union[Unset, AuEmployingEntityModelNullableFbtExemptOrganisationTypeEnum]):
        is_foreign_entity (Union[Unset, bool]):
        foreign_entity_country (Union[Unset, str]):
        id (Union[Unset, int]):
        name (Union[Unset, str]):
        contact_name (Union[Unset, str]):
        signatory_name (Union[Unset, str]):
        contact_email_address (Union[Unset, str]):
        contact_phone_number (Union[Unset, str]):
        contact_fax_number (Union[Unset, str]):
        address_line_1 (Union[Unset, str]):
        address_line_2 (Union[Unset, str]):
        postcode (Union[Unset, str]):
        external_reference_id (Union[Unset, str]):
        pay_slip_from_email_address (Union[Unset, str]):
    """

    abn: Union[Unset, str] = UNSET
    suburb: Union[Unset, str] = UNSET
    state: Union[Unset, str] = UNSET
    branch_code: Union[Unset, str] = UNSET
    is_exempt_from_fringe_benefits_tax: Union[Unset, bool] = UNSET
    has_separate_entertainment_fringe_benefits_cap: Union[Unset, bool] = UNSET
    fbt_exempt_organisation_type: Union[Unset, AuEmployingEntityModelNullableFbtExemptOrganisationTypeEnum] = UNSET
    is_foreign_entity: Union[Unset, bool] = UNSET
    foreign_entity_country: Union[Unset, str] = UNSET
    id: Union[Unset, int] = UNSET
    name: Union[Unset, str] = UNSET
    contact_name: Union[Unset, str] = UNSET
    signatory_name: Union[Unset, str] = UNSET
    contact_email_address: Union[Unset, str] = UNSET
    contact_phone_number: Union[Unset, str] = UNSET
    contact_fax_number: Union[Unset, str] = UNSET
    address_line_1: Union[Unset, str] = UNSET
    address_line_2: Union[Unset, str] = UNSET
    postcode: Union[Unset, str] = UNSET
    external_reference_id: Union[Unset, str] = UNSET
    pay_slip_from_email_address: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        abn = self.abn

        suburb = self.suburb

        state = self.state

        branch_code = self.branch_code

        is_exempt_from_fringe_benefits_tax = self.is_exempt_from_fringe_benefits_tax

        has_separate_entertainment_fringe_benefits_cap = self.has_separate_entertainment_fringe_benefits_cap

        fbt_exempt_organisation_type: Union[Unset, str] = UNSET
        if not isinstance(self.fbt_exempt_organisation_type, Unset):
            fbt_exempt_organisation_type = self.fbt_exempt_organisation_type.value

        is_foreign_entity = self.is_foreign_entity

        foreign_entity_country = self.foreign_entity_country

        id = self.id

        name = self.name

        contact_name = self.contact_name

        signatory_name = self.signatory_name

        contact_email_address = self.contact_email_address

        contact_phone_number = self.contact_phone_number

        contact_fax_number = self.contact_fax_number

        address_line_1 = self.address_line_1

        address_line_2 = self.address_line_2

        postcode = self.postcode

        external_reference_id = self.external_reference_id

        pay_slip_from_email_address = self.pay_slip_from_email_address

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if abn is not UNSET:
            field_dict["abn"] = abn
        if suburb is not UNSET:
            field_dict["suburb"] = suburb
        if state is not UNSET:
            field_dict["state"] = state
        if branch_code is not UNSET:
            field_dict["branchCode"] = branch_code
        if is_exempt_from_fringe_benefits_tax is not UNSET:
            field_dict["isExemptFromFringeBenefitsTax"] = is_exempt_from_fringe_benefits_tax
        if has_separate_entertainment_fringe_benefits_cap is not UNSET:
            field_dict["hasSeparateEntertainmentFringeBenefitsCap"] = has_separate_entertainment_fringe_benefits_cap
        if fbt_exempt_organisation_type is not UNSET:
            field_dict["fbtExemptOrganisationType"] = fbt_exempt_organisation_type
        if is_foreign_entity is not UNSET:
            field_dict["isForeignEntity"] = is_foreign_entity
        if foreign_entity_country is not UNSET:
            field_dict["foreignEntityCountry"] = foreign_entity_country
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if contact_name is not UNSET:
            field_dict["contactName"] = contact_name
        if signatory_name is not UNSET:
            field_dict["signatoryName"] = signatory_name
        if contact_email_address is not UNSET:
            field_dict["contactEmailAddress"] = contact_email_address
        if contact_phone_number is not UNSET:
            field_dict["contactPhoneNumber"] = contact_phone_number
        if contact_fax_number is not UNSET:
            field_dict["contactFaxNumber"] = contact_fax_number
        if address_line_1 is not UNSET:
            field_dict["addressLine1"] = address_line_1
        if address_line_2 is not UNSET:
            field_dict["addressLine2"] = address_line_2
        if postcode is not UNSET:
            field_dict["postcode"] = postcode
        if external_reference_id is not UNSET:
            field_dict["externalReferenceId"] = external_reference_id
        if pay_slip_from_email_address is not UNSET:
            field_dict["paySlipFromEmailAddress"] = pay_slip_from_email_address

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        abn = d.pop("abn", UNSET)

        suburb = d.pop("suburb", UNSET)

        state = d.pop("state", UNSET)

        branch_code = d.pop("branchCode", UNSET)

        is_exempt_from_fringe_benefits_tax = d.pop("isExemptFromFringeBenefitsTax", UNSET)

        has_separate_entertainment_fringe_benefits_cap = d.pop("hasSeparateEntertainmentFringeBenefitsCap", UNSET)

        _fbt_exempt_organisation_type = d.pop("fbtExemptOrganisationType", UNSET)
        fbt_exempt_organisation_type: Union[Unset, AuEmployingEntityModelNullableFbtExemptOrganisationTypeEnum]
        if isinstance(_fbt_exempt_organisation_type, Unset):
            fbt_exempt_organisation_type = UNSET
        else:
            fbt_exempt_organisation_type = AuEmployingEntityModelNullableFbtExemptOrganisationTypeEnum(
                _fbt_exempt_organisation_type
            )

        is_foreign_entity = d.pop("isForeignEntity", UNSET)

        foreign_entity_country = d.pop("foreignEntityCountry", UNSET)

        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        contact_name = d.pop("contactName", UNSET)

        signatory_name = d.pop("signatoryName", UNSET)

        contact_email_address = d.pop("contactEmailAddress", UNSET)

        contact_phone_number = d.pop("contactPhoneNumber", UNSET)

        contact_fax_number = d.pop("contactFaxNumber", UNSET)

        address_line_1 = d.pop("addressLine1", UNSET)

        address_line_2 = d.pop("addressLine2", UNSET)

        postcode = d.pop("postcode", UNSET)

        external_reference_id = d.pop("externalReferenceId", UNSET)

        pay_slip_from_email_address = d.pop("paySlipFromEmailAddress", UNSET)

        au_employing_entity_model = cls(
            abn=abn,
            suburb=suburb,
            state=state,
            branch_code=branch_code,
            is_exempt_from_fringe_benefits_tax=is_exempt_from_fringe_benefits_tax,
            has_separate_entertainment_fringe_benefits_cap=has_separate_entertainment_fringe_benefits_cap,
            fbt_exempt_organisation_type=fbt_exempt_organisation_type,
            is_foreign_entity=is_foreign_entity,
            foreign_entity_country=foreign_entity_country,
            id=id,
            name=name,
            contact_name=contact_name,
            signatory_name=signatory_name,
            contact_email_address=contact_email_address,
            contact_phone_number=contact_phone_number,
            contact_fax_number=contact_fax_number,
            address_line_1=address_line_1,
            address_line_2=address_line_2,
            postcode=postcode,
            external_reference_id=external_reference_id,
            pay_slip_from_email_address=pay_slip_from_email_address,
        )

        au_employing_entity_model.additional_properties = d
        return au_employing_entity_model

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
