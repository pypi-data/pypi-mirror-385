from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.au_submit_pay_run_earnings_line_request_id_type import AuSubmitPayRunEarningsLineRequestIdType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.au_submit_pay_run_earnings_line_request_dictionary_string_list_1 import (
        AuSubmitPayRunEarningsLineRequestDictionaryStringList1,
    )


T = TypeVar("T", bound="AuSubmitPayRunEarningsLineRequest")


@_attrs_define
class AuSubmitPayRunEarningsLineRequest:
    """
    Attributes:
        earnings_lines (Union[Unset, AuSubmitPayRunEarningsLineRequestDictionaryStringList1]):
        location_id_type (Union[Unset, AuSubmitPayRunEarningsLineRequestIdType]):
        pay_category_id_type (Union[Unset, AuSubmitPayRunEarningsLineRequestIdType]):
        pay_run_id (Union[Unset, int]):
        employee_id_type (Union[Unset, AuSubmitPayRunEarningsLineRequestIdType]):
        replace_existing (Union[Unset, bool]):
        suppress_calculations (Union[Unset, bool]):
    """

    earnings_lines: Union[Unset, "AuSubmitPayRunEarningsLineRequestDictionaryStringList1"] = UNSET
    location_id_type: Union[Unset, AuSubmitPayRunEarningsLineRequestIdType] = UNSET
    pay_category_id_type: Union[Unset, AuSubmitPayRunEarningsLineRequestIdType] = UNSET
    pay_run_id: Union[Unset, int] = UNSET
    employee_id_type: Union[Unset, AuSubmitPayRunEarningsLineRequestIdType] = UNSET
    replace_existing: Union[Unset, bool] = UNSET
    suppress_calculations: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        earnings_lines: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.earnings_lines, Unset):
            earnings_lines = self.earnings_lines.to_dict()

        location_id_type: Union[Unset, str] = UNSET
        if not isinstance(self.location_id_type, Unset):
            location_id_type = self.location_id_type.value

        pay_category_id_type: Union[Unset, str] = UNSET
        if not isinstance(self.pay_category_id_type, Unset):
            pay_category_id_type = self.pay_category_id_type.value

        pay_run_id = self.pay_run_id

        employee_id_type: Union[Unset, str] = UNSET
        if not isinstance(self.employee_id_type, Unset):
            employee_id_type = self.employee_id_type.value

        replace_existing = self.replace_existing

        suppress_calculations = self.suppress_calculations

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if earnings_lines is not UNSET:
            field_dict["earningsLines"] = earnings_lines
        if location_id_type is not UNSET:
            field_dict["locationIdType"] = location_id_type
        if pay_category_id_type is not UNSET:
            field_dict["payCategoryIdType"] = pay_category_id_type
        if pay_run_id is not UNSET:
            field_dict["payRunId"] = pay_run_id
        if employee_id_type is not UNSET:
            field_dict["employeeIdType"] = employee_id_type
        if replace_existing is not UNSET:
            field_dict["replaceExisting"] = replace_existing
        if suppress_calculations is not UNSET:
            field_dict["suppressCalculations"] = suppress_calculations

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.au_submit_pay_run_earnings_line_request_dictionary_string_list_1 import (
            AuSubmitPayRunEarningsLineRequestDictionaryStringList1,
        )

        d = src_dict.copy()
        _earnings_lines = d.pop("earningsLines", UNSET)
        earnings_lines: Union[Unset, AuSubmitPayRunEarningsLineRequestDictionaryStringList1]
        if isinstance(_earnings_lines, Unset):
            earnings_lines = UNSET
        else:
            earnings_lines = AuSubmitPayRunEarningsLineRequestDictionaryStringList1.from_dict(_earnings_lines)

        _location_id_type = d.pop("locationIdType", UNSET)
        location_id_type: Union[Unset, AuSubmitPayRunEarningsLineRequestIdType]
        if isinstance(_location_id_type, Unset):
            location_id_type = UNSET
        else:
            location_id_type = AuSubmitPayRunEarningsLineRequestIdType(_location_id_type)

        _pay_category_id_type = d.pop("payCategoryIdType", UNSET)
        pay_category_id_type: Union[Unset, AuSubmitPayRunEarningsLineRequestIdType]
        if isinstance(_pay_category_id_type, Unset):
            pay_category_id_type = UNSET
        else:
            pay_category_id_type = AuSubmitPayRunEarningsLineRequestIdType(_pay_category_id_type)

        pay_run_id = d.pop("payRunId", UNSET)

        _employee_id_type = d.pop("employeeIdType", UNSET)
        employee_id_type: Union[Unset, AuSubmitPayRunEarningsLineRequestIdType]
        if isinstance(_employee_id_type, Unset):
            employee_id_type = UNSET
        else:
            employee_id_type = AuSubmitPayRunEarningsLineRequestIdType(_employee_id_type)

        replace_existing = d.pop("replaceExisting", UNSET)

        suppress_calculations = d.pop("suppressCalculations", UNSET)

        au_submit_pay_run_earnings_line_request = cls(
            earnings_lines=earnings_lines,
            location_id_type=location_id_type,
            pay_category_id_type=pay_category_id_type,
            pay_run_id=pay_run_id,
            employee_id_type=employee_id_type,
            replace_existing=replace_existing,
            suppress_calculations=suppress_calculations,
        )

        au_submit_pay_run_earnings_line_request.additional_properties = d
        return au_submit_pay_run_earnings_line_request

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
