from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.business_ato_supplier_model_ato_supplier_role import BusinessAtoSupplierModelAtoSupplierRole
from ..types import UNSET, Unset

T = TypeVar("T", bound="BusinessAtoSupplierModel")


@_attrs_define
class BusinessAtoSupplierModel:
    """
    Attributes:
        id (Union[Unset, int]):
        abn (Union[Unset, str]):
        name (Union[Unset, str]):
        address_line_1 (Union[Unset, str]):
        address_line_2 (Union[Unset, str]):
        suburb (Union[Unset, str]):
        state (Union[Unset, str]):
        post_code (Union[Unset, str]):
        contact_name (Union[Unset, str]):
        signatory_name (Union[Unset, str]):
        phone_number (Union[Unset, str]):
        fax_number (Union[Unset, str]):
        country (Union[Unset, str]):
        branch (Union[Unset, str]):
        role (Union[Unset, BusinessAtoSupplierModelAtoSupplierRole]):
        tax_agent_number (Union[Unset, str]):
        intermediary_abn (Union[Unset, str]):
        intermediary_contact_name (Union[Unset, str]):
        intermediary_contact_email (Union[Unset, str]):
        intermediary_contact_phone (Union[Unset, str]):
    """

    id: Union[Unset, int] = UNSET
    abn: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    address_line_1: Union[Unset, str] = UNSET
    address_line_2: Union[Unset, str] = UNSET
    suburb: Union[Unset, str] = UNSET
    state: Union[Unset, str] = UNSET
    post_code: Union[Unset, str] = UNSET
    contact_name: Union[Unset, str] = UNSET
    signatory_name: Union[Unset, str] = UNSET
    phone_number: Union[Unset, str] = UNSET
    fax_number: Union[Unset, str] = UNSET
    country: Union[Unset, str] = UNSET
    branch: Union[Unset, str] = UNSET
    role: Union[Unset, BusinessAtoSupplierModelAtoSupplierRole] = UNSET
    tax_agent_number: Union[Unset, str] = UNSET
    intermediary_abn: Union[Unset, str] = UNSET
    intermediary_contact_name: Union[Unset, str] = UNSET
    intermediary_contact_email: Union[Unset, str] = UNSET
    intermediary_contact_phone: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        abn = self.abn

        name = self.name

        address_line_1 = self.address_line_1

        address_line_2 = self.address_line_2

        suburb = self.suburb

        state = self.state

        post_code = self.post_code

        contact_name = self.contact_name

        signatory_name = self.signatory_name

        phone_number = self.phone_number

        fax_number = self.fax_number

        country = self.country

        branch = self.branch

        role: Union[Unset, str] = UNSET
        if not isinstance(self.role, Unset):
            role = self.role.value

        tax_agent_number = self.tax_agent_number

        intermediary_abn = self.intermediary_abn

        intermediary_contact_name = self.intermediary_contact_name

        intermediary_contact_email = self.intermediary_contact_email

        intermediary_contact_phone = self.intermediary_contact_phone

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if abn is not UNSET:
            field_dict["abn"] = abn
        if name is not UNSET:
            field_dict["name"] = name
        if address_line_1 is not UNSET:
            field_dict["addressLine1"] = address_line_1
        if address_line_2 is not UNSET:
            field_dict["addressLine2"] = address_line_2
        if suburb is not UNSET:
            field_dict["suburb"] = suburb
        if state is not UNSET:
            field_dict["state"] = state
        if post_code is not UNSET:
            field_dict["postCode"] = post_code
        if contact_name is not UNSET:
            field_dict["contactName"] = contact_name
        if signatory_name is not UNSET:
            field_dict["signatoryName"] = signatory_name
        if phone_number is not UNSET:
            field_dict["phoneNumber"] = phone_number
        if fax_number is not UNSET:
            field_dict["faxNumber"] = fax_number
        if country is not UNSET:
            field_dict["country"] = country
        if branch is not UNSET:
            field_dict["branch"] = branch
        if role is not UNSET:
            field_dict["role"] = role
        if tax_agent_number is not UNSET:
            field_dict["taxAgentNumber"] = tax_agent_number
        if intermediary_abn is not UNSET:
            field_dict["intermediaryAbn"] = intermediary_abn
        if intermediary_contact_name is not UNSET:
            field_dict["intermediaryContactName"] = intermediary_contact_name
        if intermediary_contact_email is not UNSET:
            field_dict["intermediaryContactEmail"] = intermediary_contact_email
        if intermediary_contact_phone is not UNSET:
            field_dict["intermediaryContactPhone"] = intermediary_contact_phone

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        abn = d.pop("abn", UNSET)

        name = d.pop("name", UNSET)

        address_line_1 = d.pop("addressLine1", UNSET)

        address_line_2 = d.pop("addressLine2", UNSET)

        suburb = d.pop("suburb", UNSET)

        state = d.pop("state", UNSET)

        post_code = d.pop("postCode", UNSET)

        contact_name = d.pop("contactName", UNSET)

        signatory_name = d.pop("signatoryName", UNSET)

        phone_number = d.pop("phoneNumber", UNSET)

        fax_number = d.pop("faxNumber", UNSET)

        country = d.pop("country", UNSET)

        branch = d.pop("branch", UNSET)

        _role = d.pop("role", UNSET)
        role: Union[Unset, BusinessAtoSupplierModelAtoSupplierRole]
        if isinstance(_role, Unset):
            role = UNSET
        else:
            role = BusinessAtoSupplierModelAtoSupplierRole(_role)

        tax_agent_number = d.pop("taxAgentNumber", UNSET)

        intermediary_abn = d.pop("intermediaryAbn", UNSET)

        intermediary_contact_name = d.pop("intermediaryContactName", UNSET)

        intermediary_contact_email = d.pop("intermediaryContactEmail", UNSET)

        intermediary_contact_phone = d.pop("intermediaryContactPhone", UNSET)

        business_ato_supplier_model = cls(
            id=id,
            abn=abn,
            name=name,
            address_line_1=address_line_1,
            address_line_2=address_line_2,
            suburb=suburb,
            state=state,
            post_code=post_code,
            contact_name=contact_name,
            signatory_name=signatory_name,
            phone_number=phone_number,
            fax_number=fax_number,
            country=country,
            branch=branch,
            role=role,
            tax_agent_number=tax_agent_number,
            intermediary_abn=intermediary_abn,
            intermediary_contact_name=intermediary_contact_name,
            intermediary_contact_email=intermediary_contact_email,
            intermediary_contact_phone=intermediary_contact_phone,
        )

        business_ato_supplier_model.additional_properties = d
        return business_ato_supplier_model

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
