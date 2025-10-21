from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.shift_costings_response_shift_model import ShiftCostingsResponseShiftModel


T = TypeVar("T", bound="ShiftCostingsResponseModel")


@_attrs_define
class ShiftCostingsResponseModel:
    """
    Attributes:
        transaction_id (Union[Unset, str]):  Example: 00000000-0000-0000-0000-000000000000.
        transaction_external_id (Union[Unset, str]):
        employment_agreement_id (Union[Unset, int]):
        employment_agreement_name (Union[Unset, str]):
        pay_condition_rule_set_id (Union[Unset, int]):
        pay_condition_rule_set_name (Union[Unset, str]):
        shifts (Union[Unset, List['ShiftCostingsResponseShiftModel']]):
    """

    transaction_id: Union[Unset, str] = UNSET
    transaction_external_id: Union[Unset, str] = UNSET
    employment_agreement_id: Union[Unset, int] = UNSET
    employment_agreement_name: Union[Unset, str] = UNSET
    pay_condition_rule_set_id: Union[Unset, int] = UNSET
    pay_condition_rule_set_name: Union[Unset, str] = UNSET
    shifts: Union[Unset, List["ShiftCostingsResponseShiftModel"]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        transaction_id = self.transaction_id

        transaction_external_id = self.transaction_external_id

        employment_agreement_id = self.employment_agreement_id

        employment_agreement_name = self.employment_agreement_name

        pay_condition_rule_set_id = self.pay_condition_rule_set_id

        pay_condition_rule_set_name = self.pay_condition_rule_set_name

        shifts: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.shifts, Unset):
            shifts = []
            for shifts_item_data in self.shifts:
                shifts_item = shifts_item_data.to_dict()
                shifts.append(shifts_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if transaction_id is not UNSET:
            field_dict["transactionId"] = transaction_id
        if transaction_external_id is not UNSET:
            field_dict["transactionExternalId"] = transaction_external_id
        if employment_agreement_id is not UNSET:
            field_dict["employmentAgreementId"] = employment_agreement_id
        if employment_agreement_name is not UNSET:
            field_dict["employmentAgreementName"] = employment_agreement_name
        if pay_condition_rule_set_id is not UNSET:
            field_dict["payConditionRuleSetId"] = pay_condition_rule_set_id
        if pay_condition_rule_set_name is not UNSET:
            field_dict["payConditionRuleSetName"] = pay_condition_rule_set_name
        if shifts is not UNSET:
            field_dict["shifts"] = shifts

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.shift_costings_response_shift_model import ShiftCostingsResponseShiftModel

        d = src_dict.copy()
        transaction_id = d.pop("transactionId", UNSET)

        transaction_external_id = d.pop("transactionExternalId", UNSET)

        employment_agreement_id = d.pop("employmentAgreementId", UNSET)

        employment_agreement_name = d.pop("employmentAgreementName", UNSET)

        pay_condition_rule_set_id = d.pop("payConditionRuleSetId", UNSET)

        pay_condition_rule_set_name = d.pop("payConditionRuleSetName", UNSET)

        shifts = []
        _shifts = d.pop("shifts", UNSET)
        for shifts_item_data in _shifts or []:
            shifts_item = ShiftCostingsResponseShiftModel.from_dict(shifts_item_data)

            shifts.append(shifts_item)

        shift_costings_response_model = cls(
            transaction_id=transaction_id,
            transaction_external_id=transaction_external_id,
            employment_agreement_id=employment_agreement_id,
            employment_agreement_name=employment_agreement_name,
            pay_condition_rule_set_id=pay_condition_rule_set_id,
            pay_condition_rule_set_name=pay_condition_rule_set_name,
            shifts=shifts,
        )

        shift_costings_response_model.additional_properties = d
        return shift_costings_response_model

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
