from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="EmployerLiabilityModel")


@_attrs_define
class EmployerLiabilityModel:
    """
    Attributes:
        employer_liability_category_id (Union[Unset, str]):
        employer_liability_category_name (Union[Unset, str]):
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

    employer_liability_category_id: Union[Unset, str] = UNSET
    employer_liability_category_name: Union[Unset, str] = UNSET
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
        employer_liability_category_id = self.employer_liability_category_id

        employer_liability_category_name = self.employer_liability_category_name

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
        if employer_liability_category_id is not UNSET:
            field_dict["employerLiabilityCategoryId"] = employer_liability_category_id
        if employer_liability_category_name is not UNSET:
            field_dict["employerLiabilityCategoryName"] = employer_liability_category_name
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
        employer_liability_category_id = d.pop("employerLiabilityCategoryId", UNSET)

        employer_liability_category_name = d.pop("employerLiabilityCategoryName", UNSET)

        notes = d.pop("notes", UNSET)

        amount = d.pop("amount", UNSET)

        id = d.pop("id", UNSET)

        external_id = d.pop("externalId", UNSET)

        location_id = d.pop("locationId", UNSET)

        location_name = d.pop("locationName", UNSET)

        employee_id = d.pop("employeeId", UNSET)

        employee_name = d.pop("employeeName", UNSET)

        employee_external_id = d.pop("employeeExternalId", UNSET)

        employer_liability_model = cls(
            employer_liability_category_id=employer_liability_category_id,
            employer_liability_category_name=employer_liability_category_name,
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

        employer_liability_model.additional_properties = d
        return employer_liability_model

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
