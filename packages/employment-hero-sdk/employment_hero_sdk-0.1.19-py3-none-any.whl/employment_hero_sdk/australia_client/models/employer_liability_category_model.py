from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="EmployerLiabilityCategoryModel")


@_attrs_define
class EmployerLiabilityCategoryModel:
    """
    Attributes:
        id (Union[Unset, int]):
        name (Union[Unset, str]):
        external_reference_id (Union[Unset, str]):
        can_be_deleted (Union[Unset, bool]):
        hide_from_pay_slips (Union[Unset, bool]):
        show_total_payments (Union[Unset, bool]):
        include_in_shift_costs (Union[Unset, bool]):
        is_superannuation_fund (Union[Unset, bool]):
    """

    id: Union[Unset, int] = UNSET
    name: Union[Unset, str] = UNSET
    external_reference_id: Union[Unset, str] = UNSET
    can_be_deleted: Union[Unset, bool] = UNSET
    hide_from_pay_slips: Union[Unset, bool] = UNSET
    show_total_payments: Union[Unset, bool] = UNSET
    include_in_shift_costs: Union[Unset, bool] = UNSET
    is_superannuation_fund: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        name = self.name

        external_reference_id = self.external_reference_id

        can_be_deleted = self.can_be_deleted

        hide_from_pay_slips = self.hide_from_pay_slips

        show_total_payments = self.show_total_payments

        include_in_shift_costs = self.include_in_shift_costs

        is_superannuation_fund = self.is_superannuation_fund

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if external_reference_id is not UNSET:
            field_dict["externalReferenceId"] = external_reference_id
        if can_be_deleted is not UNSET:
            field_dict["canBeDeleted"] = can_be_deleted
        if hide_from_pay_slips is not UNSET:
            field_dict["hideFromPaySlips"] = hide_from_pay_slips
        if show_total_payments is not UNSET:
            field_dict["showTotalPayments"] = show_total_payments
        if include_in_shift_costs is not UNSET:
            field_dict["includeInShiftCosts"] = include_in_shift_costs
        if is_superannuation_fund is not UNSET:
            field_dict["isSuperannuationFund"] = is_superannuation_fund

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        external_reference_id = d.pop("externalReferenceId", UNSET)

        can_be_deleted = d.pop("canBeDeleted", UNSET)

        hide_from_pay_slips = d.pop("hideFromPaySlips", UNSET)

        show_total_payments = d.pop("showTotalPayments", UNSET)

        include_in_shift_costs = d.pop("includeInShiftCosts", UNSET)

        is_superannuation_fund = d.pop("isSuperannuationFund", UNSET)

        employer_liability_category_model = cls(
            id=id,
            name=name,
            external_reference_id=external_reference_id,
            can_be_deleted=can_be_deleted,
            hide_from_pay_slips=hide_from_pay_slips,
            show_total_payments=show_total_payments,
            include_in_shift_costs=include_in_shift_costs,
            is_superannuation_fund=is_superannuation_fund,
        )

        employer_liability_category_model.additional_properties = d
        return employer_liability_category_model

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
