from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.bank_account_edit_model_bank_account_type_enum import BankAccountEditModelBankAccountTypeEnum
from ..models.bank_account_edit_model_external_service import BankAccountEditModelExternalService
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.bank_account_edit_model_i_dictionary_string_string import BankAccountEditModelIDictionaryStringString


T = TypeVar("T", bound="BankAccountEditModel")


@_attrs_define
class BankAccountEditModel:
    """
    Attributes:
        id (Union[Unset, int]):
        bsb (Union[Unset, str]):
        account_name (Union[Unset, str]):
        account_number (Union[Unset, str]):
        allocated_percentage (Union[Unset, float]):
        fixed_amount (Union[Unset, float]):
        external_reference_id (Union[Unset, str]):
        source (Union[Unset, BankAccountEditModelExternalService]):
        allocate_balance (Union[Unset, bool]):
        is_employee_editable (Union[Unset, bool]):
        can_be_deleted (Union[Unset, bool]):
        account_type (Union[Unset, BankAccountEditModelBankAccountTypeEnum]):
        roll_number (Union[Unset, str]):
        bank_swift (Union[Unset, str]):
        branch_code (Union[Unset, str]):
        my_bank_code (Union[Unset, str]):
        my_other_bank_name (Union[Unset, str]):
        mdm_id (Union[Unset, str]):
        mdm_version (Union[Unset, int]):
        mdm_schema_version (Union[Unset, str]):
        triggered_from_mdm (Union[Unset, bool]):
        send_to_mdm (Union[Unset, bool]):
        ignore_fields (Union[Unset, BankAccountEditModelIDictionaryStringString]):
    """

    id: Union[Unset, int] = UNSET
    bsb: Union[Unset, str] = UNSET
    account_name: Union[Unset, str] = UNSET
    account_number: Union[Unset, str] = UNSET
    allocated_percentage: Union[Unset, float] = UNSET
    fixed_amount: Union[Unset, float] = UNSET
    external_reference_id: Union[Unset, str] = UNSET
    source: Union[Unset, BankAccountEditModelExternalService] = UNSET
    allocate_balance: Union[Unset, bool] = UNSET
    is_employee_editable: Union[Unset, bool] = UNSET
    can_be_deleted: Union[Unset, bool] = UNSET
    account_type: Union[Unset, BankAccountEditModelBankAccountTypeEnum] = UNSET
    roll_number: Union[Unset, str] = UNSET
    bank_swift: Union[Unset, str] = UNSET
    branch_code: Union[Unset, str] = UNSET
    my_bank_code: Union[Unset, str] = UNSET
    my_other_bank_name: Union[Unset, str] = UNSET
    mdm_id: Union[Unset, str] = UNSET
    mdm_version: Union[Unset, int] = UNSET
    mdm_schema_version: Union[Unset, str] = UNSET
    triggered_from_mdm: Union[Unset, bool] = UNSET
    send_to_mdm: Union[Unset, bool] = UNSET
    ignore_fields: Union[Unset, "BankAccountEditModelIDictionaryStringString"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        bsb = self.bsb

        account_name = self.account_name

        account_number = self.account_number

        allocated_percentage = self.allocated_percentage

        fixed_amount = self.fixed_amount

        external_reference_id = self.external_reference_id

        source: Union[Unset, str] = UNSET
        if not isinstance(self.source, Unset):
            source = self.source.value

        allocate_balance = self.allocate_balance

        is_employee_editable = self.is_employee_editable

        can_be_deleted = self.can_be_deleted

        account_type: Union[Unset, str] = UNSET
        if not isinstance(self.account_type, Unset):
            account_type = self.account_type.value

        roll_number = self.roll_number

        bank_swift = self.bank_swift

        branch_code = self.branch_code

        my_bank_code = self.my_bank_code

        my_other_bank_name = self.my_other_bank_name

        mdm_id = self.mdm_id

        mdm_version = self.mdm_version

        mdm_schema_version = self.mdm_schema_version

        triggered_from_mdm = self.triggered_from_mdm

        send_to_mdm = self.send_to_mdm

        ignore_fields: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.ignore_fields, Unset):
            ignore_fields = self.ignore_fields.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
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
        if external_reference_id is not UNSET:
            field_dict["externalReferenceId"] = external_reference_id
        if source is not UNSET:
            field_dict["source"] = source
        if allocate_balance is not UNSET:
            field_dict["allocateBalance"] = allocate_balance
        if is_employee_editable is not UNSET:
            field_dict["isEmployeeEditable"] = is_employee_editable
        if can_be_deleted is not UNSET:
            field_dict["canBeDeleted"] = can_be_deleted
        if account_type is not UNSET:
            field_dict["accountType"] = account_type
        if roll_number is not UNSET:
            field_dict["rollNumber"] = roll_number
        if bank_swift is not UNSET:
            field_dict["bankSwift"] = bank_swift
        if branch_code is not UNSET:
            field_dict["branchCode"] = branch_code
        if my_bank_code is not UNSET:
            field_dict["myBankCode"] = my_bank_code
        if my_other_bank_name is not UNSET:
            field_dict["myOtherBankName"] = my_other_bank_name
        if mdm_id is not UNSET:
            field_dict["mdmId"] = mdm_id
        if mdm_version is not UNSET:
            field_dict["mdmVersion"] = mdm_version
        if mdm_schema_version is not UNSET:
            field_dict["mdmSchemaVersion"] = mdm_schema_version
        if triggered_from_mdm is not UNSET:
            field_dict["triggeredFromMdm"] = triggered_from_mdm
        if send_to_mdm is not UNSET:
            field_dict["sendToMdm"] = send_to_mdm
        if ignore_fields is not UNSET:
            field_dict["ignoreFields"] = ignore_fields

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.bank_account_edit_model_i_dictionary_string_string import (
            BankAccountEditModelIDictionaryStringString,
        )

        d = src_dict.copy()
        id = d.pop("id", UNSET)

        bsb = d.pop("bsb", UNSET)

        account_name = d.pop("accountName", UNSET)

        account_number = d.pop("accountNumber", UNSET)

        allocated_percentage = d.pop("allocatedPercentage", UNSET)

        fixed_amount = d.pop("fixedAmount", UNSET)

        external_reference_id = d.pop("externalReferenceId", UNSET)

        _source = d.pop("source", UNSET)
        source: Union[Unset, BankAccountEditModelExternalService]
        if isinstance(_source, Unset):
            source = UNSET
        else:
            source = BankAccountEditModelExternalService(_source)

        allocate_balance = d.pop("allocateBalance", UNSET)

        is_employee_editable = d.pop("isEmployeeEditable", UNSET)

        can_be_deleted = d.pop("canBeDeleted", UNSET)

        _account_type = d.pop("accountType", UNSET)
        account_type: Union[Unset, BankAccountEditModelBankAccountTypeEnum]
        if isinstance(_account_type, Unset):
            account_type = UNSET
        else:
            account_type = BankAccountEditModelBankAccountTypeEnum(_account_type)

        roll_number = d.pop("rollNumber", UNSET)

        bank_swift = d.pop("bankSwift", UNSET)

        branch_code = d.pop("branchCode", UNSET)

        my_bank_code = d.pop("myBankCode", UNSET)

        my_other_bank_name = d.pop("myOtherBankName", UNSET)

        mdm_id = d.pop("mdmId", UNSET)

        mdm_version = d.pop("mdmVersion", UNSET)

        mdm_schema_version = d.pop("mdmSchemaVersion", UNSET)

        triggered_from_mdm = d.pop("triggeredFromMdm", UNSET)

        send_to_mdm = d.pop("sendToMdm", UNSET)

        _ignore_fields = d.pop("ignoreFields", UNSET)
        ignore_fields: Union[Unset, BankAccountEditModelIDictionaryStringString]
        if isinstance(_ignore_fields, Unset):
            ignore_fields = UNSET
        else:
            ignore_fields = BankAccountEditModelIDictionaryStringString.from_dict(_ignore_fields)

        bank_account_edit_model = cls(
            id=id,
            bsb=bsb,
            account_name=account_name,
            account_number=account_number,
            allocated_percentage=allocated_percentage,
            fixed_amount=fixed_amount,
            external_reference_id=external_reference_id,
            source=source,
            allocate_balance=allocate_balance,
            is_employee_editable=is_employee_editable,
            can_be_deleted=can_be_deleted,
            account_type=account_type,
            roll_number=roll_number,
            bank_swift=bank_swift,
            branch_code=branch_code,
            my_bank_code=my_bank_code,
            my_other_bank_name=my_other_bank_name,
            mdm_id=mdm_id,
            mdm_version=mdm_version,
            mdm_schema_version=mdm_schema_version,
            triggered_from_mdm=triggered_from_mdm,
            send_to_mdm=send_to_mdm,
            ignore_fields=ignore_fields,
        )

        bank_account_edit_model.additional_properties = d
        return bank_account_edit_model

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
