from typing import Any, Dict, List, Type, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="AuJournalItemResponseIDictionaryStringIList1")


@_attrs_define
class AuJournalItemResponseIDictionaryStringIList1:
    """Nullable</p><p><i>Note:</i> Only applicable to businesses where the Dimensions feature is enabled.</p><p>Specify an
    object with dimension names and for each one, specify an array of associated value names (normally one-per
    dimension) eg { "Department": ["Accounting"], "Job Code": ["JC1"] }.</p><p>If you prefer to specify dimension values
    directly by Id, use the ReportingDimensionValueIds field instead.</p><p>If ReportingDimensionValueIds is used,
    ReportingDimensionValueNames will be ignored (the Ids take precedence)

    """

    additional_properties: Dict[str, List[str]] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        field_dict: Dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = prop

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        au_journal_item_response_i_dictionary_string_i_list_1 = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = cast(List[str], prop_dict)

            additional_properties[prop_name] = additional_property

        au_journal_item_response_i_dictionary_string_i_list_1.additional_properties = additional_properties
        return au_journal_item_response_i_dictionary_string_i_list_1

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> List[str]:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: List[str]) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
