from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.payroll_access_model_nullable_business_restriction_type_enum import (
    PayrollAccessModelNullableBusinessRestrictionTypeEnum,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="PayrollAccessModel")


@_attrs_define
class PayrollAccessModel:
    """
    Attributes:
        approve_electronic_payroll_lodgement (Union[Unset, bool]):
        user_business_restriction_count (Union[Unset, int]):
        pay_run_approval_access (Union[Unset, PayrollAccessModelNullableBusinessRestrictionTypeEnum]):
        pay_run_creation_access (Union[Unset, PayrollAccessModelNullableBusinessRestrictionTypeEnum]):
        selected_pay_schedules_for_pay_run_approval (Union[Unset, List[int]]):
        selected_pay_schedules_for_pay_run_creation (Union[Unset, List[int]]):
    """

    approve_electronic_payroll_lodgement: Union[Unset, bool] = UNSET
    user_business_restriction_count: Union[Unset, int] = UNSET
    pay_run_approval_access: Union[Unset, PayrollAccessModelNullableBusinessRestrictionTypeEnum] = UNSET
    pay_run_creation_access: Union[Unset, PayrollAccessModelNullableBusinessRestrictionTypeEnum] = UNSET
    selected_pay_schedules_for_pay_run_approval: Union[Unset, List[int]] = UNSET
    selected_pay_schedules_for_pay_run_creation: Union[Unset, List[int]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        approve_electronic_payroll_lodgement = self.approve_electronic_payroll_lodgement

        user_business_restriction_count = self.user_business_restriction_count

        pay_run_approval_access: Union[Unset, str] = UNSET
        if not isinstance(self.pay_run_approval_access, Unset):
            pay_run_approval_access = self.pay_run_approval_access.value

        pay_run_creation_access: Union[Unset, str] = UNSET
        if not isinstance(self.pay_run_creation_access, Unset):
            pay_run_creation_access = self.pay_run_creation_access.value

        selected_pay_schedules_for_pay_run_approval: Union[Unset, List[int]] = UNSET
        if not isinstance(self.selected_pay_schedules_for_pay_run_approval, Unset):
            selected_pay_schedules_for_pay_run_approval = self.selected_pay_schedules_for_pay_run_approval

        selected_pay_schedules_for_pay_run_creation: Union[Unset, List[int]] = UNSET
        if not isinstance(self.selected_pay_schedules_for_pay_run_creation, Unset):
            selected_pay_schedules_for_pay_run_creation = self.selected_pay_schedules_for_pay_run_creation

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if approve_electronic_payroll_lodgement is not UNSET:
            field_dict["approveElectronicPayrollLodgement"] = approve_electronic_payroll_lodgement
        if user_business_restriction_count is not UNSET:
            field_dict["userBusinessRestrictionCount"] = user_business_restriction_count
        if pay_run_approval_access is not UNSET:
            field_dict["payRunApprovalAccess"] = pay_run_approval_access
        if pay_run_creation_access is not UNSET:
            field_dict["payRunCreationAccess"] = pay_run_creation_access
        if selected_pay_schedules_for_pay_run_approval is not UNSET:
            field_dict["selectedPaySchedulesForPayRunApproval"] = selected_pay_schedules_for_pay_run_approval
        if selected_pay_schedules_for_pay_run_creation is not UNSET:
            field_dict["selectedPaySchedulesForPayRunCreation"] = selected_pay_schedules_for_pay_run_creation

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        approve_electronic_payroll_lodgement = d.pop("approveElectronicPayrollLodgement", UNSET)

        user_business_restriction_count = d.pop("userBusinessRestrictionCount", UNSET)

        _pay_run_approval_access = d.pop("payRunApprovalAccess", UNSET)
        pay_run_approval_access: Union[Unset, PayrollAccessModelNullableBusinessRestrictionTypeEnum]
        if isinstance(_pay_run_approval_access, Unset):
            pay_run_approval_access = UNSET
        else:
            pay_run_approval_access = PayrollAccessModelNullableBusinessRestrictionTypeEnum(_pay_run_approval_access)

        _pay_run_creation_access = d.pop("payRunCreationAccess", UNSET)
        pay_run_creation_access: Union[Unset, PayrollAccessModelNullableBusinessRestrictionTypeEnum]
        if isinstance(_pay_run_creation_access, Unset):
            pay_run_creation_access = UNSET
        else:
            pay_run_creation_access = PayrollAccessModelNullableBusinessRestrictionTypeEnum(_pay_run_creation_access)

        selected_pay_schedules_for_pay_run_approval = cast(
            List[int], d.pop("selectedPaySchedulesForPayRunApproval", UNSET)
        )

        selected_pay_schedules_for_pay_run_creation = cast(
            List[int], d.pop("selectedPaySchedulesForPayRunCreation", UNSET)
        )

        payroll_access_model = cls(
            approve_electronic_payroll_lodgement=approve_electronic_payroll_lodgement,
            user_business_restriction_count=user_business_restriction_count,
            pay_run_approval_access=pay_run_approval_access,
            pay_run_creation_access=pay_run_creation_access,
            selected_pay_schedules_for_pay_run_approval=selected_pay_schedules_for_pay_run_approval,
            selected_pay_schedules_for_pay_run_creation=selected_pay_schedules_for_pay_run_creation,
        )

        payroll_access_model.additional_properties = d
        return payroll_access_model

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
