import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.deductions_report_deduction_amount_model import DeductionsReportDeductionAmountModel


T = TypeVar("T", bound="DeductionsReportExportModel")


@_attrs_define
class DeductionsReportExportModel:
    """
    Attributes:
        pay_run (Union[Unset, str]):
        date_paid (Union[Unset, datetime.datetime]):
        employee_id (Union[Unset, int]):
        first_name (Union[Unset, str]):
        surname (Union[Unset, str]):
        external_id (Union[Unset, str]):
        location (Union[Unset, str]):
        amounts (Union[Unset, List['DeductionsReportDeductionAmountModel']]):
        note (Union[Unset, str]):
    """

    pay_run: Union[Unset, str] = UNSET
    date_paid: Union[Unset, datetime.datetime] = UNSET
    employee_id: Union[Unset, int] = UNSET
    first_name: Union[Unset, str] = UNSET
    surname: Union[Unset, str] = UNSET
    external_id: Union[Unset, str] = UNSET
    location: Union[Unset, str] = UNSET
    amounts: Union[Unset, List["DeductionsReportDeductionAmountModel"]] = UNSET
    note: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        pay_run = self.pay_run

        date_paid: Union[Unset, str] = UNSET
        if not isinstance(self.date_paid, Unset):
            date_paid = self.date_paid.isoformat()

        employee_id = self.employee_id

        first_name = self.first_name

        surname = self.surname

        external_id = self.external_id

        location = self.location

        amounts: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.amounts, Unset):
            amounts = []
            for amounts_item_data in self.amounts:
                amounts_item = amounts_item_data.to_dict()
                amounts.append(amounts_item)

        note = self.note

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if pay_run is not UNSET:
            field_dict["payRun"] = pay_run
        if date_paid is not UNSET:
            field_dict["datePaid"] = date_paid
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if first_name is not UNSET:
            field_dict["firstName"] = first_name
        if surname is not UNSET:
            field_dict["surname"] = surname
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if location is not UNSET:
            field_dict["location"] = location
        if amounts is not UNSET:
            field_dict["amounts"] = amounts
        if note is not UNSET:
            field_dict["note"] = note

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.deductions_report_deduction_amount_model import DeductionsReportDeductionAmountModel

        d = src_dict.copy()
        pay_run = d.pop("payRun", UNSET)

        _date_paid = d.pop("datePaid", UNSET)
        date_paid: Union[Unset, datetime.datetime]
        if isinstance(_date_paid, Unset):
            date_paid = UNSET
        else:
            date_paid = isoparse(_date_paid)

        employee_id = d.pop("employeeId", UNSET)

        first_name = d.pop("firstName", UNSET)

        surname = d.pop("surname", UNSET)

        external_id = d.pop("externalId", UNSET)

        location = d.pop("location", UNSET)

        amounts = []
        _amounts = d.pop("amounts", UNSET)
        for amounts_item_data in _amounts or []:
            amounts_item = DeductionsReportDeductionAmountModel.from_dict(amounts_item_data)

            amounts.append(amounts_item)

        note = d.pop("note", UNSET)

        deductions_report_export_model = cls(
            pay_run=pay_run,
            date_paid=date_paid,
            employee_id=employee_id,
            first_name=first_name,
            surname=surname,
            external_id=external_id,
            location=location,
            amounts=amounts,
            note=note,
        )

        deductions_report_export_model.additional_properties = d
        return deductions_report_export_model

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
