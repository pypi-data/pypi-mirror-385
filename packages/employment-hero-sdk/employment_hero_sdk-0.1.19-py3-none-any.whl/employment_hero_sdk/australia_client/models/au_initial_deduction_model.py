from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AuInitialDeductionModel")


@_attrs_define
class AuInitialDeductionModel:
    """
    Attributes:
        is_resc (Union[Unset, bool]):
        tax_exempt (Union[Unset, bool]):
        is_member_voluntary (Union[Unset, bool]):
        is_resc_status_read_only (Union[Unset, bool]):
        deduction_category_id (Union[Unset, int]):
        name (Union[Unset, str]):
        amount (Union[Unset, float]):
    """

    is_resc: Union[Unset, bool] = UNSET
    tax_exempt: Union[Unset, bool] = UNSET
    is_member_voluntary: Union[Unset, bool] = UNSET
    is_resc_status_read_only: Union[Unset, bool] = UNSET
    deduction_category_id: Union[Unset, int] = UNSET
    name: Union[Unset, str] = UNSET
    amount: Union[Unset, float] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        is_resc = self.is_resc

        tax_exempt = self.tax_exempt

        is_member_voluntary = self.is_member_voluntary

        is_resc_status_read_only = self.is_resc_status_read_only

        deduction_category_id = self.deduction_category_id

        name = self.name

        amount = self.amount

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if is_resc is not UNSET:
            field_dict["isRESC"] = is_resc
        if tax_exempt is not UNSET:
            field_dict["taxExempt"] = tax_exempt
        if is_member_voluntary is not UNSET:
            field_dict["isMemberVoluntary"] = is_member_voluntary
        if is_resc_status_read_only is not UNSET:
            field_dict["isRescStatusReadOnly"] = is_resc_status_read_only
        if deduction_category_id is not UNSET:
            field_dict["deductionCategoryId"] = deduction_category_id
        if name is not UNSET:
            field_dict["name"] = name
        if amount is not UNSET:
            field_dict["amount"] = amount

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        is_resc = d.pop("isRESC", UNSET)

        tax_exempt = d.pop("taxExempt", UNSET)

        is_member_voluntary = d.pop("isMemberVoluntary", UNSET)

        is_resc_status_read_only = d.pop("isRescStatusReadOnly", UNSET)

        deduction_category_id = d.pop("deductionCategoryId", UNSET)

        name = d.pop("name", UNSET)

        amount = d.pop("amount", UNSET)

        au_initial_deduction_model = cls(
            is_resc=is_resc,
            tax_exempt=tax_exempt,
            is_member_voluntary=is_member_voluntary,
            is_resc_status_read_only=is_resc_status_read_only,
            deduction_category_id=deduction_category_id,
            name=name,
            amount=amount,
        )

        au_initial_deduction_model.additional_properties = d
        return au_initial_deduction_model

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
