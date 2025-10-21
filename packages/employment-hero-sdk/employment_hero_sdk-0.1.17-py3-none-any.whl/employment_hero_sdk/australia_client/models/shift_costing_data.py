from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.shift_allowance_model import ShiftAllowanceModel
    from ..models.shift_liability_model import ShiftLiabilityModel
    from ..models.shift_part_model import ShiftPartModel


T = TypeVar("T", bound="ShiftCostingData")


@_attrs_define
class ShiftCostingData:
    """
    Attributes:
        shift_parts (Union[Unset, List['ShiftPartModel']]):
        allowances (Union[Unset, List['ShiftAllowanceModel']]):
        liabilities (Union[Unset, List['ShiftLiabilityModel']]):
        is_consolidated (Union[Unset, bool]):
    """

    shift_parts: Union[Unset, List["ShiftPartModel"]] = UNSET
    allowances: Union[Unset, List["ShiftAllowanceModel"]] = UNSET
    liabilities: Union[Unset, List["ShiftLiabilityModel"]] = UNSET
    is_consolidated: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        shift_parts: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.shift_parts, Unset):
            shift_parts = []
            for shift_parts_item_data in self.shift_parts:
                shift_parts_item = shift_parts_item_data.to_dict()
                shift_parts.append(shift_parts_item)

        allowances: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.allowances, Unset):
            allowances = []
            for allowances_item_data in self.allowances:
                allowances_item = allowances_item_data.to_dict()
                allowances.append(allowances_item)

        liabilities: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.liabilities, Unset):
            liabilities = []
            for liabilities_item_data in self.liabilities:
                liabilities_item = liabilities_item_data.to_dict()
                liabilities.append(liabilities_item)

        is_consolidated = self.is_consolidated

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if shift_parts is not UNSET:
            field_dict["shiftParts"] = shift_parts
        if allowances is not UNSET:
            field_dict["allowances"] = allowances
        if liabilities is not UNSET:
            field_dict["liabilities"] = liabilities
        if is_consolidated is not UNSET:
            field_dict["isConsolidated"] = is_consolidated

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.shift_allowance_model import ShiftAllowanceModel
        from ..models.shift_liability_model import ShiftLiabilityModel
        from ..models.shift_part_model import ShiftPartModel

        d = src_dict.copy()
        shift_parts = []
        _shift_parts = d.pop("shiftParts", UNSET)
        for shift_parts_item_data in _shift_parts or []:
            shift_parts_item = ShiftPartModel.from_dict(shift_parts_item_data)

            shift_parts.append(shift_parts_item)

        allowances = []
        _allowances = d.pop("allowances", UNSET)
        for allowances_item_data in _allowances or []:
            allowances_item = ShiftAllowanceModel.from_dict(allowances_item_data)

            allowances.append(allowances_item)

        liabilities = []
        _liabilities = d.pop("liabilities", UNSET)
        for liabilities_item_data in _liabilities or []:
            liabilities_item = ShiftLiabilityModel.from_dict(liabilities_item_data)

            liabilities.append(liabilities_item)

        is_consolidated = d.pop("isConsolidated", UNSET)

        shift_costing_data = cls(
            shift_parts=shift_parts,
            allowances=allowances,
            liabilities=liabilities,
            is_consolidated=is_consolidated,
        )

        shift_costing_data.additional_properties = d
        return shift_costing_data

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
