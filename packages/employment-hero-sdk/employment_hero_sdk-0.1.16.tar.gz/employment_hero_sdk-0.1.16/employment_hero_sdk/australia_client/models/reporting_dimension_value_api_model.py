from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.reporting_dimension_value_api_model_external_service import ReportingDimensionValueApiModelExternalService
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.reporting_dimension_value_filter_api_model import ReportingDimensionValueFilterApiModel


T = TypeVar("T", bound="ReportingDimensionValueApiModel")


@_attrs_define
class ReportingDimensionValueApiModel:
    """
    Attributes:
        source (Union[Unset, ReportingDimensionValueApiModelExternalService]):
        external_id (Union[Unset, str]):
        all_employees (Union[Unset, bool]):
        specific_employees (Union[Unset, str]):
        filter_combination_strategy (Union[Unset, str]):
        filters (Union[Unset, List['ReportingDimensionValueFilterApiModel']]):
        id (Union[Unset, int]):
        name (Union[Unset, str]):
        reporting_dimension_id (Union[Unset, int]):
    """

    source: Union[Unset, ReportingDimensionValueApiModelExternalService] = UNSET
    external_id: Union[Unset, str] = UNSET
    all_employees: Union[Unset, bool] = UNSET
    specific_employees: Union[Unset, str] = UNSET
    filter_combination_strategy: Union[Unset, str] = UNSET
    filters: Union[Unset, List["ReportingDimensionValueFilterApiModel"]] = UNSET
    id: Union[Unset, int] = UNSET
    name: Union[Unset, str] = UNSET
    reporting_dimension_id: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        source: Union[Unset, str] = UNSET
        if not isinstance(self.source, Unset):
            source = self.source.value

        external_id = self.external_id

        all_employees = self.all_employees

        specific_employees = self.specific_employees

        filter_combination_strategy = self.filter_combination_strategy

        filters: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.filters, Unset):
            filters = []
            for filters_item_data in self.filters:
                filters_item = filters_item_data.to_dict()
                filters.append(filters_item)

        id = self.id

        name = self.name

        reporting_dimension_id = self.reporting_dimension_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if source is not UNSET:
            field_dict["source"] = source
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if all_employees is not UNSET:
            field_dict["allEmployees"] = all_employees
        if specific_employees is not UNSET:
            field_dict["specificEmployees"] = specific_employees
        if filter_combination_strategy is not UNSET:
            field_dict["filterCombinationStrategy"] = filter_combination_strategy
        if filters is not UNSET:
            field_dict["filters"] = filters
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if reporting_dimension_id is not UNSET:
            field_dict["reportingDimensionId"] = reporting_dimension_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.reporting_dimension_value_filter_api_model import ReportingDimensionValueFilterApiModel

        d = src_dict.copy()
        _source = d.pop("source", UNSET)
        source: Union[Unset, ReportingDimensionValueApiModelExternalService]
        if isinstance(_source, Unset):
            source = UNSET
        else:
            source = ReportingDimensionValueApiModelExternalService(_source)

        external_id = d.pop("externalId", UNSET)

        all_employees = d.pop("allEmployees", UNSET)

        specific_employees = d.pop("specificEmployees", UNSET)

        filter_combination_strategy = d.pop("filterCombinationStrategy", UNSET)

        filters = []
        _filters = d.pop("filters", UNSET)
        for filters_item_data in _filters or []:
            filters_item = ReportingDimensionValueFilterApiModel.from_dict(filters_item_data)

            filters.append(filters_item)

        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        reporting_dimension_id = d.pop("reportingDimensionId", UNSET)

        reporting_dimension_value_api_model = cls(
            source=source,
            external_id=external_id,
            all_employees=all_employees,
            specific_employees=specific_employees,
            filter_combination_strategy=filter_combination_strategy,
            filters=filters,
            id=id,
            name=name,
            reporting_dimension_id=reporting_dimension_id,
        )

        reporting_dimension_value_api_model.additional_properties = d
        return reporting_dimension_value_api_model

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
