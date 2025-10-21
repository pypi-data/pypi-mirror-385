from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.leave_accrual_response_dictionary_string_list_1 import LeaveAccrualResponseDictionaryStringList1


T = TypeVar("T", bound="LeaveAccrualResponse")


@_attrs_define
class LeaveAccrualResponse:
    """
    Attributes:
        pay_run_id (Union[Unset, int]):
        leave (Union[Unset, LeaveAccrualResponseDictionaryStringList1]):
    """

    pay_run_id: Union[Unset, int] = UNSET
    leave: Union[Unset, "LeaveAccrualResponseDictionaryStringList1"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        pay_run_id = self.pay_run_id

        leave: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.leave, Unset):
            leave = self.leave.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if pay_run_id is not UNSET:
            field_dict["payRunId"] = pay_run_id
        if leave is not UNSET:
            field_dict["leave"] = leave

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.leave_accrual_response_dictionary_string_list_1 import LeaveAccrualResponseDictionaryStringList1

        d = src_dict.copy()
        pay_run_id = d.pop("payRunId", UNSET)

        _leave = d.pop("leave", UNSET)
        leave: Union[Unset, LeaveAccrualResponseDictionaryStringList1]
        if isinstance(_leave, Unset):
            leave = UNSET
        else:
            leave = LeaveAccrualResponseDictionaryStringList1.from_dict(_leave)

        leave_accrual_response = cls(
            pay_run_id=pay_run_id,
            leave=leave,
        )

        leave_accrual_response.additional_properties = d
        return leave_accrual_response

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
