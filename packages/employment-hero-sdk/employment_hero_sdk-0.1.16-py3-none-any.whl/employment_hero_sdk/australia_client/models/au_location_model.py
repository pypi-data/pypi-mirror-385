from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AuLocationModel")


@_attrs_define
class AuLocationModel:
    """
    Attributes:
        country (Union[Unset, str]):
        id (Union[Unset, int]):
        parent_id (Union[Unset, int]):
        name (Union[Unset, str]):
        external_id (Union[Unset, str]):
        external_accounting_location_id (Union[Unset, str]):
        source (Union[Unset, str]):
        fully_qualified_name (Union[Unset, str]):
        is_global (Union[Unset, bool]):
        is_rollup_reporting_location (Union[Unset, bool]):
        general_ledger_mapping_code (Union[Unset, str]):
        default_shift_condition_ids (Union[Unset, List[int]]):
        state (Union[Unset, str]):
    """

    country: Union[Unset, str] = UNSET
    id: Union[Unset, int] = UNSET
    parent_id: Union[Unset, int] = UNSET
    name: Union[Unset, str] = UNSET
    external_id: Union[Unset, str] = UNSET
    external_accounting_location_id: Union[Unset, str] = UNSET
    source: Union[Unset, str] = UNSET
    fully_qualified_name: Union[Unset, str] = UNSET
    is_global: Union[Unset, bool] = UNSET
    is_rollup_reporting_location: Union[Unset, bool] = UNSET
    general_ledger_mapping_code: Union[Unset, str] = UNSET
    default_shift_condition_ids: Union[Unset, List[int]] = UNSET
    state: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        country = self.country

        id = self.id

        parent_id = self.parent_id

        name = self.name

        external_id = self.external_id

        external_accounting_location_id = self.external_accounting_location_id

        source = self.source

        fully_qualified_name = self.fully_qualified_name

        is_global = self.is_global

        is_rollup_reporting_location = self.is_rollup_reporting_location

        general_ledger_mapping_code = self.general_ledger_mapping_code

        default_shift_condition_ids: Union[Unset, List[int]] = UNSET
        if not isinstance(self.default_shift_condition_ids, Unset):
            default_shift_condition_ids = self.default_shift_condition_ids

        state = self.state

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if country is not UNSET:
            field_dict["country"] = country
        if id is not UNSET:
            field_dict["id"] = id
        if parent_id is not UNSET:
            field_dict["parentId"] = parent_id
        if name is not UNSET:
            field_dict["name"] = name
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if external_accounting_location_id is not UNSET:
            field_dict["externalAccountingLocationId"] = external_accounting_location_id
        if source is not UNSET:
            field_dict["source"] = source
        if fully_qualified_name is not UNSET:
            field_dict["fullyQualifiedName"] = fully_qualified_name
        if is_global is not UNSET:
            field_dict["isGlobal"] = is_global
        if is_rollup_reporting_location is not UNSET:
            field_dict["isRollupReportingLocation"] = is_rollup_reporting_location
        if general_ledger_mapping_code is not UNSET:
            field_dict["generalLedgerMappingCode"] = general_ledger_mapping_code
        if default_shift_condition_ids is not UNSET:
            field_dict["defaultShiftConditionIds"] = default_shift_condition_ids
        if state is not UNSET:
            field_dict["state"] = state

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        country = d.pop("country", UNSET)

        id = d.pop("id", UNSET)

        parent_id = d.pop("parentId", UNSET)

        name = d.pop("name", UNSET)

        external_id = d.pop("externalId", UNSET)

        external_accounting_location_id = d.pop("externalAccountingLocationId", UNSET)

        source = d.pop("source", UNSET)

        fully_qualified_name = d.pop("fullyQualifiedName", UNSET)

        is_global = d.pop("isGlobal", UNSET)

        is_rollup_reporting_location = d.pop("isRollupReportingLocation", UNSET)

        general_ledger_mapping_code = d.pop("generalLedgerMappingCode", UNSET)

        default_shift_condition_ids = cast(List[int], d.pop("defaultShiftConditionIds", UNSET))

        state = d.pop("state", UNSET)

        au_location_model = cls(
            country=country,
            id=id,
            parent_id=parent_id,
            name=name,
            external_id=external_id,
            external_accounting_location_id=external_accounting_location_id,
            source=source,
            fully_qualified_name=fully_qualified_name,
            is_global=is_global,
            is_rollup_reporting_location=is_rollup_reporting_location,
            general_ledger_mapping_code=general_ledger_mapping_code,
            default_shift_condition_ids=default_shift_condition_ids,
            state=state,
        )

        au_location_model.additional_properties = d
        return au_location_model

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
