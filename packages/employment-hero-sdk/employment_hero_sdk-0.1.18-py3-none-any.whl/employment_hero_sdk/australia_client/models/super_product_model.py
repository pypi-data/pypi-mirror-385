from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.super_product_model_external_service import SuperProductModelExternalService
from ..types import UNSET, Unset

T = TypeVar("T", bound="SuperProductModel")


@_attrs_define
class SuperProductModel:
    """
    Attributes:
        id (Union[Unset, int]):
        abn (Union[Unset, str]):
        product_code (Union[Unset, str]):
        product_type (Union[Unset, str]):
        business_name (Union[Unset, str]):
        display_name (Union[Unset, str]):
        product_name (Union[Unset, str]):
        account_number (Union[Unset, str]):
        bsb (Union[Unset, str]):
        account_name (Union[Unset, str]):
        source (Union[Unset, SuperProductModelExternalService]):
        electronic_service_address (Union[Unset, str]):
        email (Union[Unset, str]):
        external_reference_id (Union[Unset, str]):
    """

    id: Union[Unset, int] = UNSET
    abn: Union[Unset, str] = UNSET
    product_code: Union[Unset, str] = UNSET
    product_type: Union[Unset, str] = UNSET
    business_name: Union[Unset, str] = UNSET
    display_name: Union[Unset, str] = UNSET
    product_name: Union[Unset, str] = UNSET
    account_number: Union[Unset, str] = UNSET
    bsb: Union[Unset, str] = UNSET
    account_name: Union[Unset, str] = UNSET
    source: Union[Unset, SuperProductModelExternalService] = UNSET
    electronic_service_address: Union[Unset, str] = UNSET
    email: Union[Unset, str] = UNSET
    external_reference_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        abn = self.abn

        product_code = self.product_code

        product_type = self.product_type

        business_name = self.business_name

        display_name = self.display_name

        product_name = self.product_name

        account_number = self.account_number

        bsb = self.bsb

        account_name = self.account_name

        source: Union[Unset, str] = UNSET
        if not isinstance(self.source, Unset):
            source = self.source.value

        electronic_service_address = self.electronic_service_address

        email = self.email

        external_reference_id = self.external_reference_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if abn is not UNSET:
            field_dict["abn"] = abn
        if product_code is not UNSET:
            field_dict["productCode"] = product_code
        if product_type is not UNSET:
            field_dict["productType"] = product_type
        if business_name is not UNSET:
            field_dict["businessName"] = business_name
        if display_name is not UNSET:
            field_dict["displayName"] = display_name
        if product_name is not UNSET:
            field_dict["productName"] = product_name
        if account_number is not UNSET:
            field_dict["accountNumber"] = account_number
        if bsb is not UNSET:
            field_dict["bsb"] = bsb
        if account_name is not UNSET:
            field_dict["accountName"] = account_name
        if source is not UNSET:
            field_dict["source"] = source
        if electronic_service_address is not UNSET:
            field_dict["electronicServiceAddress"] = electronic_service_address
        if email is not UNSET:
            field_dict["email"] = email
        if external_reference_id is not UNSET:
            field_dict["externalReferenceId"] = external_reference_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        abn = d.pop("abn", UNSET)

        product_code = d.pop("productCode", UNSET)

        product_type = d.pop("productType", UNSET)

        business_name = d.pop("businessName", UNSET)

        display_name = d.pop("displayName", UNSET)

        product_name = d.pop("productName", UNSET)

        account_number = d.pop("accountNumber", UNSET)

        bsb = d.pop("bsb", UNSET)

        account_name = d.pop("accountName", UNSET)

        _source = d.pop("source", UNSET)
        source: Union[Unset, SuperProductModelExternalService]
        if isinstance(_source, Unset):
            source = UNSET
        else:
            source = SuperProductModelExternalService(_source)

        electronic_service_address = d.pop("electronicServiceAddress", UNSET)

        email = d.pop("email", UNSET)

        external_reference_id = d.pop("externalReferenceId", UNSET)

        super_product_model = cls(
            id=id,
            abn=abn,
            product_code=product_code,
            product_type=product_type,
            business_name=business_name,
            display_name=display_name,
            product_name=product_name,
            account_number=account_number,
            bsb=bsb,
            account_name=account_name,
            source=source,
            electronic_service_address=electronic_service_address,
            email=email,
            external_reference_id=external_reference_id,
        )

        super_product_model.additional_properties = d
        return super_product_model

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
