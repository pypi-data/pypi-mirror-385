import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="EssPayslipModel")


@_attrs_define
class EssPayslipModel:
    """
    Attributes:
        id (Union[Unset, int]):
        employee_id (Union[Unset, int]):
        pay_schedule (Union[Unset, str]):
        date_paid (Union[Unset, datetime.datetime]):
        pay_period_start (Union[Unset, datetime.datetime]):
        pay_period_end (Union[Unset, datetime.datetime]):
        net_pay (Union[Unset, float]):
        payer_name (Union[Unset, str]):
        payer_abn (Union[Unset, str]):
        payer_business_number (Union[Unset, str]):
    """

    id: Union[Unset, int] = UNSET
    employee_id: Union[Unset, int] = UNSET
    pay_schedule: Union[Unset, str] = UNSET
    date_paid: Union[Unset, datetime.datetime] = UNSET
    pay_period_start: Union[Unset, datetime.datetime] = UNSET
    pay_period_end: Union[Unset, datetime.datetime] = UNSET
    net_pay: Union[Unset, float] = UNSET
    payer_name: Union[Unset, str] = UNSET
    payer_abn: Union[Unset, str] = UNSET
    payer_business_number: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        employee_id = self.employee_id

        pay_schedule = self.pay_schedule

        date_paid: Union[Unset, str] = UNSET
        if not isinstance(self.date_paid, Unset):
            date_paid = self.date_paid.isoformat()

        pay_period_start: Union[Unset, str] = UNSET
        if not isinstance(self.pay_period_start, Unset):
            pay_period_start = self.pay_period_start.isoformat()

        pay_period_end: Union[Unset, str] = UNSET
        if not isinstance(self.pay_period_end, Unset):
            pay_period_end = self.pay_period_end.isoformat()

        net_pay = self.net_pay

        payer_name = self.payer_name

        payer_abn = self.payer_abn

        payer_business_number = self.payer_business_number

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if pay_schedule is not UNSET:
            field_dict["paySchedule"] = pay_schedule
        if date_paid is not UNSET:
            field_dict["datePaid"] = date_paid
        if pay_period_start is not UNSET:
            field_dict["payPeriodStart"] = pay_period_start
        if pay_period_end is not UNSET:
            field_dict["payPeriodEnd"] = pay_period_end
        if net_pay is not UNSET:
            field_dict["netPay"] = net_pay
        if payer_name is not UNSET:
            field_dict["payerName"] = payer_name
        if payer_abn is not UNSET:
            field_dict["payerAbn"] = payer_abn
        if payer_business_number is not UNSET:
            field_dict["payerBusinessNumber"] = payer_business_number

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        employee_id = d.pop("employeeId", UNSET)

        pay_schedule = d.pop("paySchedule", UNSET)

        _date_paid = d.pop("datePaid", UNSET)
        date_paid: Union[Unset, datetime.datetime]
        if isinstance(_date_paid, Unset):
            date_paid = UNSET
        else:
            date_paid = isoparse(_date_paid)

        _pay_period_start = d.pop("payPeriodStart", UNSET)
        pay_period_start: Union[Unset, datetime.datetime]
        if isinstance(_pay_period_start, Unset):
            pay_period_start = UNSET
        else:
            pay_period_start = isoparse(_pay_period_start)

        _pay_period_end = d.pop("payPeriodEnd", UNSET)
        pay_period_end: Union[Unset, datetime.datetime]
        if isinstance(_pay_period_end, Unset):
            pay_period_end = UNSET
        else:
            pay_period_end = isoparse(_pay_period_end)

        net_pay = d.pop("netPay", UNSET)

        payer_name = d.pop("payerName", UNSET)

        payer_abn = d.pop("payerAbn", UNSET)

        payer_business_number = d.pop("payerBusinessNumber", UNSET)

        ess_payslip_model = cls(
            id=id,
            employee_id=employee_id,
            pay_schedule=pay_schedule,
            date_paid=date_paid,
            pay_period_start=pay_period_start,
            pay_period_end=pay_period_end,
            net_pay=net_pay,
            payer_name=payer_name,
            payer_abn=payer_abn,
            payer_business_number=payer_business_number,
        )

        ess_payslip_model.additional_properties = d
        return ess_payslip_model

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
