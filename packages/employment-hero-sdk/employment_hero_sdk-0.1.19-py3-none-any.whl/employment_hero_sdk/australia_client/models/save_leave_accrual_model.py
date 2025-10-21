from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.save_leave_accrual_model_save_leave_accrual_type_enum import SaveLeaveAccrualModelSaveLeaveAccrualTypeEnum
from ..types import UNSET, Unset

T = TypeVar("T", bound="SaveLeaveAccrualModel")


@_attrs_define
class SaveLeaveAccrualModel:
    """
    Attributes:
        accrual_type (Union[Unset, SaveLeaveAccrualModelSaveLeaveAccrualTypeEnum]):
        notes (Union[Unset, str]):
        amount (Union[Unset, float]):
        leave_category_id (Union[Unset, int]):
        apply_leave_loading (Union[Unset, bool]):
        adjust_earnings (Union[Unset, bool]):
        external_reference_id (Union[Unset, str]):
    """

    accrual_type: Union[Unset, SaveLeaveAccrualModelSaveLeaveAccrualTypeEnum] = UNSET
    notes: Union[Unset, str] = UNSET
    amount: Union[Unset, float] = UNSET
    leave_category_id: Union[Unset, int] = UNSET
    apply_leave_loading: Union[Unset, bool] = UNSET
    adjust_earnings: Union[Unset, bool] = UNSET
    external_reference_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        accrual_type: Union[Unset, str] = UNSET
        if not isinstance(self.accrual_type, Unset):
            accrual_type = self.accrual_type.value

        notes = self.notes

        amount = self.amount

        leave_category_id = self.leave_category_id

        apply_leave_loading = self.apply_leave_loading

        adjust_earnings = self.adjust_earnings

        external_reference_id = self.external_reference_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if accrual_type is not UNSET:
            field_dict["accrualType"] = accrual_type
        if notes is not UNSET:
            field_dict["notes"] = notes
        if amount is not UNSET:
            field_dict["amount"] = amount
        if leave_category_id is not UNSET:
            field_dict["leaveCategoryId"] = leave_category_id
        if apply_leave_loading is not UNSET:
            field_dict["applyLeaveLoading"] = apply_leave_loading
        if adjust_earnings is not UNSET:
            field_dict["adjustEarnings"] = adjust_earnings
        if external_reference_id is not UNSET:
            field_dict["externalReferenceId"] = external_reference_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _accrual_type = d.pop("accrualType", UNSET)
        accrual_type: Union[Unset, SaveLeaveAccrualModelSaveLeaveAccrualTypeEnum]
        if isinstance(_accrual_type, Unset):
            accrual_type = UNSET
        else:
            accrual_type = SaveLeaveAccrualModelSaveLeaveAccrualTypeEnum(_accrual_type)

        notes = d.pop("notes", UNSET)

        amount = d.pop("amount", UNSET)

        leave_category_id = d.pop("leaveCategoryId", UNSET)

        apply_leave_loading = d.pop("applyLeaveLoading", UNSET)

        adjust_earnings = d.pop("adjustEarnings", UNSET)

        external_reference_id = d.pop("externalReferenceId", UNSET)

        save_leave_accrual_model = cls(
            accrual_type=accrual_type,
            notes=notes,
            amount=amount,
            leave_category_id=leave_category_id,
            apply_leave_loading=apply_leave_loading,
            adjust_earnings=adjust_earnings,
            external_reference_id=external_reference_id,
        )

        save_leave_accrual_model.additional_properties = d
        return save_leave_accrual_model

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
