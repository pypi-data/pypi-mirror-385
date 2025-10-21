from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkersCompReportGridModel")


@_attrs_define
class WorkersCompReportGridModel:
    """
    Attributes:
        employing_entity_id (Union[Unset, int]):
        employing_entity (Union[Unset, str]):
        pay_category_id (Union[Unset, int]):
        earnings_reporting (Union[Unset, float]):
        super_contribution_reporting (Union[Unset, float]):
        location_id (Union[Unset, int]):
        location_name (Union[Unset, str]):
        reporting_location_id (Union[Unset, int]):
        reporting_location_name (Union[Unset, str]):
    """

    employing_entity_id: Union[Unset, int] = UNSET
    employing_entity: Union[Unset, str] = UNSET
    pay_category_id: Union[Unset, int] = UNSET
    earnings_reporting: Union[Unset, float] = UNSET
    super_contribution_reporting: Union[Unset, float] = UNSET
    location_id: Union[Unset, int] = UNSET
    location_name: Union[Unset, str] = UNSET
    reporting_location_id: Union[Unset, int] = UNSET
    reporting_location_name: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        employing_entity_id = self.employing_entity_id

        employing_entity = self.employing_entity

        pay_category_id = self.pay_category_id

        earnings_reporting = self.earnings_reporting

        super_contribution_reporting = self.super_contribution_reporting

        location_id = self.location_id

        location_name = self.location_name

        reporting_location_id = self.reporting_location_id

        reporting_location_name = self.reporting_location_name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if employing_entity_id is not UNSET:
            field_dict["employingEntityId"] = employing_entity_id
        if employing_entity is not UNSET:
            field_dict["employingEntity"] = employing_entity
        if pay_category_id is not UNSET:
            field_dict["payCategoryId"] = pay_category_id
        if earnings_reporting is not UNSET:
            field_dict["earningsReporting"] = earnings_reporting
        if super_contribution_reporting is not UNSET:
            field_dict["superContributionReporting"] = super_contribution_reporting
        if location_id is not UNSET:
            field_dict["locationId"] = location_id
        if location_name is not UNSET:
            field_dict["locationName"] = location_name
        if reporting_location_id is not UNSET:
            field_dict["reportingLocationId"] = reporting_location_id
        if reporting_location_name is not UNSET:
            field_dict["reportingLocationName"] = reporting_location_name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        employing_entity_id = d.pop("employingEntityId", UNSET)

        employing_entity = d.pop("employingEntity", UNSET)

        pay_category_id = d.pop("payCategoryId", UNSET)

        earnings_reporting = d.pop("earningsReporting", UNSET)

        super_contribution_reporting = d.pop("superContributionReporting", UNSET)

        location_id = d.pop("locationId", UNSET)

        location_name = d.pop("locationName", UNSET)

        reporting_location_id = d.pop("reportingLocationId", UNSET)

        reporting_location_name = d.pop("reportingLocationName", UNSET)

        workers_comp_report_grid_model = cls(
            employing_entity_id=employing_entity_id,
            employing_entity=employing_entity,
            pay_category_id=pay_category_id,
            earnings_reporting=earnings_reporting,
            super_contribution_reporting=super_contribution_reporting,
            location_id=location_id,
            location_name=location_name,
            reporting_location_id=reporting_location_id,
            reporting_location_name=reporting_location_name,
        )

        workers_comp_report_grid_model.additional_properties = d
        return workers_comp_report_grid_model

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
