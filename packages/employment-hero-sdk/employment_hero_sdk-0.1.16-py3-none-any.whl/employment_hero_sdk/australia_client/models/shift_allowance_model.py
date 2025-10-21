from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.shift_allowance_model_shift_allowance_option import ShiftAllowanceModelShiftAllowanceOption
from ..models.shift_allowance_model_shift_allowance_type import ShiftAllowanceModelShiftAllowanceType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.nominal_classification import NominalClassification


T = TypeVar("T", bound="ShiftAllowanceModel")


@_attrs_define
class ShiftAllowanceModel:
    """
    Attributes:
        pay_category (Union[Unset, str]):
        pay_category_id (Union[Unset, int]):
        units (Union[Unset, float]):
        cost (Union[Unset, float]):
        rate_multiplier (Union[Unset, float]):
        option (Union[Unset, ShiftAllowanceModelShiftAllowanceOption]):
        type (Union[Unset, ShiftAllowanceModelShiftAllowanceType]):
        classification (Union[Unset, NominalClassification]):
    """

    pay_category: Union[Unset, str] = UNSET
    pay_category_id: Union[Unset, int] = UNSET
    units: Union[Unset, float] = UNSET
    cost: Union[Unset, float] = UNSET
    rate_multiplier: Union[Unset, float] = UNSET
    option: Union[Unset, ShiftAllowanceModelShiftAllowanceOption] = UNSET
    type: Union[Unset, ShiftAllowanceModelShiftAllowanceType] = UNSET
    classification: Union[Unset, "NominalClassification"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        pay_category = self.pay_category

        pay_category_id = self.pay_category_id

        units = self.units

        cost = self.cost

        rate_multiplier = self.rate_multiplier

        option: Union[Unset, str] = UNSET
        if not isinstance(self.option, Unset):
            option = self.option.value

        type: Union[Unset, str] = UNSET
        if not isinstance(self.type, Unset):
            type = self.type.value

        classification: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.classification, Unset):
            classification = self.classification.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if pay_category is not UNSET:
            field_dict["payCategory"] = pay_category
        if pay_category_id is not UNSET:
            field_dict["payCategoryId"] = pay_category_id
        if units is not UNSET:
            field_dict["units"] = units
        if cost is not UNSET:
            field_dict["cost"] = cost
        if rate_multiplier is not UNSET:
            field_dict["rateMultiplier"] = rate_multiplier
        if option is not UNSET:
            field_dict["option"] = option
        if type is not UNSET:
            field_dict["type"] = type
        if classification is not UNSET:
            field_dict["classification"] = classification

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.nominal_classification import NominalClassification

        d = src_dict.copy()
        pay_category = d.pop("payCategory", UNSET)

        pay_category_id = d.pop("payCategoryId", UNSET)

        units = d.pop("units", UNSET)

        cost = d.pop("cost", UNSET)

        rate_multiplier = d.pop("rateMultiplier", UNSET)

        _option = d.pop("option", UNSET)
        option: Union[Unset, ShiftAllowanceModelShiftAllowanceOption]
        if isinstance(_option, Unset):
            option = UNSET
        else:
            option = ShiftAllowanceModelShiftAllowanceOption(_option)

        _type = d.pop("type", UNSET)
        type: Union[Unset, ShiftAllowanceModelShiftAllowanceType]
        if isinstance(_type, Unset):
            type = UNSET
        else:
            type = ShiftAllowanceModelShiftAllowanceType(_type)

        _classification = d.pop("classification", UNSET)
        classification: Union[Unset, NominalClassification]
        if isinstance(_classification, Unset):
            classification = UNSET
        else:
            classification = NominalClassification.from_dict(_classification)

        shift_allowance_model = cls(
            pay_category=pay_category,
            pay_category_id=pay_category_id,
            units=units,
            cost=cost,
            rate_multiplier=rate_multiplier,
            option=option,
            type=type,
            classification=classification,
        )

        shift_allowance_model.additional_properties = d
        return shift_allowance_model

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
