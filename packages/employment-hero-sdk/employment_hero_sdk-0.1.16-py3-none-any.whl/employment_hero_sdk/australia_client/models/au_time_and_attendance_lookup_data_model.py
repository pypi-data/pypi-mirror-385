from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.classification_lookup_model import ClassificationLookupModel
    from ..models.location_select_model import LocationSelectModel
    from ..models.location_shift_conditions_model import LocationShiftConditionsModel
    from ..models.numeric_nullable_select_list_item import NumericNullableSelectListItem
    from ..models.reporting_dimension_value_select_model import ReportingDimensionValueSelectModel
    from ..models.shift_condition_select_model import ShiftConditionSelectModel
    from ..models.work_type_select_model import WorkTypeSelectModel


T = TypeVar("T", bound="AuTimeAndAttendanceLookupDataModel")


@_attrs_define
class AuTimeAndAttendanceLookupDataModel:
    """
    Attributes:
        locations (Union[Unset, List['LocationSelectModel']]):
        work_types (Union[Unset, List['WorkTypeSelectModel']]):
        classifications (Union[Unset, List['ClassificationLookupModel']]):
        default_location (Union[Unset, LocationSelectModel]):
        shift_conditions (Union[Unset, List['ShiftConditionSelectModel']]):
        location_shift_conditions (Union[Unset, List['LocationShiftConditionsModel']]):
        reporting_dimensions_enabled (Union[Unset, bool]):
        reporting_dimension_groups (Union[Unset, List['NumericNullableSelectListItem']]):
        reporting_dimension_values (Union[Unset, List['ReportingDimensionValueSelectModel']]):
    """

    locations: Union[Unset, List["LocationSelectModel"]] = UNSET
    work_types: Union[Unset, List["WorkTypeSelectModel"]] = UNSET
    classifications: Union[Unset, List["ClassificationLookupModel"]] = UNSET
    default_location: Union[Unset, "LocationSelectModel"] = UNSET
    shift_conditions: Union[Unset, List["ShiftConditionSelectModel"]] = UNSET
    location_shift_conditions: Union[Unset, List["LocationShiftConditionsModel"]] = UNSET
    reporting_dimensions_enabled: Union[Unset, bool] = UNSET
    reporting_dimension_groups: Union[Unset, List["NumericNullableSelectListItem"]] = UNSET
    reporting_dimension_values: Union[Unset, List["ReportingDimensionValueSelectModel"]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        locations: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.locations, Unset):
            locations = []
            for locations_item_data in self.locations:
                locations_item = locations_item_data.to_dict()
                locations.append(locations_item)

        work_types: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.work_types, Unset):
            work_types = []
            for work_types_item_data in self.work_types:
                work_types_item = work_types_item_data.to_dict()
                work_types.append(work_types_item)

        classifications: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.classifications, Unset):
            classifications = []
            for classifications_item_data in self.classifications:
                classifications_item = classifications_item_data.to_dict()
                classifications.append(classifications_item)

        default_location: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.default_location, Unset):
            default_location = self.default_location.to_dict()

        shift_conditions: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.shift_conditions, Unset):
            shift_conditions = []
            for shift_conditions_item_data in self.shift_conditions:
                shift_conditions_item = shift_conditions_item_data.to_dict()
                shift_conditions.append(shift_conditions_item)

        location_shift_conditions: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.location_shift_conditions, Unset):
            location_shift_conditions = []
            for location_shift_conditions_item_data in self.location_shift_conditions:
                location_shift_conditions_item = location_shift_conditions_item_data.to_dict()
                location_shift_conditions.append(location_shift_conditions_item)

        reporting_dimensions_enabled = self.reporting_dimensions_enabled

        reporting_dimension_groups: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.reporting_dimension_groups, Unset):
            reporting_dimension_groups = []
            for reporting_dimension_groups_item_data in self.reporting_dimension_groups:
                reporting_dimension_groups_item = reporting_dimension_groups_item_data.to_dict()
                reporting_dimension_groups.append(reporting_dimension_groups_item)

        reporting_dimension_values: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.reporting_dimension_values, Unset):
            reporting_dimension_values = []
            for reporting_dimension_values_item_data in self.reporting_dimension_values:
                reporting_dimension_values_item = reporting_dimension_values_item_data.to_dict()
                reporting_dimension_values.append(reporting_dimension_values_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if locations is not UNSET:
            field_dict["locations"] = locations
        if work_types is not UNSET:
            field_dict["workTypes"] = work_types
        if classifications is not UNSET:
            field_dict["classifications"] = classifications
        if default_location is not UNSET:
            field_dict["defaultLocation"] = default_location
        if shift_conditions is not UNSET:
            field_dict["shiftConditions"] = shift_conditions
        if location_shift_conditions is not UNSET:
            field_dict["locationShiftConditions"] = location_shift_conditions
        if reporting_dimensions_enabled is not UNSET:
            field_dict["reportingDimensionsEnabled"] = reporting_dimensions_enabled
        if reporting_dimension_groups is not UNSET:
            field_dict["reportingDimensionGroups"] = reporting_dimension_groups
        if reporting_dimension_values is not UNSET:
            field_dict["reportingDimensionValues"] = reporting_dimension_values

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.classification_lookup_model import ClassificationLookupModel
        from ..models.location_select_model import LocationSelectModel
        from ..models.location_shift_conditions_model import LocationShiftConditionsModel
        from ..models.numeric_nullable_select_list_item import NumericNullableSelectListItem
        from ..models.reporting_dimension_value_select_model import ReportingDimensionValueSelectModel
        from ..models.shift_condition_select_model import ShiftConditionSelectModel
        from ..models.work_type_select_model import WorkTypeSelectModel

        d = src_dict.copy()
        locations = []
        _locations = d.pop("locations", UNSET)
        for locations_item_data in _locations or []:
            locations_item = LocationSelectModel.from_dict(locations_item_data)

            locations.append(locations_item)

        work_types = []
        _work_types = d.pop("workTypes", UNSET)
        for work_types_item_data in _work_types or []:
            work_types_item = WorkTypeSelectModel.from_dict(work_types_item_data)

            work_types.append(work_types_item)

        classifications = []
        _classifications = d.pop("classifications", UNSET)
        for classifications_item_data in _classifications or []:
            classifications_item = ClassificationLookupModel.from_dict(classifications_item_data)

            classifications.append(classifications_item)

        _default_location = d.pop("defaultLocation", UNSET)
        default_location: Union[Unset, LocationSelectModel]
        if isinstance(_default_location, Unset):
            default_location = UNSET
        else:
            default_location = LocationSelectModel.from_dict(_default_location)

        shift_conditions = []
        _shift_conditions = d.pop("shiftConditions", UNSET)
        for shift_conditions_item_data in _shift_conditions or []:
            shift_conditions_item = ShiftConditionSelectModel.from_dict(shift_conditions_item_data)

            shift_conditions.append(shift_conditions_item)

        location_shift_conditions = []
        _location_shift_conditions = d.pop("locationShiftConditions", UNSET)
        for location_shift_conditions_item_data in _location_shift_conditions or []:
            location_shift_conditions_item = LocationShiftConditionsModel.from_dict(location_shift_conditions_item_data)

            location_shift_conditions.append(location_shift_conditions_item)

        reporting_dimensions_enabled = d.pop("reportingDimensionsEnabled", UNSET)

        reporting_dimension_groups = []
        _reporting_dimension_groups = d.pop("reportingDimensionGroups", UNSET)
        for reporting_dimension_groups_item_data in _reporting_dimension_groups or []:
            reporting_dimension_groups_item = NumericNullableSelectListItem.from_dict(
                reporting_dimension_groups_item_data
            )

            reporting_dimension_groups.append(reporting_dimension_groups_item)

        reporting_dimension_values = []
        _reporting_dimension_values = d.pop("reportingDimensionValues", UNSET)
        for reporting_dimension_values_item_data in _reporting_dimension_values or []:
            reporting_dimension_values_item = ReportingDimensionValueSelectModel.from_dict(
                reporting_dimension_values_item_data
            )

            reporting_dimension_values.append(reporting_dimension_values_item)

        au_time_and_attendance_lookup_data_model = cls(
            locations=locations,
            work_types=work_types,
            classifications=classifications,
            default_location=default_location,
            shift_conditions=shift_conditions,
            location_shift_conditions=location_shift_conditions,
            reporting_dimensions_enabled=reporting_dimensions_enabled,
            reporting_dimension_groups=reporting_dimension_groups,
            reporting_dimension_values=reporting_dimension_values,
        )

        au_time_and_attendance_lookup_data_model.additional_properties = d
        return au_time_and_attendance_lookup_data_model

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
