from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SuperContributionsReportExportModel")


@_attrs_define
class SuperContributionsReportExportModel:
    """
    Attributes:
        location_name (Union[Unset, str]):
        employee_id (Union[Unset, int]):
        first_name (Union[Unset, str]):
        surname (Union[Unset, str]):
        external_id (Union[Unset, str]):
        super_fund_name (Union[Unset, str]):
        super_fund_number (Union[Unset, str]):
        payment_type (Union[Unset, str]):
        amount (Union[Unset, float]):
    """

    location_name: Union[Unset, str] = UNSET
    employee_id: Union[Unset, int] = UNSET
    first_name: Union[Unset, str] = UNSET
    surname: Union[Unset, str] = UNSET
    external_id: Union[Unset, str] = UNSET
    super_fund_name: Union[Unset, str] = UNSET
    super_fund_number: Union[Unset, str] = UNSET
    payment_type: Union[Unset, str] = UNSET
    amount: Union[Unset, float] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        location_name = self.location_name

        employee_id = self.employee_id

        first_name = self.first_name

        surname = self.surname

        external_id = self.external_id

        super_fund_name = self.super_fund_name

        super_fund_number = self.super_fund_number

        payment_type = self.payment_type

        amount = self.amount

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if location_name is not UNSET:
            field_dict["locationName"] = location_name
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if first_name is not UNSET:
            field_dict["firstName"] = first_name
        if surname is not UNSET:
            field_dict["surname"] = surname
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if super_fund_name is not UNSET:
            field_dict["superFundName"] = super_fund_name
        if super_fund_number is not UNSET:
            field_dict["superFundNumber"] = super_fund_number
        if payment_type is not UNSET:
            field_dict["paymentType"] = payment_type
        if amount is not UNSET:
            field_dict["amount"] = amount

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        location_name = d.pop("locationName", UNSET)

        employee_id = d.pop("employeeId", UNSET)

        first_name = d.pop("firstName", UNSET)

        surname = d.pop("surname", UNSET)

        external_id = d.pop("externalId", UNSET)

        super_fund_name = d.pop("superFundName", UNSET)

        super_fund_number = d.pop("superFundNumber", UNSET)

        payment_type = d.pop("paymentType", UNSET)

        amount = d.pop("amount", UNSET)

        super_contributions_report_export_model = cls(
            location_name=location_name,
            employee_id=employee_id,
            first_name=first_name,
            surname=surname,
            external_id=external_id,
            super_fund_name=super_fund_name,
            super_fund_number=super_fund_number,
            payment_type=payment_type,
            amount=amount,
        )

        super_contributions_report_export_model.additional_properties = d
        return super_contributions_report_export_model

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
