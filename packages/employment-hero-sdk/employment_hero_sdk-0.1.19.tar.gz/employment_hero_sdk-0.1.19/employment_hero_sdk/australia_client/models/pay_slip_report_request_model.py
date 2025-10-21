from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PaySlipReportRequestModel")


@_attrs_define
class PaySlipReportRequestModel:
    """
    Attributes:
        pay_run_id (Union[Unset, int]):
        employee_id (Union[Unset, int]):
        location_id (Union[Unset, int]):
        employing_entity_id (Union[Unset, int]):
    """

    pay_run_id: Union[Unset, int] = UNSET
    employee_id: Union[Unset, int] = UNSET
    location_id: Union[Unset, int] = UNSET
    employing_entity_id: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        pay_run_id = self.pay_run_id

        employee_id = self.employee_id

        location_id = self.location_id

        employing_entity_id = self.employing_entity_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if pay_run_id is not UNSET:
            field_dict["payRunId"] = pay_run_id
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if location_id is not UNSET:
            field_dict["locationId"] = location_id
        if employing_entity_id is not UNSET:
            field_dict["employingEntityId"] = employing_entity_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        pay_run_id = d.pop("payRunId", UNSET)

        employee_id = d.pop("employeeId", UNSET)

        location_id = d.pop("locationId", UNSET)

        employing_entity_id = d.pop("employingEntityId", UNSET)

        pay_slip_report_request_model = cls(
            pay_run_id=pay_run_id,
            employee_id=employee_id,
            location_id=location_id,
            employing_entity_id=employing_entity_id,
        )

        pay_slip_report_request_model.additional_properties = d
        return pay_slip_report_request_model

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
