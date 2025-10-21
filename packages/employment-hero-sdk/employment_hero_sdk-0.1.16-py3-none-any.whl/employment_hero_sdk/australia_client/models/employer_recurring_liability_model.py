import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.employer_recurring_liability_model_employer_recurring_liability_type_enum import (
    EmployerRecurringLiabilityModelEmployerRecurringLiabilityTypeEnum,
)
from ..models.employer_recurring_liability_model_external_service import EmployerRecurringLiabilityModelExternalService
from ..types import UNSET, Unset

T = TypeVar("T", bound="EmployerRecurringLiabilityModel")


@_attrs_define
class EmployerRecurringLiabilityModel:
    """
    Attributes:
        employer_liability_category_name (Union[Unset, str]):
        employer_liability_category_id (Union[Unset, int]):
        liability_type (Union[Unset, EmployerRecurringLiabilityModelEmployerRecurringLiabilityTypeEnum]):
        external_reference_id (Union[Unset, str]):
        source (Union[Unset, EmployerRecurringLiabilityModelExternalService]):
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

    employer_liability_category_name: Union[Unset, str] = UNSET
    employer_liability_category_id: Union[Unset, int] = UNSET
    liability_type: Union[Unset, EmployerRecurringLiabilityModelEmployerRecurringLiabilityTypeEnum] = UNSET
    external_reference_id: Union[Unset, str] = UNSET
    source: Union[Unset, EmployerRecurringLiabilityModelExternalService] = UNSET
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
        employer_liability_category_name = self.employer_liability_category_name

        employer_liability_category_id = self.employer_liability_category_id

        liability_type: Union[Unset, str] = UNSET
        if not isinstance(self.liability_type, Unset):
            liability_type = self.liability_type.value

        external_reference_id = self.external_reference_id

        source: Union[Unset, str] = UNSET
        if not isinstance(self.source, Unset):
            source = self.source.value

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
        if employer_liability_category_name is not UNSET:
            field_dict["employerLiabilityCategoryName"] = employer_liability_category_name
        if employer_liability_category_id is not UNSET:
            field_dict["employerLiabilityCategoryId"] = employer_liability_category_id
        if liability_type is not UNSET:
            field_dict["liabilityType"] = liability_type
        if external_reference_id is not UNSET:
            field_dict["externalReferenceId"] = external_reference_id
        if source is not UNSET:
            field_dict["source"] = source
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
        employer_liability_category_name = d.pop("employerLiabilityCategoryName", UNSET)

        employer_liability_category_id = d.pop("employerLiabilityCategoryId", UNSET)

        _liability_type = d.pop("liabilityType", UNSET)
        liability_type: Union[Unset, EmployerRecurringLiabilityModelEmployerRecurringLiabilityTypeEnum]
        if isinstance(_liability_type, Unset):
            liability_type = UNSET
        else:
            liability_type = EmployerRecurringLiabilityModelEmployerRecurringLiabilityTypeEnum(_liability_type)

        external_reference_id = d.pop("externalReferenceId", UNSET)

        _source = d.pop("source", UNSET)
        source: Union[Unset, EmployerRecurringLiabilityModelExternalService]
        if isinstance(_source, Unset):
            source = UNSET
        else:
            source = EmployerRecurringLiabilityModelExternalService(_source)

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

        employer_recurring_liability_model = cls(
            employer_liability_category_name=employer_liability_category_name,
            employer_liability_category_id=employer_liability_category_id,
            liability_type=liability_type,
            external_reference_id=external_reference_id,
            source=source,
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

        employer_recurring_liability_model.additional_properties = d
        return employer_recurring_liability_model

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
