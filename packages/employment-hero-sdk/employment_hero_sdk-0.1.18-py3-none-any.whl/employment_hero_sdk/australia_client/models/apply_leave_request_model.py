import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="ApplyLeaveRequestModel")


@_attrs_define
class ApplyLeaveRequestModel:
    """
    Attributes:
        pay_run_total_id (Union[Unset, int]):
        leave_request_id (Union[Unset, int]):
        units (Union[Unset, float]):
        error_message (Union[Unset, str]):
        from_date (Union[Unset, datetime.datetime]):
        to_date (Union[Unset, datetime.datetime]):
    """

    pay_run_total_id: Union[Unset, int] = UNSET
    leave_request_id: Union[Unset, int] = UNSET
    units: Union[Unset, float] = UNSET
    error_message: Union[Unset, str] = UNSET
    from_date: Union[Unset, datetime.datetime] = UNSET
    to_date: Union[Unset, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        pay_run_total_id = self.pay_run_total_id

        leave_request_id = self.leave_request_id

        units = self.units

        error_message = self.error_message

        from_date: Union[Unset, str] = UNSET
        if not isinstance(self.from_date, Unset):
            from_date = self.from_date.isoformat()

        to_date: Union[Unset, str] = UNSET
        if not isinstance(self.to_date, Unset):
            to_date = self.to_date.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if pay_run_total_id is not UNSET:
            field_dict["payRunTotalId"] = pay_run_total_id
        if leave_request_id is not UNSET:
            field_dict["leaveRequestId"] = leave_request_id
        if units is not UNSET:
            field_dict["units"] = units
        if error_message is not UNSET:
            field_dict["errorMessage"] = error_message
        if from_date is not UNSET:
            field_dict["fromDate"] = from_date
        if to_date is not UNSET:
            field_dict["toDate"] = to_date

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        pay_run_total_id = d.pop("payRunTotalId", UNSET)

        leave_request_id = d.pop("leaveRequestId", UNSET)

        units = d.pop("units", UNSET)

        error_message = d.pop("errorMessage", UNSET)

        _from_date = d.pop("fromDate", UNSET)
        from_date: Union[Unset, datetime.datetime]
        if isinstance(_from_date, Unset):
            from_date = UNSET
        else:
            from_date = isoparse(_from_date)

        _to_date = d.pop("toDate", UNSET)
        to_date: Union[Unset, datetime.datetime]
        if isinstance(_to_date, Unset):
            to_date = UNSET
        else:
            to_date = isoparse(_to_date)

        apply_leave_request_model = cls(
            pay_run_total_id=pay_run_total_id,
            leave_request_id=leave_request_id,
            units=units,
            error_message=error_message,
            from_date=from_date,
            to_date=to_date,
        )

        apply_leave_request_model.additional_properties = d
        return apply_leave_request_model

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
