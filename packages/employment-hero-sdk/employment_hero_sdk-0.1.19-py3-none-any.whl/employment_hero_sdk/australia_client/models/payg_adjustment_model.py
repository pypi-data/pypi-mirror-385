from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PaygAdjustmentModel")


@_attrs_define
class PaygAdjustmentModel:
    """
    Attributes:
        notes (Union[Unset, str]):
        amount (Union[Unset, float]):
        id (Union[Unset, int]):
        external_id (Union[Unset, str]):
        location_id (Union[Unset, str]):
        location_name (Union[Unset, str]):
        employee_id (Union[Unset, str]):
        employee_name (Union[Unset, str]):
        employee_external_id (Union[Unset, str]):
    """

    notes: Union[Unset, str] = UNSET
    amount: Union[Unset, float] = UNSET
    id: Union[Unset, int] = UNSET
    external_id: Union[Unset, str] = UNSET
    location_id: Union[Unset, str] = UNSET
    location_name: Union[Unset, str] = UNSET
    employee_id: Union[Unset, str] = UNSET
    employee_name: Union[Unset, str] = UNSET
    employee_external_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        notes = self.notes

        amount = self.amount

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
        if notes is not UNSET:
            field_dict["notes"] = notes
        if amount is not UNSET:
            field_dict["amount"] = amount
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
        notes = d.pop("notes", UNSET)

        amount = d.pop("amount", UNSET)

        id = d.pop("id", UNSET)

        external_id = d.pop("externalId", UNSET)

        location_id = d.pop("locationId", UNSET)

        location_name = d.pop("locationName", UNSET)

        employee_id = d.pop("employeeId", UNSET)

        employee_name = d.pop("employeeName", UNSET)

        employee_external_id = d.pop("employeeExternalId", UNSET)

        payg_adjustment_model = cls(
            notes=notes,
            amount=amount,
            id=id,
            external_id=external_id,
            location_id=location_id,
            location_name=location_name,
            employee_id=employee_id,
            employee_name=employee_name,
            employee_external_id=employee_external_id,
        )

        payg_adjustment_model.additional_properties = d
        return payg_adjustment_model

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
