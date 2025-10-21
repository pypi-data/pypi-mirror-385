from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.au_bank_account_model_bank_account_type_enum import AuBankAccountModelBankAccountTypeEnum
from ..types import UNSET, Unset

T = TypeVar("T", bound="AuBankAccountModel")


@_attrs_define
class AuBankAccountModel:
    """
    Attributes:
        account_type (Union[Unset, AuBankAccountModelBankAccountTypeEnum]):
        id (Union[Unset, int]):
        employee_id (Union[Unset, int]):
        bsb (Union[Unset, str]):
        account_name (Union[Unset, str]):
        account_number (Union[Unset, str]):
        allocated_percentage (Union[Unset, float]):
        fixed_amount (Union[Unset, float]):
        allocate_balance (Union[Unset, bool]):
        is_employee_editable (Union[Unset, bool]):
        can_be_deleted (Union[Unset, bool]):
        external_reference_id (Union[Unset, str]):
    """

    account_type: Union[Unset, AuBankAccountModelBankAccountTypeEnum] = UNSET
    id: Union[Unset, int] = UNSET
    employee_id: Union[Unset, int] = UNSET
    bsb: Union[Unset, str] = UNSET
    account_name: Union[Unset, str] = UNSET
    account_number: Union[Unset, str] = UNSET
    allocated_percentage: Union[Unset, float] = UNSET
    fixed_amount: Union[Unset, float] = UNSET
    allocate_balance: Union[Unset, bool] = UNSET
    is_employee_editable: Union[Unset, bool] = UNSET
    can_be_deleted: Union[Unset, bool] = UNSET
    external_reference_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        account_type: Union[Unset, str] = UNSET
        if not isinstance(self.account_type, Unset):
            account_type = self.account_type.value

        id = self.id

        employee_id = self.employee_id

        bsb = self.bsb

        account_name = self.account_name

        account_number = self.account_number

        allocated_percentage = self.allocated_percentage

        fixed_amount = self.fixed_amount

        allocate_balance = self.allocate_balance

        is_employee_editable = self.is_employee_editable

        can_be_deleted = self.can_be_deleted

        external_reference_id = self.external_reference_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if account_type is not UNSET:
            field_dict["accountType"] = account_type
        if id is not UNSET:
            field_dict["id"] = id
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if bsb is not UNSET:
            field_dict["bsb"] = bsb
        if account_name is not UNSET:
            field_dict["accountName"] = account_name
        if account_number is not UNSET:
            field_dict["accountNumber"] = account_number
        if allocated_percentage is not UNSET:
            field_dict["allocatedPercentage"] = allocated_percentage
        if fixed_amount is not UNSET:
            field_dict["fixedAmount"] = fixed_amount
        if allocate_balance is not UNSET:
            field_dict["allocateBalance"] = allocate_balance
        if is_employee_editable is not UNSET:
            field_dict["isEmployeeEditable"] = is_employee_editable
        if can_be_deleted is not UNSET:
            field_dict["canBeDeleted"] = can_be_deleted
        if external_reference_id is not UNSET:
            field_dict["externalReferenceId"] = external_reference_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _account_type = d.pop("accountType", UNSET)
        account_type: Union[Unset, AuBankAccountModelBankAccountTypeEnum]
        if isinstance(_account_type, Unset):
            account_type = UNSET
        else:
            account_type = AuBankAccountModelBankAccountTypeEnum(_account_type)

        id = d.pop("id", UNSET)

        employee_id = d.pop("employeeId", UNSET)

        bsb = d.pop("bsb", UNSET)

        account_name = d.pop("accountName", UNSET)

        account_number = d.pop("accountNumber", UNSET)

        allocated_percentage = d.pop("allocatedPercentage", UNSET)

        fixed_amount = d.pop("fixedAmount", UNSET)

        allocate_balance = d.pop("allocateBalance", UNSET)

        is_employee_editable = d.pop("isEmployeeEditable", UNSET)

        can_be_deleted = d.pop("canBeDeleted", UNSET)

        external_reference_id = d.pop("externalReferenceId", UNSET)

        au_bank_account_model = cls(
            account_type=account_type,
            id=id,
            employee_id=employee_id,
            bsb=bsb,
            account_name=account_name,
            account_number=account_number,
            allocated_percentage=allocated_percentage,
            fixed_amount=fixed_amount,
            allocate_balance=allocate_balance,
            is_employee_editable=is_employee_editable,
            can_be_deleted=can_be_deleted,
            external_reference_id=external_reference_id,
        )

        au_bank_account_model.additional_properties = d
        return au_bank_account_model

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
