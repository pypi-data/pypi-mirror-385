from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.business_aba_model_nullable_payment_file_balance_additional_content import (
    BusinessAbaModelNullablePaymentFileBalanceAdditionalContent,
)
from ..models.business_aba_model_nullable_payment_file_payment_additional_content import (
    BusinessAbaModelNullablePaymentFilePaymentAdditionalContent,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="BusinessAbaModel")


@_attrs_define
class BusinessAbaModel:
    """
    Attributes:
        id (Union[Unset, int]):
        bsb (Union[Unset, str]):
        account_number (Union[Unset, str]):
        account_name (Union[Unset, str]):
        financial_institution_code (Union[Unset, str]):
        lodgement_reference (Union[Unset, str]):
        user_name (Union[Unset, str]):
        user_id (Union[Unset, str]):
        include_self_balancing_transaction (Union[Unset, bool]):
        merge_multiple_account_payments (Union[Unset, bool]):
        balance_lodgement_reference (Union[Unset, str]):
        payment_additional_content (Union[Unset, BusinessAbaModelNullablePaymentFilePaymentAdditionalContent]):
        balance_additional_content (Union[Unset, BusinessAbaModelNullablePaymentFileBalanceAdditionalContent]):
    """

    id: Union[Unset, int] = UNSET
    bsb: Union[Unset, str] = UNSET
    account_number: Union[Unset, str] = UNSET
    account_name: Union[Unset, str] = UNSET
    financial_institution_code: Union[Unset, str] = UNSET
    lodgement_reference: Union[Unset, str] = UNSET
    user_name: Union[Unset, str] = UNSET
    user_id: Union[Unset, str] = UNSET
    include_self_balancing_transaction: Union[Unset, bool] = UNSET
    merge_multiple_account_payments: Union[Unset, bool] = UNSET
    balance_lodgement_reference: Union[Unset, str] = UNSET
    payment_additional_content: Union[Unset, BusinessAbaModelNullablePaymentFilePaymentAdditionalContent] = UNSET
    balance_additional_content: Union[Unset, BusinessAbaModelNullablePaymentFileBalanceAdditionalContent] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        bsb = self.bsb

        account_number = self.account_number

        account_name = self.account_name

        financial_institution_code = self.financial_institution_code

        lodgement_reference = self.lodgement_reference

        user_name = self.user_name

        user_id = self.user_id

        include_self_balancing_transaction = self.include_self_balancing_transaction

        merge_multiple_account_payments = self.merge_multiple_account_payments

        balance_lodgement_reference = self.balance_lodgement_reference

        payment_additional_content: Union[Unset, str] = UNSET
        if not isinstance(self.payment_additional_content, Unset):
            payment_additional_content = self.payment_additional_content.value

        balance_additional_content: Union[Unset, str] = UNSET
        if not isinstance(self.balance_additional_content, Unset):
            balance_additional_content = self.balance_additional_content.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if bsb is not UNSET:
            field_dict["bsb"] = bsb
        if account_number is not UNSET:
            field_dict["accountNumber"] = account_number
        if account_name is not UNSET:
            field_dict["accountName"] = account_name
        if financial_institution_code is not UNSET:
            field_dict["financialInstitutionCode"] = financial_institution_code
        if lodgement_reference is not UNSET:
            field_dict["lodgementReference"] = lodgement_reference
        if user_name is not UNSET:
            field_dict["userName"] = user_name
        if user_id is not UNSET:
            field_dict["userId"] = user_id
        if include_self_balancing_transaction is not UNSET:
            field_dict["includeSelfBalancingTransaction"] = include_self_balancing_transaction
        if merge_multiple_account_payments is not UNSET:
            field_dict["mergeMultipleAccountPayments"] = merge_multiple_account_payments
        if balance_lodgement_reference is not UNSET:
            field_dict["balanceLodgementReference"] = balance_lodgement_reference
        if payment_additional_content is not UNSET:
            field_dict["paymentAdditionalContent"] = payment_additional_content
        if balance_additional_content is not UNSET:
            field_dict["balanceAdditionalContent"] = balance_additional_content

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        bsb = d.pop("bsb", UNSET)

        account_number = d.pop("accountNumber", UNSET)

        account_name = d.pop("accountName", UNSET)

        financial_institution_code = d.pop("financialInstitutionCode", UNSET)

        lodgement_reference = d.pop("lodgementReference", UNSET)

        user_name = d.pop("userName", UNSET)

        user_id = d.pop("userId", UNSET)

        include_self_balancing_transaction = d.pop("includeSelfBalancingTransaction", UNSET)

        merge_multiple_account_payments = d.pop("mergeMultipleAccountPayments", UNSET)

        balance_lodgement_reference = d.pop("balanceLodgementReference", UNSET)

        _payment_additional_content = d.pop("paymentAdditionalContent", UNSET)
        payment_additional_content: Union[Unset, BusinessAbaModelNullablePaymentFilePaymentAdditionalContent]
        if isinstance(_payment_additional_content, Unset):
            payment_additional_content = UNSET
        else:
            payment_additional_content = BusinessAbaModelNullablePaymentFilePaymentAdditionalContent(
                _payment_additional_content
            )

        _balance_additional_content = d.pop("balanceAdditionalContent", UNSET)
        balance_additional_content: Union[Unset, BusinessAbaModelNullablePaymentFileBalanceAdditionalContent]
        if isinstance(_balance_additional_content, Unset):
            balance_additional_content = UNSET
        else:
            balance_additional_content = BusinessAbaModelNullablePaymentFileBalanceAdditionalContent(
                _balance_additional_content
            )

        business_aba_model = cls(
            id=id,
            bsb=bsb,
            account_number=account_number,
            account_name=account_name,
            financial_institution_code=financial_institution_code,
            lodgement_reference=lodgement_reference,
            user_name=user_name,
            user_id=user_id,
            include_self_balancing_transaction=include_self_balancing_transaction,
            merge_multiple_account_payments=merge_multiple_account_payments,
            balance_lodgement_reference=balance_lodgement_reference,
            payment_additional_content=payment_additional_content,
            balance_additional_content=balance_additional_content,
        )

        business_aba_model.additional_properties = d
        return business_aba_model

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
