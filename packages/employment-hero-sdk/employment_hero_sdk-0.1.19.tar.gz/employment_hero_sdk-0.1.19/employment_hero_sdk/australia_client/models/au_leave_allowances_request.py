from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.au_leave_allowances_request_id_type import AuLeaveAllowancesRequestIdType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.au_leave_allowances_request_dictionary_string_i_list_1 import (
        AuLeaveAllowancesRequestDictionaryStringIList1,
    )


T = TypeVar("T", bound="AuLeaveAllowancesRequest")


@_attrs_define
class AuLeaveAllowancesRequest:
    """
    Attributes:
        employee_id_type (Union[Unset, AuLeaveAllowancesRequestIdType]):
        leave_category_id_type (Union[Unset, AuLeaveAllowancesRequestIdType]):
        leave_allowances (Union[Unset, AuLeaveAllowancesRequestDictionaryStringIList1]):
    """

    employee_id_type: Union[Unset, AuLeaveAllowancesRequestIdType] = UNSET
    leave_category_id_type: Union[Unset, AuLeaveAllowancesRequestIdType] = UNSET
    leave_allowances: Union[Unset, "AuLeaveAllowancesRequestDictionaryStringIList1"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        employee_id_type: Union[Unset, str] = UNSET
        if not isinstance(self.employee_id_type, Unset):
            employee_id_type = self.employee_id_type.value

        leave_category_id_type: Union[Unset, str] = UNSET
        if not isinstance(self.leave_category_id_type, Unset):
            leave_category_id_type = self.leave_category_id_type.value

        leave_allowances: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.leave_allowances, Unset):
            leave_allowances = self.leave_allowances.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if employee_id_type is not UNSET:
            field_dict["employeeIdType"] = employee_id_type
        if leave_category_id_type is not UNSET:
            field_dict["leaveCategoryIdType"] = leave_category_id_type
        if leave_allowances is not UNSET:
            field_dict["leaveAllowances"] = leave_allowances

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.au_leave_allowances_request_dictionary_string_i_list_1 import (
            AuLeaveAllowancesRequestDictionaryStringIList1,
        )

        d = src_dict.copy()
        _employee_id_type = d.pop("employeeIdType", UNSET)
        employee_id_type: Union[Unset, AuLeaveAllowancesRequestIdType]
        if isinstance(_employee_id_type, Unset):
            employee_id_type = UNSET
        else:
            employee_id_type = AuLeaveAllowancesRequestIdType(_employee_id_type)

        _leave_category_id_type = d.pop("leaveCategoryIdType", UNSET)
        leave_category_id_type: Union[Unset, AuLeaveAllowancesRequestIdType]
        if isinstance(_leave_category_id_type, Unset):
            leave_category_id_type = UNSET
        else:
            leave_category_id_type = AuLeaveAllowancesRequestIdType(_leave_category_id_type)

        _leave_allowances = d.pop("leaveAllowances", UNSET)
        leave_allowances: Union[Unset, AuLeaveAllowancesRequestDictionaryStringIList1]
        if isinstance(_leave_allowances, Unset):
            leave_allowances = UNSET
        else:
            leave_allowances = AuLeaveAllowancesRequestDictionaryStringIList1.from_dict(_leave_allowances)

        au_leave_allowances_request = cls(
            employee_id_type=employee_id_type,
            leave_category_id_type=leave_category_id_type,
            leave_allowances=leave_allowances,
        )

        au_leave_allowances_request.additional_properties = d
        return au_leave_allowances_request

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
