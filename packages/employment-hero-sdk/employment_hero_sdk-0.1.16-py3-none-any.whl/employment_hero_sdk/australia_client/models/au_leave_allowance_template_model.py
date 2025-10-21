import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.au_leave_allowance_template_model_external_service import AuLeaveAllowanceTemplateModelExternalService
from ..models.au_leave_allowance_template_model_nullable_leave_accrual_start_date_type import (
    AuLeaveAllowanceTemplateModelNullableLeaveAccrualStartDateType,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.au_leave_allowance_template_leave_category_api_model import (
        AuLeaveAllowanceTemplateLeaveCategoryApiModel,
    )


T = TypeVar("T", bound="AuLeaveAllowanceTemplateModel")


@_attrs_define
class AuLeaveAllowanceTemplateModel:
    """
    Attributes:
        leave_loading_calculated_from_pay_category_id (Union[Unset, int]):
        leave_categories (Union[Unset, List['AuLeaveAllowanceTemplateLeaveCategoryApiModel']]):
        award_id (Union[Unset, int]):
        award_name (Union[Unset, str]):
        id (Union[Unset, int]):
        name (Union[Unset, str]):
        external_id (Union[Unset, str]):
        source (Union[Unset, AuLeaveAllowanceTemplateModelExternalService]):
        leave_year_start (Union[Unset, datetime.datetime]):
        leave_accrual_start_date_type (Union[Unset, AuLeaveAllowanceTemplateModelNullableLeaveAccrualStartDateType]):
    """

    leave_loading_calculated_from_pay_category_id: Union[Unset, int] = UNSET
    leave_categories: Union[Unset, List["AuLeaveAllowanceTemplateLeaveCategoryApiModel"]] = UNSET
    award_id: Union[Unset, int] = UNSET
    award_name: Union[Unset, str] = UNSET
    id: Union[Unset, int] = UNSET
    name: Union[Unset, str] = UNSET
    external_id: Union[Unset, str] = UNSET
    source: Union[Unset, AuLeaveAllowanceTemplateModelExternalService] = UNSET
    leave_year_start: Union[Unset, datetime.datetime] = UNSET
    leave_accrual_start_date_type: Union[Unset, AuLeaveAllowanceTemplateModelNullableLeaveAccrualStartDateType] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        leave_loading_calculated_from_pay_category_id = self.leave_loading_calculated_from_pay_category_id

        leave_categories: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.leave_categories, Unset):
            leave_categories = []
            for leave_categories_item_data in self.leave_categories:
                leave_categories_item = leave_categories_item_data.to_dict()
                leave_categories.append(leave_categories_item)

        award_id = self.award_id

        award_name = self.award_name

        id = self.id

        name = self.name

        external_id = self.external_id

        source: Union[Unset, str] = UNSET
        if not isinstance(self.source, Unset):
            source = self.source.value

        leave_year_start: Union[Unset, str] = UNSET
        if not isinstance(self.leave_year_start, Unset):
            leave_year_start = self.leave_year_start.isoformat()

        leave_accrual_start_date_type: Union[Unset, str] = UNSET
        if not isinstance(self.leave_accrual_start_date_type, Unset):
            leave_accrual_start_date_type = self.leave_accrual_start_date_type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if leave_loading_calculated_from_pay_category_id is not UNSET:
            field_dict["leaveLoadingCalculatedFromPayCategoryId"] = leave_loading_calculated_from_pay_category_id
        if leave_categories is not UNSET:
            field_dict["leaveCategories"] = leave_categories
        if award_id is not UNSET:
            field_dict["awardId"] = award_id
        if award_name is not UNSET:
            field_dict["awardName"] = award_name
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if source is not UNSET:
            field_dict["source"] = source
        if leave_year_start is not UNSET:
            field_dict["leaveYearStart"] = leave_year_start
        if leave_accrual_start_date_type is not UNSET:
            field_dict["leaveAccrualStartDateType"] = leave_accrual_start_date_type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.au_leave_allowance_template_leave_category_api_model import (
            AuLeaveAllowanceTemplateLeaveCategoryApiModel,
        )

        d = src_dict.copy()
        leave_loading_calculated_from_pay_category_id = d.pop("leaveLoadingCalculatedFromPayCategoryId", UNSET)

        leave_categories = []
        _leave_categories = d.pop("leaveCategories", UNSET)
        for leave_categories_item_data in _leave_categories or []:
            leave_categories_item = AuLeaveAllowanceTemplateLeaveCategoryApiModel.from_dict(leave_categories_item_data)

            leave_categories.append(leave_categories_item)

        award_id = d.pop("awardId", UNSET)

        award_name = d.pop("awardName", UNSET)

        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        external_id = d.pop("externalId", UNSET)

        _source = d.pop("source", UNSET)
        source: Union[Unset, AuLeaveAllowanceTemplateModelExternalService]
        if isinstance(_source, Unset):
            source = UNSET
        else:
            source = AuLeaveAllowanceTemplateModelExternalService(_source)

        _leave_year_start = d.pop("leaveYearStart", UNSET)
        leave_year_start: Union[Unset, datetime.datetime]
        if isinstance(_leave_year_start, Unset):
            leave_year_start = UNSET
        else:
            leave_year_start = isoparse(_leave_year_start)

        _leave_accrual_start_date_type = d.pop("leaveAccrualStartDateType", UNSET)
        leave_accrual_start_date_type: Union[Unset, AuLeaveAllowanceTemplateModelNullableLeaveAccrualStartDateType]
        if isinstance(_leave_accrual_start_date_type, Unset):
            leave_accrual_start_date_type = UNSET
        else:
            leave_accrual_start_date_type = AuLeaveAllowanceTemplateModelNullableLeaveAccrualStartDateType(
                _leave_accrual_start_date_type
            )

        au_leave_allowance_template_model = cls(
            leave_loading_calculated_from_pay_category_id=leave_loading_calculated_from_pay_category_id,
            leave_categories=leave_categories,
            award_id=award_id,
            award_name=award_name,
            id=id,
            name=name,
            external_id=external_id,
            source=source,
            leave_year_start=leave_year_start,
            leave_accrual_start_date_type=leave_accrual_start_date_type,
        )

        au_leave_allowance_template_model.additional_properties = d
        return au_leave_allowance_template_model

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
