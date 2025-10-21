from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.ess_work_type_model_employment_type_enum import EssWorkTypeModelEmploymentTypeEnum
from ..models.ess_work_type_model_nullable_work_type_mapping_type import EssWorkTypeModelNullableWorkTypeMappingType
from ..types import UNSET, Unset

T = TypeVar("T", bound="EssWorkTypeModel")


@_attrs_define
class EssWorkTypeModel:
    """
    Attributes:
        is_unit_based_work_type (Union[Unset, bool]):
        unit_type (Union[Unset, str]):
        id (Union[Unset, int]):
        name (Union[Unset, str]):
        pay_category_id (Union[Unset, int]):
        pay_category_name (Union[Unset, str]):
        leave_category_id (Union[Unset, int]):
        external_id (Union[Unset, str]):
        source (Union[Unset, str]):
        accrues_leave (Union[Unset, bool]):
        employment_types (Union[Unset, List[EssWorkTypeModelEmploymentTypeEnum]]):
        mapping_type (Union[Unset, EssWorkTypeModelNullableWorkTypeMappingType]):
        short_code (Union[Unset, str]):
        award_package_id (Union[Unset, int]):
        award_package_name (Union[Unset, str]):
    """

    is_unit_based_work_type: Union[Unset, bool] = UNSET
    unit_type: Union[Unset, str] = UNSET
    id: Union[Unset, int] = UNSET
    name: Union[Unset, str] = UNSET
    pay_category_id: Union[Unset, int] = UNSET
    pay_category_name: Union[Unset, str] = UNSET
    leave_category_id: Union[Unset, int] = UNSET
    external_id: Union[Unset, str] = UNSET
    source: Union[Unset, str] = UNSET
    accrues_leave: Union[Unset, bool] = UNSET
    employment_types: Union[Unset, List[EssWorkTypeModelEmploymentTypeEnum]] = UNSET
    mapping_type: Union[Unset, EssWorkTypeModelNullableWorkTypeMappingType] = UNSET
    short_code: Union[Unset, str] = UNSET
    award_package_id: Union[Unset, int] = UNSET
    award_package_name: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        is_unit_based_work_type = self.is_unit_based_work_type

        unit_type = self.unit_type

        id = self.id

        name = self.name

        pay_category_id = self.pay_category_id

        pay_category_name = self.pay_category_name

        leave_category_id = self.leave_category_id

        external_id = self.external_id

        source = self.source

        accrues_leave = self.accrues_leave

        employment_types: Union[Unset, List[str]] = UNSET
        if not isinstance(self.employment_types, Unset):
            employment_types = []
            for employment_types_item_data in self.employment_types:
                employment_types_item = employment_types_item_data.value
                employment_types.append(employment_types_item)

        mapping_type: Union[Unset, str] = UNSET
        if not isinstance(self.mapping_type, Unset):
            mapping_type = self.mapping_type.value

        short_code = self.short_code

        award_package_id = self.award_package_id

        award_package_name = self.award_package_name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if is_unit_based_work_type is not UNSET:
            field_dict["isUnitBasedWorkType"] = is_unit_based_work_type
        if unit_type is not UNSET:
            field_dict["unitType"] = unit_type
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if pay_category_id is not UNSET:
            field_dict["payCategoryId"] = pay_category_id
        if pay_category_name is not UNSET:
            field_dict["payCategoryName"] = pay_category_name
        if leave_category_id is not UNSET:
            field_dict["leaveCategoryId"] = leave_category_id
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if source is not UNSET:
            field_dict["source"] = source
        if accrues_leave is not UNSET:
            field_dict["accruesLeave"] = accrues_leave
        if employment_types is not UNSET:
            field_dict["employmentTypes"] = employment_types
        if mapping_type is not UNSET:
            field_dict["mappingType"] = mapping_type
        if short_code is not UNSET:
            field_dict["shortCode"] = short_code
        if award_package_id is not UNSET:
            field_dict["awardPackageId"] = award_package_id
        if award_package_name is not UNSET:
            field_dict["awardPackageName"] = award_package_name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        is_unit_based_work_type = d.pop("isUnitBasedWorkType", UNSET)

        unit_type = d.pop("unitType", UNSET)

        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        pay_category_id = d.pop("payCategoryId", UNSET)

        pay_category_name = d.pop("payCategoryName", UNSET)

        leave_category_id = d.pop("leaveCategoryId", UNSET)

        external_id = d.pop("externalId", UNSET)

        source = d.pop("source", UNSET)

        accrues_leave = d.pop("accruesLeave", UNSET)

        employment_types = []
        _employment_types = d.pop("employmentTypes", UNSET)
        for employment_types_item_data in _employment_types or []:
            employment_types_item = EssWorkTypeModelEmploymentTypeEnum(employment_types_item_data)

            employment_types.append(employment_types_item)

        _mapping_type = d.pop("mappingType", UNSET)
        mapping_type: Union[Unset, EssWorkTypeModelNullableWorkTypeMappingType]
        if isinstance(_mapping_type, Unset):
            mapping_type = UNSET
        else:
            mapping_type = EssWorkTypeModelNullableWorkTypeMappingType(_mapping_type)

        short_code = d.pop("shortCode", UNSET)

        award_package_id = d.pop("awardPackageId", UNSET)

        award_package_name = d.pop("awardPackageName", UNSET)

        ess_work_type_model = cls(
            is_unit_based_work_type=is_unit_based_work_type,
            unit_type=unit_type,
            id=id,
            name=name,
            pay_category_id=pay_category_id,
            pay_category_name=pay_category_name,
            leave_category_id=leave_category_id,
            external_id=external_id,
            source=source,
            accrues_leave=accrues_leave,
            employment_types=employment_types,
            mapping_type=mapping_type,
            short_code=short_code,
            award_package_id=award_package_id,
            award_package_name=award_package_name,
        )

        ess_work_type_model.additional_properties = d
        return ess_work_type_model

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
