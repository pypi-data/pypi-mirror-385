from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.au_work_type_model_au_employment_type_enum import AuWorkTypeModelAuEmploymentTypeEnum
from ..models.au_work_type_model_nullable_work_type_mapping_type import AuWorkTypeModelNullableWorkTypeMappingType
from ..types import UNSET, Unset

T = TypeVar("T", bound="AuWorkTypeModel")


@_attrs_define
class AuWorkTypeModel:
    """
    Attributes:
        employment_types (Union[Unset, List[AuWorkTypeModelAuEmploymentTypeEnum]]):
        award_package_id (Union[Unset, int]):
        award_package_name (Union[Unset, str]):
        id (Union[Unset, int]):
        name (Union[Unset, str]):
        pay_category_id (Union[Unset, int]):
        leave_category_id (Union[Unset, int]):
        external_id (Union[Unset, str]):
        source (Union[Unset, str]):
        accrues_leave (Union[Unset, bool]):
        mapping_type (Union[Unset, AuWorkTypeModelNullableWorkTypeMappingType]):
        short_code (Union[Unset, str]):
    """

    employment_types: Union[Unset, List[AuWorkTypeModelAuEmploymentTypeEnum]] = UNSET
    award_package_id: Union[Unset, int] = UNSET
    award_package_name: Union[Unset, str] = UNSET
    id: Union[Unset, int] = UNSET
    name: Union[Unset, str] = UNSET
    pay_category_id: Union[Unset, int] = UNSET
    leave_category_id: Union[Unset, int] = UNSET
    external_id: Union[Unset, str] = UNSET
    source: Union[Unset, str] = UNSET
    accrues_leave: Union[Unset, bool] = UNSET
    mapping_type: Union[Unset, AuWorkTypeModelNullableWorkTypeMappingType] = UNSET
    short_code: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        employment_types: Union[Unset, List[str]] = UNSET
        if not isinstance(self.employment_types, Unset):
            employment_types = []
            for employment_types_item_data in self.employment_types:
                employment_types_item = employment_types_item_data.value
                employment_types.append(employment_types_item)

        award_package_id = self.award_package_id

        award_package_name = self.award_package_name

        id = self.id

        name = self.name

        pay_category_id = self.pay_category_id

        leave_category_id = self.leave_category_id

        external_id = self.external_id

        source = self.source

        accrues_leave = self.accrues_leave

        mapping_type: Union[Unset, str] = UNSET
        if not isinstance(self.mapping_type, Unset):
            mapping_type = self.mapping_type.value

        short_code = self.short_code

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if employment_types is not UNSET:
            field_dict["employmentTypes"] = employment_types
        if award_package_id is not UNSET:
            field_dict["awardPackageId"] = award_package_id
        if award_package_name is not UNSET:
            field_dict["awardPackageName"] = award_package_name
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if pay_category_id is not UNSET:
            field_dict["payCategoryId"] = pay_category_id
        if leave_category_id is not UNSET:
            field_dict["leaveCategoryId"] = leave_category_id
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if source is not UNSET:
            field_dict["source"] = source
        if accrues_leave is not UNSET:
            field_dict["accruesLeave"] = accrues_leave
        if mapping_type is not UNSET:
            field_dict["mappingType"] = mapping_type
        if short_code is not UNSET:
            field_dict["shortCode"] = short_code

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        employment_types = []
        _employment_types = d.pop("employmentTypes", UNSET)
        for employment_types_item_data in _employment_types or []:
            employment_types_item = AuWorkTypeModelAuEmploymentTypeEnum(employment_types_item_data)

            employment_types.append(employment_types_item)

        award_package_id = d.pop("awardPackageId", UNSET)

        award_package_name = d.pop("awardPackageName", UNSET)

        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        pay_category_id = d.pop("payCategoryId", UNSET)

        leave_category_id = d.pop("leaveCategoryId", UNSET)

        external_id = d.pop("externalId", UNSET)

        source = d.pop("source", UNSET)

        accrues_leave = d.pop("accruesLeave", UNSET)

        _mapping_type = d.pop("mappingType", UNSET)
        mapping_type: Union[Unset, AuWorkTypeModelNullableWorkTypeMappingType]
        if isinstance(_mapping_type, Unset):
            mapping_type = UNSET
        else:
            mapping_type = AuWorkTypeModelNullableWorkTypeMappingType(_mapping_type)

        short_code = d.pop("shortCode", UNSET)

        au_work_type_model = cls(
            employment_types=employment_types,
            award_package_id=award_package_id,
            award_package_name=award_package_name,
            id=id,
            name=name,
            pay_category_id=pay_category_id,
            leave_category_id=leave_category_id,
            external_id=external_id,
            source=source,
            accrues_leave=accrues_leave,
            mapping_type=mapping_type,
            short_code=short_code,
        )

        au_work_type_model.additional_properties = d
        return au_work_type_model

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
