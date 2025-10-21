from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.au_ess_work_type_model import AuEssWorkTypeModel
    from ..models.classification_select_model import ClassificationSelectModel
    from ..models.location_model import LocationModel
    from ..models.reporting_dimension_value_select_model import ReportingDimensionValueSelectModel


T = TypeVar("T", bound="AuTimesheetReferenceData")


@_attrs_define
class AuTimesheetReferenceData:
    """
    Attributes:
        classifications (Union[Unset, List['ClassificationSelectModel']]):
        work_types (Union[Unset, List['AuEssWorkTypeModel']]):
        shift_conditions (Union[Unset, List['AuEssWorkTypeModel']]):
        locations (Union[Unset, List['LocationModel']]):
        dimension_values (Union[Unset, List['ReportingDimensionValueSelectModel']]):
    """

    classifications: Union[Unset, List["ClassificationSelectModel"]] = UNSET
    work_types: Union[Unset, List["AuEssWorkTypeModel"]] = UNSET
    shift_conditions: Union[Unset, List["AuEssWorkTypeModel"]] = UNSET
    locations: Union[Unset, List["LocationModel"]] = UNSET
    dimension_values: Union[Unset, List["ReportingDimensionValueSelectModel"]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        classifications: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.classifications, Unset):
            classifications = []
            for classifications_item_data in self.classifications:
                classifications_item = classifications_item_data.to_dict()
                classifications.append(classifications_item)

        work_types: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.work_types, Unset):
            work_types = []
            for work_types_item_data in self.work_types:
                work_types_item = work_types_item_data.to_dict()
                work_types.append(work_types_item)

        shift_conditions: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.shift_conditions, Unset):
            shift_conditions = []
            for shift_conditions_item_data in self.shift_conditions:
                shift_conditions_item = shift_conditions_item_data.to_dict()
                shift_conditions.append(shift_conditions_item)

        locations: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.locations, Unset):
            locations = []
            for locations_item_data in self.locations:
                locations_item = locations_item_data.to_dict()
                locations.append(locations_item)

        dimension_values: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.dimension_values, Unset):
            dimension_values = []
            for dimension_values_item_data in self.dimension_values:
                dimension_values_item = dimension_values_item_data.to_dict()
                dimension_values.append(dimension_values_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if classifications is not UNSET:
            field_dict["classifications"] = classifications
        if work_types is not UNSET:
            field_dict["workTypes"] = work_types
        if shift_conditions is not UNSET:
            field_dict["shiftConditions"] = shift_conditions
        if locations is not UNSET:
            field_dict["locations"] = locations
        if dimension_values is not UNSET:
            field_dict["dimensionValues"] = dimension_values

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.au_ess_work_type_model import AuEssWorkTypeModel
        from ..models.classification_select_model import ClassificationSelectModel
        from ..models.location_model import LocationModel
        from ..models.reporting_dimension_value_select_model import ReportingDimensionValueSelectModel

        d = src_dict.copy()
        classifications = []
        _classifications = d.pop("classifications", UNSET)
        for classifications_item_data in _classifications or []:
            classifications_item = ClassificationSelectModel.from_dict(classifications_item_data)

            classifications.append(classifications_item)

        work_types = []
        _work_types = d.pop("workTypes", UNSET)
        for work_types_item_data in _work_types or []:
            work_types_item = AuEssWorkTypeModel.from_dict(work_types_item_data)

            work_types.append(work_types_item)

        shift_conditions = []
        _shift_conditions = d.pop("shiftConditions", UNSET)
        for shift_conditions_item_data in _shift_conditions or []:
            shift_conditions_item = AuEssWorkTypeModel.from_dict(shift_conditions_item_data)

            shift_conditions.append(shift_conditions_item)

        locations = []
        _locations = d.pop("locations", UNSET)
        for locations_item_data in _locations or []:
            locations_item = LocationModel.from_dict(locations_item_data)

            locations.append(locations_item)

        dimension_values = []
        _dimension_values = d.pop("dimensionValues", UNSET)
        for dimension_values_item_data in _dimension_values or []:
            dimension_values_item = ReportingDimensionValueSelectModel.from_dict(dimension_values_item_data)

            dimension_values.append(dimension_values_item)

        au_timesheet_reference_data = cls(
            classifications=classifications,
            work_types=work_types,
            shift_conditions=shift_conditions,
            locations=locations,
            dimension_values=dimension_values,
        )

        au_timesheet_reference_data.additional_properties = d
        return au_timesheet_reference_data

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
