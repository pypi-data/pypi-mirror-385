from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DeductionModel")


@_attrs_define
class DeductionModel:
    """
    Attributes:
        deduction_category_id (Union[Unset, str]):
        deduction_category_name (Union[Unset, str]):
        amount (Union[Unset, float]):
        notes (Union[Unset, str]):
        payment_reference (Union[Unset, str]):
        note (Union[Unset, str]):
        associated_employee_deduction_category_id (Union[Unset, int]):
        pay_to_bank_account_bsb (Union[Unset, str]):
        pay_to_bank_account_swift (Union[Unset, str]):
        pay_to_bank_account_bank_code (Union[Unset, str]):
        pay_to_bank_account_number (Union[Unset, str]):
        pay_to_super_fund_name (Union[Unset, str]):
        pay_to_super_fund_member_number (Union[Unset, str]):
        pay_to (Union[Unset, str]):
        additional_data (Union[Unset, int]):
        id (Union[Unset, int]):
        external_id (Union[Unset, str]):
        location_id (Union[Unset, str]):
        location_name (Union[Unset, str]):
        employee_id (Union[Unset, str]):
        employee_name (Union[Unset, str]):
        employee_external_id (Union[Unset, str]):
    """

    deduction_category_id: Union[Unset, str] = UNSET
    deduction_category_name: Union[Unset, str] = UNSET
    amount: Union[Unset, float] = UNSET
    notes: Union[Unset, str] = UNSET
    payment_reference: Union[Unset, str] = UNSET
    note: Union[Unset, str] = UNSET
    associated_employee_deduction_category_id: Union[Unset, int] = UNSET
    pay_to_bank_account_bsb: Union[Unset, str] = UNSET
    pay_to_bank_account_swift: Union[Unset, str] = UNSET
    pay_to_bank_account_bank_code: Union[Unset, str] = UNSET
    pay_to_bank_account_number: Union[Unset, str] = UNSET
    pay_to_super_fund_name: Union[Unset, str] = UNSET
    pay_to_super_fund_member_number: Union[Unset, str] = UNSET
    pay_to: Union[Unset, str] = UNSET
    additional_data: Union[Unset, int] = UNSET
    id: Union[Unset, int] = UNSET
    external_id: Union[Unset, str] = UNSET
    location_id: Union[Unset, str] = UNSET
    location_name: Union[Unset, str] = UNSET
    employee_id: Union[Unset, str] = UNSET
    employee_name: Union[Unset, str] = UNSET
    employee_external_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        deduction_category_id = self.deduction_category_id

        deduction_category_name = self.deduction_category_name

        amount = self.amount

        notes = self.notes

        payment_reference = self.payment_reference

        note = self.note

        associated_employee_deduction_category_id = self.associated_employee_deduction_category_id

        pay_to_bank_account_bsb = self.pay_to_bank_account_bsb

        pay_to_bank_account_swift = self.pay_to_bank_account_swift

        pay_to_bank_account_bank_code = self.pay_to_bank_account_bank_code

        pay_to_bank_account_number = self.pay_to_bank_account_number

        pay_to_super_fund_name = self.pay_to_super_fund_name

        pay_to_super_fund_member_number = self.pay_to_super_fund_member_number

        pay_to = self.pay_to

        additional_data = self.additional_data

        id = self.id

        external_id = self.external_id

        location_id = self.location_id

        location_name = self.location_name

        employee_id = self.employee_id

        employee_name = self.employee_name

        employee_external_id = self.employee_external_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if deduction_category_id is not UNSET:
            field_dict["deductionCategoryId"] = deduction_category_id
        if deduction_category_name is not UNSET:
            field_dict["deductionCategoryName"] = deduction_category_name
        if amount is not UNSET:
            field_dict["amount"] = amount
        if notes is not UNSET:
            field_dict["notes"] = notes
        if payment_reference is not UNSET:
            field_dict["paymentReference"] = payment_reference
        if note is not UNSET:
            field_dict["note"] = note
        if associated_employee_deduction_category_id is not UNSET:
            field_dict["associatedEmployeeDeductionCategoryId"] = associated_employee_deduction_category_id
        if pay_to_bank_account_bsb is not UNSET:
            field_dict["payToBankAccountBSB"] = pay_to_bank_account_bsb
        if pay_to_bank_account_swift is not UNSET:
            field_dict["payToBankAccountSwift"] = pay_to_bank_account_swift
        if pay_to_bank_account_bank_code is not UNSET:
            field_dict["payToBankAccountBankCode"] = pay_to_bank_account_bank_code
        if pay_to_bank_account_number is not UNSET:
            field_dict["payToBankAccountNumber"] = pay_to_bank_account_number
        if pay_to_super_fund_name is not UNSET:
            field_dict["payToSuperFundName"] = pay_to_super_fund_name
        if pay_to_super_fund_member_number is not UNSET:
            field_dict["payToSuperFundMemberNumber"] = pay_to_super_fund_member_number
        if pay_to is not UNSET:
            field_dict["payTo"] = pay_to
        if additional_data is not UNSET:
            field_dict["additionalData"] = additional_data
        if id is not UNSET:
            field_dict["id"] = id
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if location_id is not UNSET:
            field_dict["locationId"] = location_id
        if location_name is not UNSET:
            field_dict["locationName"] = location_name
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if employee_name is not UNSET:
            field_dict["employeeName"] = employee_name
        if employee_external_id is not UNSET:
            field_dict["employeeExternalId"] = employee_external_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        deduction_category_id = d.pop("deductionCategoryId", UNSET)

        deduction_category_name = d.pop("deductionCategoryName", UNSET)

        amount = d.pop("amount", UNSET)

        notes = d.pop("notes", UNSET)

        payment_reference = d.pop("paymentReference", UNSET)

        note = d.pop("note", UNSET)

        associated_employee_deduction_category_id = d.pop("associatedEmployeeDeductionCategoryId", UNSET)

        pay_to_bank_account_bsb = d.pop("payToBankAccountBSB", UNSET)

        pay_to_bank_account_swift = d.pop("payToBankAccountSwift", UNSET)

        pay_to_bank_account_bank_code = d.pop("payToBankAccountBankCode", UNSET)

        pay_to_bank_account_number = d.pop("payToBankAccountNumber", UNSET)

        pay_to_super_fund_name = d.pop("payToSuperFundName", UNSET)

        pay_to_super_fund_member_number = d.pop("payToSuperFundMemberNumber", UNSET)

        pay_to = d.pop("payTo", UNSET)

        additional_data = d.pop("additionalData", UNSET)

        id = d.pop("id", UNSET)

        external_id = d.pop("externalId", UNSET)

        location_id = d.pop("locationId", UNSET)

        location_name = d.pop("locationName", UNSET)

        employee_id = d.pop("employeeId", UNSET)

        employee_name = d.pop("employeeName", UNSET)

        employee_external_id = d.pop("employeeExternalId", UNSET)

        deduction_model = cls(
            deduction_category_id=deduction_category_id,
            deduction_category_name=deduction_category_name,
            amount=amount,
            notes=notes,
            payment_reference=payment_reference,
            note=note,
            associated_employee_deduction_category_id=associated_employee_deduction_category_id,
            pay_to_bank_account_bsb=pay_to_bank_account_bsb,
            pay_to_bank_account_swift=pay_to_bank_account_swift,
            pay_to_bank_account_bank_code=pay_to_bank_account_bank_code,
            pay_to_bank_account_number=pay_to_bank_account_number,
            pay_to_super_fund_name=pay_to_super_fund_name,
            pay_to_super_fund_member_number=pay_to_super_fund_member_number,
            pay_to=pay_to,
            additional_data=additional_data,
            id=id,
            external_id=external_id,
            location_id=location_id,
            location_name=location_name,
            employee_id=employee_id,
            employee_name=employee_name,
            employee_external_id=employee_external_id,
        )

        deduction_model.additional_properties = d
        return deduction_model

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
