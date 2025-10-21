from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.au_billing_plan_response_model_function_toggle import AuBillingPlanResponseModelFunctionToggle
from ..models.au_billing_plan_response_model_pricing_model_type_enum import (
    AuBillingPlanResponseModelPricingModelTypeEnum,
)
from ..models.au_billing_plan_response_model_super_inclusion_type_enum import (
    AuBillingPlanResponseModelSuperInclusionTypeEnum,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="AuBillingPlanResponseModel")


@_attrs_define
class AuBillingPlanResponseModel:
    """
    Attributes:
        super_inclusion (Union[Unset, AuBillingPlanResponseModelSuperInclusionTypeEnum]):
        function_pay_conditions (Union[Unset, AuBillingPlanResponseModelFunctionToggle]):
        function_awards (Union[Unset, AuBillingPlanResponseModelFunctionToggle]):
        id (Union[Unset, int]):
        name (Union[Unset, str]):
        type (Union[Unset, AuBillingPlanResponseModelPricingModelTypeEnum]):
        price_per_unit (Union[Unset, float]):
        price_per_sms (Union[Unset, float]):
        included_employees (Union[Unset, int]):
        function_rostering (Union[Unset, AuBillingPlanResponseModelFunctionToggle]):
        function_time_and_attendance (Union[Unset, AuBillingPlanResponseModelFunctionToggle]):
        function_employee_onboarding (Union[Unset, AuBillingPlanResponseModelFunctionToggle]):
        description (Union[Unset, str]):
        is_hidden (Union[Unset, bool]):
    """

    super_inclusion: Union[Unset, AuBillingPlanResponseModelSuperInclusionTypeEnum] = UNSET
    function_pay_conditions: Union[Unset, AuBillingPlanResponseModelFunctionToggle] = UNSET
    function_awards: Union[Unset, AuBillingPlanResponseModelFunctionToggle] = UNSET
    id: Union[Unset, int] = UNSET
    name: Union[Unset, str] = UNSET
    type: Union[Unset, AuBillingPlanResponseModelPricingModelTypeEnum] = UNSET
    price_per_unit: Union[Unset, float] = UNSET
    price_per_sms: Union[Unset, float] = UNSET
    included_employees: Union[Unset, int] = UNSET
    function_rostering: Union[Unset, AuBillingPlanResponseModelFunctionToggle] = UNSET
    function_time_and_attendance: Union[Unset, AuBillingPlanResponseModelFunctionToggle] = UNSET
    function_employee_onboarding: Union[Unset, AuBillingPlanResponseModelFunctionToggle] = UNSET
    description: Union[Unset, str] = UNSET
    is_hidden: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        super_inclusion: Union[Unset, str] = UNSET
        if not isinstance(self.super_inclusion, Unset):
            super_inclusion = self.super_inclusion.value

        function_pay_conditions: Union[Unset, str] = UNSET
        if not isinstance(self.function_pay_conditions, Unset):
            function_pay_conditions = self.function_pay_conditions.value

        function_awards: Union[Unset, str] = UNSET
        if not isinstance(self.function_awards, Unset):
            function_awards = self.function_awards.value

        id = self.id

        name = self.name

        type: Union[Unset, str] = UNSET
        if not isinstance(self.type, Unset):
            type = self.type.value

        price_per_unit = self.price_per_unit

        price_per_sms = self.price_per_sms

        included_employees = self.included_employees

        function_rostering: Union[Unset, str] = UNSET
        if not isinstance(self.function_rostering, Unset):
            function_rostering = self.function_rostering.value

        function_time_and_attendance: Union[Unset, str] = UNSET
        if not isinstance(self.function_time_and_attendance, Unset):
            function_time_and_attendance = self.function_time_and_attendance.value

        function_employee_onboarding: Union[Unset, str] = UNSET
        if not isinstance(self.function_employee_onboarding, Unset):
            function_employee_onboarding = self.function_employee_onboarding.value

        description = self.description

        is_hidden = self.is_hidden

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if super_inclusion is not UNSET:
            field_dict["superInclusion"] = super_inclusion
        if function_pay_conditions is not UNSET:
            field_dict["functionPayConditions"] = function_pay_conditions
        if function_awards is not UNSET:
            field_dict["functionAwards"] = function_awards
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if type is not UNSET:
            field_dict["type"] = type
        if price_per_unit is not UNSET:
            field_dict["pricePerUnit"] = price_per_unit
        if price_per_sms is not UNSET:
            field_dict["pricePerSms"] = price_per_sms
        if included_employees is not UNSET:
            field_dict["includedEmployees"] = included_employees
        if function_rostering is not UNSET:
            field_dict["functionRostering"] = function_rostering
        if function_time_and_attendance is not UNSET:
            field_dict["functionTimeAndAttendance"] = function_time_and_attendance
        if function_employee_onboarding is not UNSET:
            field_dict["functionEmployeeOnboarding"] = function_employee_onboarding
        if description is not UNSET:
            field_dict["description"] = description
        if is_hidden is not UNSET:
            field_dict["isHidden"] = is_hidden

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _super_inclusion = d.pop("superInclusion", UNSET)
        super_inclusion: Union[Unset, AuBillingPlanResponseModelSuperInclusionTypeEnum]
        if isinstance(_super_inclusion, Unset):
            super_inclusion = UNSET
        else:
            super_inclusion = AuBillingPlanResponseModelSuperInclusionTypeEnum(_super_inclusion)

        _function_pay_conditions = d.pop("functionPayConditions", UNSET)
        function_pay_conditions: Union[Unset, AuBillingPlanResponseModelFunctionToggle]
        if isinstance(_function_pay_conditions, Unset):
            function_pay_conditions = UNSET
        else:
            function_pay_conditions = AuBillingPlanResponseModelFunctionToggle(_function_pay_conditions)

        _function_awards = d.pop("functionAwards", UNSET)
        function_awards: Union[Unset, AuBillingPlanResponseModelFunctionToggle]
        if isinstance(_function_awards, Unset):
            function_awards = UNSET
        else:
            function_awards = AuBillingPlanResponseModelFunctionToggle(_function_awards)

        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        _type = d.pop("type", UNSET)
        type: Union[Unset, AuBillingPlanResponseModelPricingModelTypeEnum]
        if isinstance(_type, Unset):
            type = UNSET
        else:
            type = AuBillingPlanResponseModelPricingModelTypeEnum(_type)

        price_per_unit = d.pop("pricePerUnit", UNSET)

        price_per_sms = d.pop("pricePerSms", UNSET)

        included_employees = d.pop("includedEmployees", UNSET)

        _function_rostering = d.pop("functionRostering", UNSET)
        function_rostering: Union[Unset, AuBillingPlanResponseModelFunctionToggle]
        if isinstance(_function_rostering, Unset):
            function_rostering = UNSET
        else:
            function_rostering = AuBillingPlanResponseModelFunctionToggle(_function_rostering)

        _function_time_and_attendance = d.pop("functionTimeAndAttendance", UNSET)
        function_time_and_attendance: Union[Unset, AuBillingPlanResponseModelFunctionToggle]
        if isinstance(_function_time_and_attendance, Unset):
            function_time_and_attendance = UNSET
        else:
            function_time_and_attendance = AuBillingPlanResponseModelFunctionToggle(_function_time_and_attendance)

        _function_employee_onboarding = d.pop("functionEmployeeOnboarding", UNSET)
        function_employee_onboarding: Union[Unset, AuBillingPlanResponseModelFunctionToggle]
        if isinstance(_function_employee_onboarding, Unset):
            function_employee_onboarding = UNSET
        else:
            function_employee_onboarding = AuBillingPlanResponseModelFunctionToggle(_function_employee_onboarding)

        description = d.pop("description", UNSET)

        is_hidden = d.pop("isHidden", UNSET)

        au_billing_plan_response_model = cls(
            super_inclusion=super_inclusion,
            function_pay_conditions=function_pay_conditions,
            function_awards=function_awards,
            id=id,
            name=name,
            type=type,
            price_per_unit=price_per_unit,
            price_per_sms=price_per_sms,
            included_employees=included_employees,
            function_rostering=function_rostering,
            function_time_and_attendance=function_time_and_attendance,
            function_employee_onboarding=function_employee_onboarding,
            description=description,
            is_hidden=is_hidden,
        )

        au_billing_plan_response_model.additional_properties = d
        return au_billing_plan_response_model

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
