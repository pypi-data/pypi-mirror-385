from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.shift_costings_request_model_id_type import ShiftCostingsRequestModelIdType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.rate_override import RateOverride
    from ..models.shift_costings_employee_model import ShiftCostingsEmployeeModel
    from ..models.shift_costings_request_shift_model import ShiftCostingsRequestShiftModel


T = TypeVar("T", bound="ShiftCostingsRequestModel")


@_attrs_define
class ShiftCostingsRequestModel:
    """
    Attributes:
        transaction_external_id (Union[Unset, str]):
        location_id_type (Union[Unset, ShiftCostingsRequestModelIdType]):
        work_type_id_type (Union[Unset, ShiftCostingsRequestModelIdType]):
        include_evaluation_results (Union[Unset, bool]):
        employee (Union[Unset, ShiftCostingsEmployeeModel]):
        shifts (Union[Unset, List['ShiftCostingsRequestShiftModel']]):
        override_rates (Union[Unset, List['RateOverride']]):
    """

    transaction_external_id: Union[Unset, str] = UNSET
    location_id_type: Union[Unset, ShiftCostingsRequestModelIdType] = UNSET
    work_type_id_type: Union[Unset, ShiftCostingsRequestModelIdType] = UNSET
    include_evaluation_results: Union[Unset, bool] = UNSET
    employee: Union[Unset, "ShiftCostingsEmployeeModel"] = UNSET
    shifts: Union[Unset, List["ShiftCostingsRequestShiftModel"]] = UNSET
    override_rates: Union[Unset, List["RateOverride"]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        transaction_external_id = self.transaction_external_id

        location_id_type: Union[Unset, str] = UNSET
        if not isinstance(self.location_id_type, Unset):
            location_id_type = self.location_id_type.value

        work_type_id_type: Union[Unset, str] = UNSET
        if not isinstance(self.work_type_id_type, Unset):
            work_type_id_type = self.work_type_id_type.value

        include_evaluation_results = self.include_evaluation_results

        employee: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.employee, Unset):
            employee = self.employee.to_dict()

        shifts: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.shifts, Unset):
            shifts = []
            for shifts_item_data in self.shifts:
                shifts_item = shifts_item_data.to_dict()
                shifts.append(shifts_item)

        override_rates: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.override_rates, Unset):
            override_rates = []
            for override_rates_item_data in self.override_rates:
                override_rates_item = override_rates_item_data.to_dict()
                override_rates.append(override_rates_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if transaction_external_id is not UNSET:
            field_dict["transactionExternalId"] = transaction_external_id
        if location_id_type is not UNSET:
            field_dict["locationIdType"] = location_id_type
        if work_type_id_type is not UNSET:
            field_dict["workTypeIdType"] = work_type_id_type
        if include_evaluation_results is not UNSET:
            field_dict["includeEvaluationResults"] = include_evaluation_results
        if employee is not UNSET:
            field_dict["employee"] = employee
        if shifts is not UNSET:
            field_dict["shifts"] = shifts
        if override_rates is not UNSET:
            field_dict["overrideRates"] = override_rates

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.rate_override import RateOverride
        from ..models.shift_costings_employee_model import ShiftCostingsEmployeeModel
        from ..models.shift_costings_request_shift_model import ShiftCostingsRequestShiftModel

        d = src_dict.copy()
        transaction_external_id = d.pop("transactionExternalId", UNSET)

        _location_id_type = d.pop("locationIdType", UNSET)
        location_id_type: Union[Unset, ShiftCostingsRequestModelIdType]
        if isinstance(_location_id_type, Unset):
            location_id_type = UNSET
        else:
            location_id_type = ShiftCostingsRequestModelIdType(_location_id_type)

        _work_type_id_type = d.pop("workTypeIdType", UNSET)
        work_type_id_type: Union[Unset, ShiftCostingsRequestModelIdType]
        if isinstance(_work_type_id_type, Unset):
            work_type_id_type = UNSET
        else:
            work_type_id_type = ShiftCostingsRequestModelIdType(_work_type_id_type)

        include_evaluation_results = d.pop("includeEvaluationResults", UNSET)

        _employee = d.pop("employee", UNSET)
        employee: Union[Unset, ShiftCostingsEmployeeModel]
        if isinstance(_employee, Unset):
            employee = UNSET
        else:
            employee = ShiftCostingsEmployeeModel.from_dict(_employee)

        shifts = []
        _shifts = d.pop("shifts", UNSET)
        for shifts_item_data in _shifts or []:
            shifts_item = ShiftCostingsRequestShiftModel.from_dict(shifts_item_data)

            shifts.append(shifts_item)

        override_rates = []
        _override_rates = d.pop("overrideRates", UNSET)
        for override_rates_item_data in _override_rates or []:
            override_rates_item = RateOverride.from_dict(override_rates_item_data)

            override_rates.append(override_rates_item)

        shift_costings_request_model = cls(
            transaction_external_id=transaction_external_id,
            location_id_type=location_id_type,
            work_type_id_type=work_type_id_type,
            include_evaluation_results=include_evaluation_results,
            employee=employee,
            shifts=shifts,
            override_rates=override_rates,
        )

        shift_costings_request_model.additional_properties = d
        return shift_costings_request_model

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
