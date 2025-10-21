from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.reporting_dimension_value_base_api_model import ReportingDimensionValueBaseApiModel


T = TypeVar("T", bound="DimensionEarningsLineSplitApiModel")


@_attrs_define
class DimensionEarningsLineSplitApiModel:
    """
    Attributes:
        id (Union[Unset, int]):
        reporting_dimension_values (Union[Unset, List['ReportingDimensionValueBaseApiModel']]):
        allocated_percentage (Union[Unset, float]):
        allocate_balance (Union[Unset, bool]):
    """

    id: Union[Unset, int] = UNSET
    reporting_dimension_values: Union[Unset, List["ReportingDimensionValueBaseApiModel"]] = UNSET
    allocated_percentage: Union[Unset, float] = UNSET
    allocate_balance: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        reporting_dimension_values: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.reporting_dimension_values, Unset):
            reporting_dimension_values = []
            for reporting_dimension_values_item_data in self.reporting_dimension_values:
                reporting_dimension_values_item = reporting_dimension_values_item_data.to_dict()
                reporting_dimension_values.append(reporting_dimension_values_item)

        allocated_percentage = self.allocated_percentage

        allocate_balance = self.allocate_balance

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if reporting_dimension_values is not UNSET:
            field_dict["reportingDimensionValues"] = reporting_dimension_values
        if allocated_percentage is not UNSET:
            field_dict["allocatedPercentage"] = allocated_percentage
        if allocate_balance is not UNSET:
            field_dict["allocateBalance"] = allocate_balance

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.reporting_dimension_value_base_api_model import ReportingDimensionValueBaseApiModel

        d = src_dict.copy()
        id = d.pop("id", UNSET)

        reporting_dimension_values = []
        _reporting_dimension_values = d.pop("reportingDimensionValues", UNSET)
        for reporting_dimension_values_item_data in _reporting_dimension_values or []:
            reporting_dimension_values_item = ReportingDimensionValueBaseApiModel.from_dict(
                reporting_dimension_values_item_data
            )

            reporting_dimension_values.append(reporting_dimension_values_item)

        allocated_percentage = d.pop("allocatedPercentage", UNSET)

        allocate_balance = d.pop("allocateBalance", UNSET)

        dimension_earnings_line_split_api_model = cls(
            id=id,
            reporting_dimension_values=reporting_dimension_values,
            allocated_percentage=allocated_percentage,
            allocate_balance=allocate_balance,
        )

        dimension_earnings_line_split_api_model.additional_properties = d
        return dimension_earnings_line_split_api_model

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
