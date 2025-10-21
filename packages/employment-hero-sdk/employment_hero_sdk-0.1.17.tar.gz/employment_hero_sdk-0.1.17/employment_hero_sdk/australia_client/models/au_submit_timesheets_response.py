from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.au_submit_timesheets_response_i_dictionary_string_i_list_1 import (
        AuSubmitTimesheetsResponseIDictionaryStringIList1,
    )


T = TypeVar("T", bound="AuSubmitTimesheetsResponse")


@_attrs_define
class AuSubmitTimesheetsResponse:
    """
    Attributes:
        timesheets (Union[Unset, AuSubmitTimesheetsResponseIDictionaryStringIList1]):
    """

    timesheets: Union[Unset, "AuSubmitTimesheetsResponseIDictionaryStringIList1"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        timesheets: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.timesheets, Unset):
            timesheets = self.timesheets.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if timesheets is not UNSET:
            field_dict["timesheets"] = timesheets

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.au_submit_timesheets_response_i_dictionary_string_i_list_1 import (
            AuSubmitTimesheetsResponseIDictionaryStringIList1,
        )

        d = src_dict.copy()
        _timesheets = d.pop("timesheets", UNSET)
        timesheets: Union[Unset, AuSubmitTimesheetsResponseIDictionaryStringIList1]
        if isinstance(_timesheets, Unset):
            timesheets = UNSET
        else:
            timesheets = AuSubmitTimesheetsResponseIDictionaryStringIList1.from_dict(_timesheets)

        au_submit_timesheets_response = cls(
            timesheets=timesheets,
        )

        au_submit_timesheets_response.additional_properties = d
        return au_submit_timesheets_response

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
