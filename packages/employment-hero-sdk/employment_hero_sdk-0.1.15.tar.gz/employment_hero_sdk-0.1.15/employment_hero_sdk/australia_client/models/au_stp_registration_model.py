from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.au_stp_registration_model_ato_integration_option import AuStpRegistrationModelAtoIntegrationOption
from ..models.au_stp_registration_model_ato_supplier_role import AuStpRegistrationModelAtoSupplierRole
from ..types import UNSET, Unset

T = TypeVar("T", bound="AuStpRegistrationModel")


@_attrs_define
class AuStpRegistrationModel:
    """
    Attributes:
        name (Union[Unset, str]):
        branch (Union[Unset, str]):
        abn (Union[Unset, str]):
        contact_name (Union[Unset, str]):
        contact_phone_number (Union[Unset, str]):
        contact_email_address (Union[Unset, str]):
        address_line_1 (Union[Unset, str]):
        address_line_2 (Union[Unset, str]):
        suburb_id (Union[Unset, int]):
        suburb (Union[Unset, str]):
        post_code (Union[Unset, str]):
        state (Union[Unset, str]):
        lodgement_role (Union[Unset, AuStpRegistrationModelAtoSupplierRole]):
        tax_agent_number (Union[Unset, str]):
        intermediary_abn (Union[Unset, str]):
        intermediary_contact_name (Union[Unset, str]):
        intermediary_contact_email (Union[Unset, str]):
        intermediary_contact_phone (Union[Unset, str]):
        ato_integration_option (Union[Unset, AuStpRegistrationModelAtoIntegrationOption]):
        sbr_software_id (Union[Unset, str]):
        sbr_enabled (Union[Unset, bool]):
        single_touch_payroll_enabled (Union[Unset, bool]):
    """

    name: Union[Unset, str] = UNSET
    branch: Union[Unset, str] = UNSET
    abn: Union[Unset, str] = UNSET
    contact_name: Union[Unset, str] = UNSET
    contact_phone_number: Union[Unset, str] = UNSET
    contact_email_address: Union[Unset, str] = UNSET
    address_line_1: Union[Unset, str] = UNSET
    address_line_2: Union[Unset, str] = UNSET
    suburb_id: Union[Unset, int] = UNSET
    suburb: Union[Unset, str] = UNSET
    post_code: Union[Unset, str] = UNSET
    state: Union[Unset, str] = UNSET
    lodgement_role: Union[Unset, AuStpRegistrationModelAtoSupplierRole] = UNSET
    tax_agent_number: Union[Unset, str] = UNSET
    intermediary_abn: Union[Unset, str] = UNSET
    intermediary_contact_name: Union[Unset, str] = UNSET
    intermediary_contact_email: Union[Unset, str] = UNSET
    intermediary_contact_phone: Union[Unset, str] = UNSET
    ato_integration_option: Union[Unset, AuStpRegistrationModelAtoIntegrationOption] = UNSET
    sbr_software_id: Union[Unset, str] = UNSET
    sbr_enabled: Union[Unset, bool] = UNSET
    single_touch_payroll_enabled: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name

        branch = self.branch

        abn = self.abn

        contact_name = self.contact_name

        contact_phone_number = self.contact_phone_number

        contact_email_address = self.contact_email_address

        address_line_1 = self.address_line_1

        address_line_2 = self.address_line_2

        suburb_id = self.suburb_id

        suburb = self.suburb

        post_code = self.post_code

        state = self.state

        lodgement_role: Union[Unset, str] = UNSET
        if not isinstance(self.lodgement_role, Unset):
            lodgement_role = self.lodgement_role.value

        tax_agent_number = self.tax_agent_number

        intermediary_abn = self.intermediary_abn

        intermediary_contact_name = self.intermediary_contact_name

        intermediary_contact_email = self.intermediary_contact_email

        intermediary_contact_phone = self.intermediary_contact_phone

        ato_integration_option: Union[Unset, str] = UNSET
        if not isinstance(self.ato_integration_option, Unset):
            ato_integration_option = self.ato_integration_option.value

        sbr_software_id = self.sbr_software_id

        sbr_enabled = self.sbr_enabled

        single_touch_payroll_enabled = self.single_touch_payroll_enabled

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if branch is not UNSET:
            field_dict["branch"] = branch
        if abn is not UNSET:
            field_dict["abn"] = abn
        if contact_name is not UNSET:
            field_dict["contactName"] = contact_name
        if contact_phone_number is not UNSET:
            field_dict["contactPhoneNumber"] = contact_phone_number
        if contact_email_address is not UNSET:
            field_dict["contactEmailAddress"] = contact_email_address
        if address_line_1 is not UNSET:
            field_dict["addressLine1"] = address_line_1
        if address_line_2 is not UNSET:
            field_dict["addressLine2"] = address_line_2
        if suburb_id is not UNSET:
            field_dict["suburbId"] = suburb_id
        if suburb is not UNSET:
            field_dict["suburb"] = suburb
        if post_code is not UNSET:
            field_dict["postCode"] = post_code
        if state is not UNSET:
            field_dict["state"] = state
        if lodgement_role is not UNSET:
            field_dict["lodgementRole"] = lodgement_role
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
        if ato_integration_option is not UNSET:
            field_dict["atoIntegrationOption"] = ato_integration_option
        if sbr_software_id is not UNSET:
            field_dict["sbrSoftwareId"] = sbr_software_id
        if sbr_enabled is not UNSET:
            field_dict["sbrEnabled"] = sbr_enabled
        if single_touch_payroll_enabled is not UNSET:
            field_dict["singleTouchPayrollEnabled"] = single_touch_payroll_enabled

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name", UNSET)

        branch = d.pop("branch", UNSET)

        abn = d.pop("abn", UNSET)

        contact_name = d.pop("contactName", UNSET)

        contact_phone_number = d.pop("contactPhoneNumber", UNSET)

        contact_email_address = d.pop("contactEmailAddress", UNSET)

        address_line_1 = d.pop("addressLine1", UNSET)

        address_line_2 = d.pop("addressLine2", UNSET)

        suburb_id = d.pop("suburbId", UNSET)

        suburb = d.pop("suburb", UNSET)

        post_code = d.pop("postCode", UNSET)

        state = d.pop("state", UNSET)

        _lodgement_role = d.pop("lodgementRole", UNSET)
        lodgement_role: Union[Unset, AuStpRegistrationModelAtoSupplierRole]
        if isinstance(_lodgement_role, Unset):
            lodgement_role = UNSET
        else:
            lodgement_role = AuStpRegistrationModelAtoSupplierRole(_lodgement_role)

        tax_agent_number = d.pop("taxAgentNumber", UNSET)

        intermediary_abn = d.pop("intermediaryAbn", UNSET)

        intermediary_contact_name = d.pop("intermediaryContactName", UNSET)

        intermediary_contact_email = d.pop("intermediaryContactEmail", UNSET)

        intermediary_contact_phone = d.pop("intermediaryContactPhone", UNSET)

        _ato_integration_option = d.pop("atoIntegrationOption", UNSET)
        ato_integration_option: Union[Unset, AuStpRegistrationModelAtoIntegrationOption]
        if isinstance(_ato_integration_option, Unset):
            ato_integration_option = UNSET
        else:
            ato_integration_option = AuStpRegistrationModelAtoIntegrationOption(_ato_integration_option)

        sbr_software_id = d.pop("sbrSoftwareId", UNSET)

        sbr_enabled = d.pop("sbrEnabled", UNSET)

        single_touch_payroll_enabled = d.pop("singleTouchPayrollEnabled", UNSET)

        au_stp_registration_model = cls(
            name=name,
            branch=branch,
            abn=abn,
            contact_name=contact_name,
            contact_phone_number=contact_phone_number,
            contact_email_address=contact_email_address,
            address_line_1=address_line_1,
            address_line_2=address_line_2,
            suburb_id=suburb_id,
            suburb=suburb,
            post_code=post_code,
            state=state,
            lodgement_role=lodgement_role,
            tax_agent_number=tax_agent_number,
            intermediary_abn=intermediary_abn,
            intermediary_contact_name=intermediary_contact_name,
            intermediary_contact_email=intermediary_contact_email,
            intermediary_contact_phone=intermediary_contact_phone,
            ato_integration_option=ato_integration_option,
            sbr_software_id=sbr_software_id,
            sbr_enabled=sbr_enabled,
            single_touch_payroll_enabled=single_touch_payroll_enabled,
        )

        au_stp_registration_model.additional_properties = d
        return au_stp_registration_model

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
