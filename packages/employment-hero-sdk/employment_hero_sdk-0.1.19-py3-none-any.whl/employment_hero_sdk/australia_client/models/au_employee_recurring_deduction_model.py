import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.au_employee_recurring_deduction_model_au_employee_recurring_deduction_paid_to_enum import (
    AuEmployeeRecurringDeductionModelAuEmployeeRecurringDeductionPaidToEnum,
)
from ..models.au_employee_recurring_deduction_model_deduction_amount_not_reached_enum import (
    AuEmployeeRecurringDeductionModelDeductionAmountNotReachedEnum,
)
from ..models.au_employee_recurring_deduction_model_deduction_type_enum import (
    AuEmployeeRecurringDeductionModelDeductionTypeEnum,
)
from ..models.au_employee_recurring_deduction_model_preserved_earnings_calculation_type_enum import (
    AuEmployeeRecurringDeductionModelPreservedEarningsCalculationTypeEnum,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="AuEmployeeRecurringDeductionModel")


@_attrs_define
class AuEmployeeRecurringDeductionModel:
    """
    Attributes:
        deduction_type (Union[Unset, AuEmployeeRecurringDeductionModelDeductionTypeEnum]):
        paid_to (Union[Unset, AuEmployeeRecurringDeductionModelAuEmployeeRecurringDeductionPaidToEnum]):
        name (Union[Unset, str]):
        deduction_category_id (Union[Unset, int]):
        paid_to_account_id (Union[Unset, int]):
        external_reference_id (Union[Unset, str]):
        preserved_earnings_amount_not_reached_action (Union[Unset,
            AuEmployeeRecurringDeductionModelDeductionAmountNotReachedEnum]):
        carry_forward_unpaid_deductions (Union[Unset, bool]):
        carry_forward_unused_preserved_earnings (Union[Unset, bool]):
        payment_reference (Union[Unset, str]):
        preserved_earnings (Union[Unset, AuEmployeeRecurringDeductionModelPreservedEarningsCalculationTypeEnum]):
        preserved_earnings_amount (Union[Unset, float]):
        additional_data (Union[Unset, int]):
        priority (Union[Unset, int]):
        deleted (Union[Unset, bool]):
        id (Union[Unset, int]):
        employee_id (Union[Unset, int]):
        amount (Union[Unset, float]):
        expiry_date (Union[Unset, datetime.datetime]):
        from_date (Union[Unset, datetime.datetime]):
        maximum_amount_paid (Union[Unset, float]):
        total_amount_paid (Union[Unset, float]):
        is_active (Union[Unset, bool]):
        notes (Union[Unset, str]):
    """

    deduction_type: Union[Unset, AuEmployeeRecurringDeductionModelDeductionTypeEnum] = UNSET
    paid_to: Union[Unset, AuEmployeeRecurringDeductionModelAuEmployeeRecurringDeductionPaidToEnum] = UNSET
    name: Union[Unset, str] = UNSET
    deduction_category_id: Union[Unset, int] = UNSET
    paid_to_account_id: Union[Unset, int] = UNSET
    external_reference_id: Union[Unset, str] = UNSET
    preserved_earnings_amount_not_reached_action: Union[
        Unset, AuEmployeeRecurringDeductionModelDeductionAmountNotReachedEnum
    ] = UNSET
    carry_forward_unpaid_deductions: Union[Unset, bool] = UNSET
    carry_forward_unused_preserved_earnings: Union[Unset, bool] = UNSET
    payment_reference: Union[Unset, str] = UNSET
    preserved_earnings: Union[Unset, AuEmployeeRecurringDeductionModelPreservedEarningsCalculationTypeEnum] = UNSET
    preserved_earnings_amount: Union[Unset, float] = UNSET
    additional_data: Union[Unset, int] = UNSET
    priority: Union[Unset, int] = UNSET
    deleted: Union[Unset, bool] = UNSET
    id: Union[Unset, int] = UNSET
    employee_id: Union[Unset, int] = UNSET
    amount: Union[Unset, float] = UNSET
    expiry_date: Union[Unset, datetime.datetime] = UNSET
    from_date: Union[Unset, datetime.datetime] = UNSET
    maximum_amount_paid: Union[Unset, float] = UNSET
    total_amount_paid: Union[Unset, float] = UNSET
    is_active: Union[Unset, bool] = UNSET
    notes: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        deduction_type: Union[Unset, str] = UNSET
        if not isinstance(self.deduction_type, Unset):
            deduction_type = self.deduction_type.value

        paid_to: Union[Unset, str] = UNSET
        if not isinstance(self.paid_to, Unset):
            paid_to = self.paid_to.value

        name = self.name

        deduction_category_id = self.deduction_category_id

        paid_to_account_id = self.paid_to_account_id

        external_reference_id = self.external_reference_id

        preserved_earnings_amount_not_reached_action: Union[Unset, str] = UNSET
        if not isinstance(self.preserved_earnings_amount_not_reached_action, Unset):
            preserved_earnings_amount_not_reached_action = self.preserved_earnings_amount_not_reached_action.value

        carry_forward_unpaid_deductions = self.carry_forward_unpaid_deductions

        carry_forward_unused_preserved_earnings = self.carry_forward_unused_preserved_earnings

        payment_reference = self.payment_reference

        preserved_earnings: Union[Unset, str] = UNSET
        if not isinstance(self.preserved_earnings, Unset):
            preserved_earnings = self.preserved_earnings.value

        preserved_earnings_amount = self.preserved_earnings_amount

        additional_data = self.additional_data

        priority = self.priority

        deleted = self.deleted

        id = self.id

        employee_id = self.employee_id

        amount = self.amount

        expiry_date: Union[Unset, str] = UNSET
        if not isinstance(self.expiry_date, Unset):
            expiry_date = self.expiry_date.isoformat()

        from_date: Union[Unset, str] = UNSET
        if not isinstance(self.from_date, Unset):
            from_date = self.from_date.isoformat()

        maximum_amount_paid = self.maximum_amount_paid

        total_amount_paid = self.total_amount_paid

        is_active = self.is_active

        notes = self.notes

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if deduction_type is not UNSET:
            field_dict["deductionType"] = deduction_type
        if paid_to is not UNSET:
            field_dict["paidTo"] = paid_to
        if name is not UNSET:
            field_dict["name"] = name
        if deduction_category_id is not UNSET:
            field_dict["deductionCategoryId"] = deduction_category_id
        if paid_to_account_id is not UNSET:
            field_dict["paidToAccountId"] = paid_to_account_id
        if external_reference_id is not UNSET:
            field_dict["externalReferenceId"] = external_reference_id
        if preserved_earnings_amount_not_reached_action is not UNSET:
            field_dict["preservedEarningsAmountNotReachedAction"] = preserved_earnings_amount_not_reached_action
        if carry_forward_unpaid_deductions is not UNSET:
            field_dict["carryForwardUnpaidDeductions"] = carry_forward_unpaid_deductions
        if carry_forward_unused_preserved_earnings is not UNSET:
            field_dict["carryForwardUnusedPreservedEarnings"] = carry_forward_unused_preserved_earnings
        if payment_reference is not UNSET:
            field_dict["paymentReference"] = payment_reference
        if preserved_earnings is not UNSET:
            field_dict["preservedEarnings"] = preserved_earnings
        if preserved_earnings_amount is not UNSET:
            field_dict["preservedEarningsAmount"] = preserved_earnings_amount
        if additional_data is not UNSET:
            field_dict["additionalData"] = additional_data
        if priority is not UNSET:
            field_dict["priority"] = priority
        if deleted is not UNSET:
            field_dict["deleted"] = deleted
        if id is not UNSET:
            field_dict["id"] = id
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if amount is not UNSET:
            field_dict["amount"] = amount
        if expiry_date is not UNSET:
            field_dict["expiryDate"] = expiry_date
        if from_date is not UNSET:
            field_dict["fromDate"] = from_date
        if maximum_amount_paid is not UNSET:
            field_dict["maximumAmountPaid"] = maximum_amount_paid
        if total_amount_paid is not UNSET:
            field_dict["totalAmountPaid"] = total_amount_paid
        if is_active is not UNSET:
            field_dict["isActive"] = is_active
        if notes is not UNSET:
            field_dict["notes"] = notes

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _deduction_type = d.pop("deductionType", UNSET)
        deduction_type: Union[Unset, AuEmployeeRecurringDeductionModelDeductionTypeEnum]
        if isinstance(_deduction_type, Unset):
            deduction_type = UNSET
        else:
            deduction_type = AuEmployeeRecurringDeductionModelDeductionTypeEnum(_deduction_type)

        _paid_to = d.pop("paidTo", UNSET)
        paid_to: Union[Unset, AuEmployeeRecurringDeductionModelAuEmployeeRecurringDeductionPaidToEnum]
        if isinstance(_paid_to, Unset):
            paid_to = UNSET
        else:
            paid_to = AuEmployeeRecurringDeductionModelAuEmployeeRecurringDeductionPaidToEnum(_paid_to)

        name = d.pop("name", UNSET)

        deduction_category_id = d.pop("deductionCategoryId", UNSET)

        paid_to_account_id = d.pop("paidToAccountId", UNSET)

        external_reference_id = d.pop("externalReferenceId", UNSET)

        _preserved_earnings_amount_not_reached_action = d.pop("preservedEarningsAmountNotReachedAction", UNSET)
        preserved_earnings_amount_not_reached_action: Union[
            Unset, AuEmployeeRecurringDeductionModelDeductionAmountNotReachedEnum
        ]
        if isinstance(_preserved_earnings_amount_not_reached_action, Unset):
            preserved_earnings_amount_not_reached_action = UNSET
        else:
            preserved_earnings_amount_not_reached_action = (
                AuEmployeeRecurringDeductionModelDeductionAmountNotReachedEnum(
                    _preserved_earnings_amount_not_reached_action
                )
            )

        carry_forward_unpaid_deductions = d.pop("carryForwardUnpaidDeductions", UNSET)

        carry_forward_unused_preserved_earnings = d.pop("carryForwardUnusedPreservedEarnings", UNSET)

        payment_reference = d.pop("paymentReference", UNSET)

        _preserved_earnings = d.pop("preservedEarnings", UNSET)
        preserved_earnings: Union[Unset, AuEmployeeRecurringDeductionModelPreservedEarningsCalculationTypeEnum]
        if isinstance(_preserved_earnings, Unset):
            preserved_earnings = UNSET
        else:
            preserved_earnings = AuEmployeeRecurringDeductionModelPreservedEarningsCalculationTypeEnum(
                _preserved_earnings
            )

        preserved_earnings_amount = d.pop("preservedEarningsAmount", UNSET)

        additional_data = d.pop("additionalData", UNSET)

        priority = d.pop("priority", UNSET)

        deleted = d.pop("deleted", UNSET)

        id = d.pop("id", UNSET)

        employee_id = d.pop("employeeId", UNSET)

        amount = d.pop("amount", UNSET)

        _expiry_date = d.pop("expiryDate", UNSET)
        expiry_date: Union[Unset, datetime.datetime]
        if isinstance(_expiry_date, Unset):
            expiry_date = UNSET
        else:
            expiry_date = isoparse(_expiry_date)

        _from_date = d.pop("fromDate", UNSET)
        from_date: Union[Unset, datetime.datetime]
        if isinstance(_from_date, Unset):
            from_date = UNSET
        else:
            from_date = isoparse(_from_date)

        maximum_amount_paid = d.pop("maximumAmountPaid", UNSET)

        total_amount_paid = d.pop("totalAmountPaid", UNSET)

        is_active = d.pop("isActive", UNSET)

        notes = d.pop("notes", UNSET)

        au_employee_recurring_deduction_model = cls(
            deduction_type=deduction_type,
            paid_to=paid_to,
            name=name,
            deduction_category_id=deduction_category_id,
            paid_to_account_id=paid_to_account_id,
            external_reference_id=external_reference_id,
            preserved_earnings_amount_not_reached_action=preserved_earnings_amount_not_reached_action,
            carry_forward_unpaid_deductions=carry_forward_unpaid_deductions,
            carry_forward_unused_preserved_earnings=carry_forward_unused_preserved_earnings,
            payment_reference=payment_reference,
            preserved_earnings=preserved_earnings,
            preserved_earnings_amount=preserved_earnings_amount,
            additional_data=additional_data,
            priority=priority,
            deleted=deleted,
            id=id,
            employee_id=employee_id,
            amount=amount,
            expiry_date=expiry_date,
            from_date=from_date,
            maximum_amount_paid=maximum_amount_paid,
            total_amount_paid=total_amount_paid,
            is_active=is_active,
            notes=notes,
        )

        au_employee_recurring_deduction_model.additional_properties = d
        return au_employee_recurring_deduction_model

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
