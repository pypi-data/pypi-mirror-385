import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.leave_allowance_template_model_external_service import LeaveAllowanceTemplateModelExternalService
from ..models.leave_allowance_template_model_nullable_leave_accrual_start_date_type import (
    LeaveAllowanceTemplateModelNullableLeaveAccrualStartDateType,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.leave_allowance_template_leave_category_model import LeaveAllowanceTemplateLeaveCategoryModel


T = TypeVar("T", bound="LeaveAllowanceTemplateModel")


@_attrs_define
class LeaveAllowanceTemplateModel:
    """
    Attributes:
        id (Union[Unset, int]):
        name (Union[Unset, str]):
        leave_categories (Union[Unset, List['LeaveAllowanceTemplateLeaveCategoryModel']]):
        external_id (Union[Unset, str]):
        source (Union[Unset, LeaveAllowanceTemplateModelExternalService]):
        leave_loading_calculated_from_pay_category_id (Union[Unset, int]):
        leave_accrual_start_date_type (Union[Unset, LeaveAllowanceTemplateModelNullableLeaveAccrualStartDateType]):
        leave_year_start (Union[Unset, datetime.datetime]):
    """

    id: Union[Unset, int] = UNSET
    name: Union[Unset, str] = UNSET
    leave_categories: Union[Unset, List["LeaveAllowanceTemplateLeaveCategoryModel"]] = UNSET
    external_id: Union[Unset, str] = UNSET
    source: Union[Unset, LeaveAllowanceTemplateModelExternalService] = UNSET
    leave_loading_calculated_from_pay_category_id: Union[Unset, int] = UNSET
    leave_accrual_start_date_type: Union[Unset, LeaveAllowanceTemplateModelNullableLeaveAccrualStartDateType] = UNSET
    leave_year_start: Union[Unset, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        name = self.name

        leave_categories: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.leave_categories, Unset):
            leave_categories = []
            for leave_categories_item_data in self.leave_categories:
                leave_categories_item = leave_categories_item_data.to_dict()
                leave_categories.append(leave_categories_item)

        external_id = self.external_id

        source: Union[Unset, str] = UNSET
        if not isinstance(self.source, Unset):
            source = self.source.value

        leave_loading_calculated_from_pay_category_id = self.leave_loading_calculated_from_pay_category_id

        leave_accrual_start_date_type: Union[Unset, str] = UNSET
        if not isinstance(self.leave_accrual_start_date_type, Unset):
            leave_accrual_start_date_type = self.leave_accrual_start_date_type.value

        leave_year_start: Union[Unset, str] = UNSET
        if not isinstance(self.leave_year_start, Unset):
            leave_year_start = self.leave_year_start.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if leave_categories is not UNSET:
            field_dict["leaveCategories"] = leave_categories
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if source is not UNSET:
            field_dict["source"] = source
        if leave_loading_calculated_from_pay_category_id is not UNSET:
            field_dict["leaveLoadingCalculatedFromPayCategoryId"] = leave_loading_calculated_from_pay_category_id
        if leave_accrual_start_date_type is not UNSET:
            field_dict["leaveAccrualStartDateType"] = leave_accrual_start_date_type
        if leave_year_start is not UNSET:
            field_dict["leaveYearStart"] = leave_year_start

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.leave_allowance_template_leave_category_model import LeaveAllowanceTemplateLeaveCategoryModel

        d = src_dict.copy()
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        leave_categories = []
        _leave_categories = d.pop("leaveCategories", UNSET)
        for leave_categories_item_data in _leave_categories or []:
            leave_categories_item = LeaveAllowanceTemplateLeaveCategoryModel.from_dict(leave_categories_item_data)

            leave_categories.append(leave_categories_item)

        external_id = d.pop("externalId", UNSET)

        _source = d.pop("source", UNSET)
        source: Union[Unset, LeaveAllowanceTemplateModelExternalService]
        if isinstance(_source, Unset):
            source = UNSET
        else:
            source = LeaveAllowanceTemplateModelExternalService(_source)

        leave_loading_calculated_from_pay_category_id = d.pop("leaveLoadingCalculatedFromPayCategoryId", UNSET)

        _leave_accrual_start_date_type = d.pop("leaveAccrualStartDateType", UNSET)
        leave_accrual_start_date_type: Union[Unset, LeaveAllowanceTemplateModelNullableLeaveAccrualStartDateType]
        if isinstance(_leave_accrual_start_date_type, Unset):
            leave_accrual_start_date_type = UNSET
        else:
            leave_accrual_start_date_type = LeaveAllowanceTemplateModelNullableLeaveAccrualStartDateType(
                _leave_accrual_start_date_type
            )

        _leave_year_start = d.pop("leaveYearStart", UNSET)
        leave_year_start: Union[Unset, datetime.datetime]
        if isinstance(_leave_year_start, Unset):
            leave_year_start = UNSET
        else:
            leave_year_start = isoparse(_leave_year_start)

        leave_allowance_template_model = cls(
            id=id,
            name=name,
            leave_categories=leave_categories,
            external_id=external_id,
            source=source,
            leave_loading_calculated_from_pay_category_id=leave_loading_calculated_from_pay_category_id,
            leave_accrual_start_date_type=leave_accrual_start_date_type,
            leave_year_start=leave_year_start,
        )

        leave_allowance_template_model.additional_properties = d
        return leave_allowance_template_model

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
