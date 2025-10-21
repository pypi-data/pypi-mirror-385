from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.au_detailed_employee_group_model_filter_combination_strategy_enum import (
    AuDetailedEmployeeGroupModelFilterCombinationStrategyEnum,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.au_employee_filter_model import AuEmployeeFilterModel
    from ..models.matching_employee_model import MatchingEmployeeModel


T = TypeVar("T", bound="AuDetailedEmployeeGroupModel")


@_attrs_define
class AuDetailedEmployeeGroupModel:
    """
    Attributes:
        matching_employees (Union[Unset, List['MatchingEmployeeModel']]):
        id (Union[Unset, int]):
        name (Union[Unset, str]):
        filter_combination_strategy (Union[Unset, AuDetailedEmployeeGroupModelFilterCombinationStrategyEnum]):
        filters (Union[Unset, List['AuEmployeeFilterModel']]):
    """

    matching_employees: Union[Unset, List["MatchingEmployeeModel"]] = UNSET
    id: Union[Unset, int] = UNSET
    name: Union[Unset, str] = UNSET
    filter_combination_strategy: Union[Unset, AuDetailedEmployeeGroupModelFilterCombinationStrategyEnum] = UNSET
    filters: Union[Unset, List["AuEmployeeFilterModel"]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        matching_employees: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.matching_employees, Unset):
            matching_employees = []
            for matching_employees_item_data in self.matching_employees:
                matching_employees_item = matching_employees_item_data.to_dict()
                matching_employees.append(matching_employees_item)

        id = self.id

        name = self.name

        filter_combination_strategy: Union[Unset, str] = UNSET
        if not isinstance(self.filter_combination_strategy, Unset):
            filter_combination_strategy = self.filter_combination_strategy.value

        filters: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.filters, Unset):
            filters = []
            for filters_item_data in self.filters:
                filters_item = filters_item_data.to_dict()
                filters.append(filters_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if matching_employees is not UNSET:
            field_dict["matchingEmployees"] = matching_employees
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if filter_combination_strategy is not UNSET:
            field_dict["filterCombinationStrategy"] = filter_combination_strategy
        if filters is not UNSET:
            field_dict["filters"] = filters

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.au_employee_filter_model import AuEmployeeFilterModel
        from ..models.matching_employee_model import MatchingEmployeeModel

        d = src_dict.copy()
        matching_employees = []
        _matching_employees = d.pop("matchingEmployees", UNSET)
        for matching_employees_item_data in _matching_employees or []:
            matching_employees_item = MatchingEmployeeModel.from_dict(matching_employees_item_data)

            matching_employees.append(matching_employees_item)

        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        _filter_combination_strategy = d.pop("filterCombinationStrategy", UNSET)
        filter_combination_strategy: Union[Unset, AuDetailedEmployeeGroupModelFilterCombinationStrategyEnum]
        if isinstance(_filter_combination_strategy, Unset):
            filter_combination_strategy = UNSET
        else:
            filter_combination_strategy = AuDetailedEmployeeGroupModelFilterCombinationStrategyEnum(
                _filter_combination_strategy
            )

        filters = []
        _filters = d.pop("filters", UNSET)
        for filters_item_data in _filters or []:
            filters_item = AuEmployeeFilterModel.from_dict(filters_item_data)

            filters.append(filters_item)

        au_detailed_employee_group_model = cls(
            matching_employees=matching_employees,
            id=id,
            name=name,
            filter_combination_strategy=filter_combination_strategy,
            filters=filters,
        )

        au_detailed_employee_group_model.additional_properties = d
        return au_detailed_employee_group_model

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
