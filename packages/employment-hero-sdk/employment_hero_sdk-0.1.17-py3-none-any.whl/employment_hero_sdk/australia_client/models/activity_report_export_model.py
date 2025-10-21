from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ActivityReportExportModel")


@_attrs_define
class ActivityReportExportModel:
    """
    Attributes:
        employee_id (Union[Unset, int]):
        location_id (Union[Unset, int]):
        location (Union[Unset, str]):
        first_name (Union[Unset, str]):
        surname (Union[Unset, str]):
        total_hours (Union[Unset, float]):
        gross_earnings (Union[Unset, float]):
        taxable_earnings (Union[Unset, float]):
        payg_withholding (Union[Unset, float]):
        super_contributions (Union[Unset, float]):
        employer_contributions (Union[Unset, float]):
        net_earnings (Union[Unset, float]):
    """

    employee_id: Union[Unset, int] = UNSET
    location_id: Union[Unset, int] = UNSET
    location: Union[Unset, str] = UNSET
    first_name: Union[Unset, str] = UNSET
    surname: Union[Unset, str] = UNSET
    total_hours: Union[Unset, float] = UNSET
    gross_earnings: Union[Unset, float] = UNSET
    taxable_earnings: Union[Unset, float] = UNSET
    payg_withholding: Union[Unset, float] = UNSET
    super_contributions: Union[Unset, float] = UNSET
    employer_contributions: Union[Unset, float] = UNSET
    net_earnings: Union[Unset, float] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        employee_id = self.employee_id

        location_id = self.location_id

        location = self.location

        first_name = self.first_name

        surname = self.surname

        total_hours = self.total_hours

        gross_earnings = self.gross_earnings

        taxable_earnings = self.taxable_earnings

        payg_withholding = self.payg_withholding

        super_contributions = self.super_contributions

        employer_contributions = self.employer_contributions

        net_earnings = self.net_earnings

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if location_id is not UNSET:
            field_dict["locationId"] = location_id
        if location is not UNSET:
            field_dict["location"] = location
        if first_name is not UNSET:
            field_dict["firstName"] = first_name
        if surname is not UNSET:
            field_dict["surname"] = surname
        if total_hours is not UNSET:
            field_dict["totalHours"] = total_hours
        if gross_earnings is not UNSET:
            field_dict["grossEarnings"] = gross_earnings
        if taxable_earnings is not UNSET:
            field_dict["taxableEarnings"] = taxable_earnings
        if payg_withholding is not UNSET:
            field_dict["paygWithholding"] = payg_withholding
        if super_contributions is not UNSET:
            field_dict["superContributions"] = super_contributions
        if employer_contributions is not UNSET:
            field_dict["employerContributions"] = employer_contributions
        if net_earnings is not UNSET:
            field_dict["netEarnings"] = net_earnings

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        employee_id = d.pop("employeeId", UNSET)

        location_id = d.pop("locationId", UNSET)

        location = d.pop("location", UNSET)

        first_name = d.pop("firstName", UNSET)

        surname = d.pop("surname", UNSET)

        total_hours = d.pop("totalHours", UNSET)

        gross_earnings = d.pop("grossEarnings", UNSET)

        taxable_earnings = d.pop("taxableEarnings", UNSET)

        payg_withholding = d.pop("paygWithholding", UNSET)

        super_contributions = d.pop("superContributions", UNSET)

        employer_contributions = d.pop("employerContributions", UNSET)

        net_earnings = d.pop("netEarnings", UNSET)

        activity_report_export_model = cls(
            employee_id=employee_id,
            location_id=location_id,
            location=location,
            first_name=first_name,
            surname=surname,
            total_hours=total_hours,
            gross_earnings=gross_earnings,
            taxable_earnings=taxable_earnings,
            payg_withholding=payg_withholding,
            super_contributions=super_contributions,
            employer_contributions=employer_contributions,
            net_earnings=net_earnings,
        )

        activity_report_export_model.additional_properties = d
        return activity_report_export_model

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
