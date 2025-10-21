from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.au_leave_category_model_au_leave_category_type_enum import AuLeaveCategoryModelAuLeaveCategoryTypeEnum
from ..models.au_leave_category_model_leave_allowance_unit_enum import AuLeaveCategoryModelLeaveAllowanceUnitEnum
from ..models.au_leave_category_model_leave_unit_type_enum import AuLeaveCategoryModelLeaveUnitTypeEnum
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.au_leave_accrual_rule_model import AuLeaveAccrualRuleModel
    from ..models.leave_entitlement_model import LeaveEntitlementModel


T = TypeVar("T", bound="AuLeaveCategoryModel")


@_attrs_define
class AuLeaveCategoryModel:
    """
    Attributes:
        contingent_period (Union[Unset, float]):
        entitlement_period (Union[Unset, float]):
        leave_loading (Union[Unset, float]):
        unit_type (Union[Unset, AuLeaveCategoryModelLeaveAllowanceUnitEnum]):
        leave_category_type (Union[Unset, AuLeaveCategoryModelAuLeaveCategoryTypeEnum]):
        leave_accrual_rule (Union[Unset, AuLeaveAccrualRuleModel]):
        transfer_on_termination_to_pay_category_id (Union[Unset, int]):
        id (Union[Unset, int]):
        name (Union[Unset, str]):
        units (Union[Unset, float]):
        automatically_accrues (Union[Unset, bool]):
        is_private (Union[Unset, bool]):
        exclude_from_termination_payout (Union[Unset, bool]):
        external_id (Union[Unset, str]):
        source (Union[Unset, str]):
        is_balance_untracked (Union[Unset, bool]):
        deduct_from_primary_pay_category (Union[Unset, bool]):
        deduct_from_pay_category_id (Union[Unset, int]):
        transfer_to_pay_category_id (Union[Unset, int]):
        hide_accruals_on_payslip (Union[Unset, bool]):
        use_deduct_from_pay_category_rate (Union[Unset, bool]):
        is_name_private (Union[Unset, bool]):
        leave_unit_type (Union[Unset, AuLeaveCategoryModelLeaveUnitTypeEnum]):
        payout_as_etp (Union[Unset, bool]):
        accrues_first_pay_run_per_period_only (Union[Unset, bool]):
        prevent_negative_balance_unpaid_leave_category_id (Union[Unset, int]):
        leave_entitlement (Union[Unset, LeaveEntitlementModel]):
    """

    contingent_period: Union[Unset, float] = UNSET
    entitlement_period: Union[Unset, float] = UNSET
    leave_loading: Union[Unset, float] = UNSET
    unit_type: Union[Unset, AuLeaveCategoryModelLeaveAllowanceUnitEnum] = UNSET
    leave_category_type: Union[Unset, AuLeaveCategoryModelAuLeaveCategoryTypeEnum] = UNSET
    leave_accrual_rule: Union[Unset, "AuLeaveAccrualRuleModel"] = UNSET
    transfer_on_termination_to_pay_category_id: Union[Unset, int] = UNSET
    id: Union[Unset, int] = UNSET
    name: Union[Unset, str] = UNSET
    units: Union[Unset, float] = UNSET
    automatically_accrues: Union[Unset, bool] = UNSET
    is_private: Union[Unset, bool] = UNSET
    exclude_from_termination_payout: Union[Unset, bool] = UNSET
    external_id: Union[Unset, str] = UNSET
    source: Union[Unset, str] = UNSET
    is_balance_untracked: Union[Unset, bool] = UNSET
    deduct_from_primary_pay_category: Union[Unset, bool] = UNSET
    deduct_from_pay_category_id: Union[Unset, int] = UNSET
    transfer_to_pay_category_id: Union[Unset, int] = UNSET
    hide_accruals_on_payslip: Union[Unset, bool] = UNSET
    use_deduct_from_pay_category_rate: Union[Unset, bool] = UNSET
    is_name_private: Union[Unset, bool] = UNSET
    leave_unit_type: Union[Unset, AuLeaveCategoryModelLeaveUnitTypeEnum] = UNSET
    payout_as_etp: Union[Unset, bool] = UNSET
    accrues_first_pay_run_per_period_only: Union[Unset, bool] = UNSET
    prevent_negative_balance_unpaid_leave_category_id: Union[Unset, int] = UNSET
    leave_entitlement: Union[Unset, "LeaveEntitlementModel"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        contingent_period = self.contingent_period

        entitlement_period = self.entitlement_period

        leave_loading = self.leave_loading

        unit_type: Union[Unset, str] = UNSET
        if not isinstance(self.unit_type, Unset):
            unit_type = self.unit_type.value

        leave_category_type: Union[Unset, str] = UNSET
        if not isinstance(self.leave_category_type, Unset):
            leave_category_type = self.leave_category_type.value

        leave_accrual_rule: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.leave_accrual_rule, Unset):
            leave_accrual_rule = self.leave_accrual_rule.to_dict()

        transfer_on_termination_to_pay_category_id = self.transfer_on_termination_to_pay_category_id

        id = self.id

        name = self.name

        units = self.units

        automatically_accrues = self.automatically_accrues

        is_private = self.is_private

        exclude_from_termination_payout = self.exclude_from_termination_payout

        external_id = self.external_id

        source = self.source

        is_balance_untracked = self.is_balance_untracked

        deduct_from_primary_pay_category = self.deduct_from_primary_pay_category

        deduct_from_pay_category_id = self.deduct_from_pay_category_id

        transfer_to_pay_category_id = self.transfer_to_pay_category_id

        hide_accruals_on_payslip = self.hide_accruals_on_payslip

        use_deduct_from_pay_category_rate = self.use_deduct_from_pay_category_rate

        is_name_private = self.is_name_private

        leave_unit_type: Union[Unset, str] = UNSET
        if not isinstance(self.leave_unit_type, Unset):
            leave_unit_type = self.leave_unit_type.value

        payout_as_etp = self.payout_as_etp

        accrues_first_pay_run_per_period_only = self.accrues_first_pay_run_per_period_only

        prevent_negative_balance_unpaid_leave_category_id = self.prevent_negative_balance_unpaid_leave_category_id

        leave_entitlement: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.leave_entitlement, Unset):
            leave_entitlement = self.leave_entitlement.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if contingent_period is not UNSET:
            field_dict["contingentPeriod"] = contingent_period
        if entitlement_period is not UNSET:
            field_dict["entitlementPeriod"] = entitlement_period
        if leave_loading is not UNSET:
            field_dict["leaveLoading"] = leave_loading
        if unit_type is not UNSET:
            field_dict["unitType"] = unit_type
        if leave_category_type is not UNSET:
            field_dict["leaveCategoryType"] = leave_category_type
        if leave_accrual_rule is not UNSET:
            field_dict["leaveAccrualRule"] = leave_accrual_rule
        if transfer_on_termination_to_pay_category_id is not UNSET:
            field_dict["transferOnTerminationToPayCategoryId"] = transfer_on_termination_to_pay_category_id
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if units is not UNSET:
            field_dict["units"] = units
        if automatically_accrues is not UNSET:
            field_dict["automaticallyAccrues"] = automatically_accrues
        if is_private is not UNSET:
            field_dict["isPrivate"] = is_private
        if exclude_from_termination_payout is not UNSET:
            field_dict["excludeFromTerminationPayout"] = exclude_from_termination_payout
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if source is not UNSET:
            field_dict["source"] = source
        if is_balance_untracked is not UNSET:
            field_dict["isBalanceUntracked"] = is_balance_untracked
        if deduct_from_primary_pay_category is not UNSET:
            field_dict["deductFromPrimaryPayCategory"] = deduct_from_primary_pay_category
        if deduct_from_pay_category_id is not UNSET:
            field_dict["deductFromPayCategoryId"] = deduct_from_pay_category_id
        if transfer_to_pay_category_id is not UNSET:
            field_dict["transferToPayCategoryId"] = transfer_to_pay_category_id
        if hide_accruals_on_payslip is not UNSET:
            field_dict["hideAccrualsOnPayslip"] = hide_accruals_on_payslip
        if use_deduct_from_pay_category_rate is not UNSET:
            field_dict["useDeductFromPayCategoryRate"] = use_deduct_from_pay_category_rate
        if is_name_private is not UNSET:
            field_dict["isNamePrivate"] = is_name_private
        if leave_unit_type is not UNSET:
            field_dict["leaveUnitType"] = leave_unit_type
        if payout_as_etp is not UNSET:
            field_dict["payoutAsETP"] = payout_as_etp
        if accrues_first_pay_run_per_period_only is not UNSET:
            field_dict["accruesFirstPayRunPerPeriodOnly"] = accrues_first_pay_run_per_period_only
        if prevent_negative_balance_unpaid_leave_category_id is not UNSET:
            field_dict["preventNegativeBalanceUnpaidLeaveCategoryId"] = (
                prevent_negative_balance_unpaid_leave_category_id
            )
        if leave_entitlement is not UNSET:
            field_dict["leaveEntitlement"] = leave_entitlement

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.au_leave_accrual_rule_model import AuLeaveAccrualRuleModel
        from ..models.leave_entitlement_model import LeaveEntitlementModel

        d = src_dict.copy()
        contingent_period = d.pop("contingentPeriod", UNSET)

        entitlement_period = d.pop("entitlementPeriod", UNSET)

        leave_loading = d.pop("leaveLoading", UNSET)

        _unit_type = d.pop("unitType", UNSET)
        unit_type: Union[Unset, AuLeaveCategoryModelLeaveAllowanceUnitEnum]
        if isinstance(_unit_type, Unset):
            unit_type = UNSET
        else:
            unit_type = AuLeaveCategoryModelLeaveAllowanceUnitEnum(_unit_type)

        _leave_category_type = d.pop("leaveCategoryType", UNSET)
        leave_category_type: Union[Unset, AuLeaveCategoryModelAuLeaveCategoryTypeEnum]
        if isinstance(_leave_category_type, Unset):
            leave_category_type = UNSET
        else:
            leave_category_type = AuLeaveCategoryModelAuLeaveCategoryTypeEnum(_leave_category_type)

        _leave_accrual_rule = d.pop("leaveAccrualRule", UNSET)
        leave_accrual_rule: Union[Unset, AuLeaveAccrualRuleModel]
        if isinstance(_leave_accrual_rule, Unset):
            leave_accrual_rule = UNSET
        else:
            leave_accrual_rule = AuLeaveAccrualRuleModel.from_dict(_leave_accrual_rule)

        transfer_on_termination_to_pay_category_id = d.pop("transferOnTerminationToPayCategoryId", UNSET)

        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        units = d.pop("units", UNSET)

        automatically_accrues = d.pop("automaticallyAccrues", UNSET)

        is_private = d.pop("isPrivate", UNSET)

        exclude_from_termination_payout = d.pop("excludeFromTerminationPayout", UNSET)

        external_id = d.pop("externalId", UNSET)

        source = d.pop("source", UNSET)

        is_balance_untracked = d.pop("isBalanceUntracked", UNSET)

        deduct_from_primary_pay_category = d.pop("deductFromPrimaryPayCategory", UNSET)

        deduct_from_pay_category_id = d.pop("deductFromPayCategoryId", UNSET)

        transfer_to_pay_category_id = d.pop("transferToPayCategoryId", UNSET)

        hide_accruals_on_payslip = d.pop("hideAccrualsOnPayslip", UNSET)

        use_deduct_from_pay_category_rate = d.pop("useDeductFromPayCategoryRate", UNSET)

        is_name_private = d.pop("isNamePrivate", UNSET)

        _leave_unit_type = d.pop("leaveUnitType", UNSET)
        leave_unit_type: Union[Unset, AuLeaveCategoryModelLeaveUnitTypeEnum]
        if isinstance(_leave_unit_type, Unset):
            leave_unit_type = UNSET
        else:
            leave_unit_type = AuLeaveCategoryModelLeaveUnitTypeEnum(_leave_unit_type)

        payout_as_etp = d.pop("payoutAsETP", UNSET)

        accrues_first_pay_run_per_period_only = d.pop("accruesFirstPayRunPerPeriodOnly", UNSET)

        prevent_negative_balance_unpaid_leave_category_id = d.pop("preventNegativeBalanceUnpaidLeaveCategoryId", UNSET)

        _leave_entitlement = d.pop("leaveEntitlement", UNSET)
        leave_entitlement: Union[Unset, LeaveEntitlementModel]
        if isinstance(_leave_entitlement, Unset):
            leave_entitlement = UNSET
        else:
            leave_entitlement = LeaveEntitlementModel.from_dict(_leave_entitlement)

        au_leave_category_model = cls(
            contingent_period=contingent_period,
            entitlement_period=entitlement_period,
            leave_loading=leave_loading,
            unit_type=unit_type,
            leave_category_type=leave_category_type,
            leave_accrual_rule=leave_accrual_rule,
            transfer_on_termination_to_pay_category_id=transfer_on_termination_to_pay_category_id,
            id=id,
            name=name,
            units=units,
            automatically_accrues=automatically_accrues,
            is_private=is_private,
            exclude_from_termination_payout=exclude_from_termination_payout,
            external_id=external_id,
            source=source,
            is_balance_untracked=is_balance_untracked,
            deduct_from_primary_pay_category=deduct_from_primary_pay_category,
            deduct_from_pay_category_id=deduct_from_pay_category_id,
            transfer_to_pay_category_id=transfer_to_pay_category_id,
            hide_accruals_on_payslip=hide_accruals_on_payslip,
            use_deduct_from_pay_category_rate=use_deduct_from_pay_category_rate,
            is_name_private=is_name_private,
            leave_unit_type=leave_unit_type,
            payout_as_etp=payout_as_etp,
            accrues_first_pay_run_per_period_only=accrues_first_pay_run_per_period_only,
            prevent_negative_balance_unpaid_leave_category_id=prevent_negative_balance_unpaid_leave_category_id,
            leave_entitlement=leave_entitlement,
        )

        au_leave_category_model.additional_properties = d
        return au_leave_category_model

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
