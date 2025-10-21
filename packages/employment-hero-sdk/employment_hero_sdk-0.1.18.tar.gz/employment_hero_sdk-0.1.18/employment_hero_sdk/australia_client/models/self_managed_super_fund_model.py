from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SelfManagedSuperFundModel")


@_attrs_define
class SelfManagedSuperFundModel:
    """
    Attributes:
        id (Union[Unset, int]):
        abn (Union[Unset, str]):
        fund_name (Union[Unset, str]):
        account_name (Union[Unset, str]):
        account_number (Union[Unset, str]):
        bsb (Union[Unset, str]):
        electronic_service_address (Union[Unset, str]):
        email (Union[Unset, str]):
        employee_id (Union[Unset, int]):
        external_id (Union[Unset, str]):
    """

    id: Union[Unset, int] = UNSET
    abn: Union[Unset, str] = UNSET
    fund_name: Union[Unset, str] = UNSET
    account_name: Union[Unset, str] = UNSET
    account_number: Union[Unset, str] = UNSET
    bsb: Union[Unset, str] = UNSET
    electronic_service_address: Union[Unset, str] = UNSET
    email: Union[Unset, str] = UNSET
    employee_id: Union[Unset, int] = UNSET
    external_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        abn = self.abn

        fund_name = self.fund_name

        account_name = self.account_name

        account_number = self.account_number

        bsb = self.bsb

        electronic_service_address = self.electronic_service_address

        email = self.email

        employee_id = self.employee_id

        external_id = self.external_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if abn is not UNSET:
            field_dict["abn"] = abn
        if fund_name is not UNSET:
            field_dict["fundName"] = fund_name
        if account_name is not UNSET:
            field_dict["accountName"] = account_name
        if account_number is not UNSET:
            field_dict["accountNumber"] = account_number
        if bsb is not UNSET:
            field_dict["bsb"] = bsb
        if electronic_service_address is not UNSET:
            field_dict["electronicServiceAddress"] = electronic_service_address
        if email is not UNSET:
            field_dict["email"] = email
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if external_id is not UNSET:
            field_dict["externalId"] = external_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        abn = d.pop("abn", UNSET)

        fund_name = d.pop("fundName", UNSET)

        account_name = d.pop("accountName", UNSET)

        account_number = d.pop("accountNumber", UNSET)

        bsb = d.pop("bsb", UNSET)

        electronic_service_address = d.pop("electronicServiceAddress", UNSET)

        email = d.pop("email", UNSET)

        employee_id = d.pop("employeeId", UNSET)

        external_id = d.pop("externalId", UNSET)

        self_managed_super_fund_model = cls(
            id=id,
            abn=abn,
            fund_name=fund_name,
            account_name=account_name,
            account_number=account_number,
            bsb=bsb,
            electronic_service_address=electronic_service_address,
            email=email,
            employee_id=employee_id,
            external_id=external_id,
        )

        self_managed_super_fund_model.additional_properties = d
        return self_managed_super_fund_model

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
