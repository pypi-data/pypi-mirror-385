from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.leave_history_report_group_model_leave_unit_type_enum import LeaveHistoryReportGroupModelLeaveUnitTypeEnum
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.leave_history_report_detail_model import LeaveHistoryReportDetailModel


T = TypeVar("T", bound="LeaveHistoryReportGroupModel")


@_attrs_define
class LeaveHistoryReportGroupModel:
    """
    Attributes:
        employee_id (Union[Unset, int]):
        employee_external_id (Union[Unset, str]):
        first_name (Union[Unset, str]):
        surname (Union[Unset, str]):
        leave_category_type (Union[Unset, str]):
        opening_balance (Union[Unset, float]):
        closing_balance (Union[Unset, float]):
        leave_history_details (Union[Unset, List['LeaveHistoryReportDetailModel']]):
        unit_type (Union[Unset, LeaveHistoryReportGroupModelLeaveUnitTypeEnum]):
    """

    employee_id: Union[Unset, int] = UNSET
    employee_external_id: Union[Unset, str] = UNSET
    first_name: Union[Unset, str] = UNSET
    surname: Union[Unset, str] = UNSET
    leave_category_type: Union[Unset, str] = UNSET
    opening_balance: Union[Unset, float] = UNSET
    closing_balance: Union[Unset, float] = UNSET
    leave_history_details: Union[Unset, List["LeaveHistoryReportDetailModel"]] = UNSET
    unit_type: Union[Unset, LeaveHistoryReportGroupModelLeaveUnitTypeEnum] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        employee_id = self.employee_id

        employee_external_id = self.employee_external_id

        first_name = self.first_name

        surname = self.surname

        leave_category_type = self.leave_category_type

        opening_balance = self.opening_balance

        closing_balance = self.closing_balance

        leave_history_details: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.leave_history_details, Unset):
            leave_history_details = []
            for leave_history_details_item_data in self.leave_history_details:
                leave_history_details_item = leave_history_details_item_data.to_dict()
                leave_history_details.append(leave_history_details_item)

        unit_type: Union[Unset, str] = UNSET
        if not isinstance(self.unit_type, Unset):
            unit_type = self.unit_type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if employee_external_id is not UNSET:
            field_dict["employeeExternalId"] = employee_external_id
        if first_name is not UNSET:
            field_dict["firstName"] = first_name
        if surname is not UNSET:
            field_dict["surname"] = surname
        if leave_category_type is not UNSET:
            field_dict["leaveCategoryType"] = leave_category_type
        if opening_balance is not UNSET:
            field_dict["openingBalance"] = opening_balance
        if closing_balance is not UNSET:
            field_dict["closingBalance"] = closing_balance
        if leave_history_details is not UNSET:
            field_dict["leaveHistoryDetails"] = leave_history_details
        if unit_type is not UNSET:
            field_dict["unitType"] = unit_type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.leave_history_report_detail_model import LeaveHistoryReportDetailModel

        d = src_dict.copy()
        employee_id = d.pop("employeeId", UNSET)

        employee_external_id = d.pop("employeeExternalId", UNSET)

        first_name = d.pop("firstName", UNSET)

        surname = d.pop("surname", UNSET)

        leave_category_type = d.pop("leaveCategoryType", UNSET)

        opening_balance = d.pop("openingBalance", UNSET)

        closing_balance = d.pop("closingBalance", UNSET)

        leave_history_details = []
        _leave_history_details = d.pop("leaveHistoryDetails", UNSET)
        for leave_history_details_item_data in _leave_history_details or []:
            leave_history_details_item = LeaveHistoryReportDetailModel.from_dict(leave_history_details_item_data)

            leave_history_details.append(leave_history_details_item)

        _unit_type = d.pop("unitType", UNSET)
        unit_type: Union[Unset, LeaveHistoryReportGroupModelLeaveUnitTypeEnum]
        if isinstance(_unit_type, Unset):
            unit_type = UNSET
        else:
            unit_type = LeaveHistoryReportGroupModelLeaveUnitTypeEnum(_unit_type)

        leave_history_report_group_model = cls(
            employee_id=employee_id,
            employee_external_id=employee_external_id,
            first_name=first_name,
            surname=surname,
            leave_category_type=leave_category_type,
            opening_balance=opening_balance,
            closing_balance=closing_balance,
            leave_history_details=leave_history_details,
            unit_type=unit_type,
        )

        leave_history_report_group_model.additional_properties = d
        return leave_history_report_group_model

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
