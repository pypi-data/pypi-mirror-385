from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.apply_leave_request_model import ApplyLeaveRequestModel


T = TypeVar("T", bound="ApplyLeaveRequestResult")


@_attrs_define
class ApplyLeaveRequestResult:
    """
    Attributes:
        updated_pay_run_totals (Union[Unset, List[int]]):
        failed_leave_requests (Union[Unset, List['ApplyLeaveRequestModel']]):
    """

    updated_pay_run_totals: Union[Unset, List[int]] = UNSET
    failed_leave_requests: Union[Unset, List["ApplyLeaveRequestModel"]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        updated_pay_run_totals: Union[Unset, List[int]] = UNSET
        if not isinstance(self.updated_pay_run_totals, Unset):
            updated_pay_run_totals = self.updated_pay_run_totals

        failed_leave_requests: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.failed_leave_requests, Unset):
            failed_leave_requests = []
            for failed_leave_requests_item_data in self.failed_leave_requests:
                failed_leave_requests_item = failed_leave_requests_item_data.to_dict()
                failed_leave_requests.append(failed_leave_requests_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if updated_pay_run_totals is not UNSET:
            field_dict["updatedPayRunTotals"] = updated_pay_run_totals
        if failed_leave_requests is not UNSET:
            field_dict["failedLeaveRequests"] = failed_leave_requests

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.apply_leave_request_model import ApplyLeaveRequestModel

        d = src_dict.copy()
        updated_pay_run_totals = cast(List[int], d.pop("updatedPayRunTotals", UNSET))

        failed_leave_requests = []
        _failed_leave_requests = d.pop("failedLeaveRequests", UNSET)
        for failed_leave_requests_item_data in _failed_leave_requests or []:
            failed_leave_requests_item = ApplyLeaveRequestModel.from_dict(failed_leave_requests_item_data)

            failed_leave_requests.append(failed_leave_requests_item)

        apply_leave_request_result = cls(
            updated_pay_run_totals=updated_pay_run_totals,
            failed_leave_requests=failed_leave_requests,
        )

        apply_leave_request_result.additional_properties = d
        return apply_leave_request_result

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
